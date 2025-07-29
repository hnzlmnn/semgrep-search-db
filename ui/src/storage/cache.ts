import {Database, type WritableDatabase} from "./database";
import type {Repository} from "../models/repository";
import type {Rule, RuleRow} from "../models/rule";
import {calcStats, type RepositoryStats} from "../util/statistics";
import {readonly, writable, type Writable} from "svelte/store";
import {loading} from "./uistate";
import {
    type Collection,
    type CollectionType, type DynamicCollection,
    isDynamicCollection, isLoadedCollection,
    isStaticCollection,
    type LoadedCollection
} from "../models/collection";
import type {Metadata} from "../models/metadata";

export interface UniqueValues {
    readonly sources: string[]
    readonly categories: Array<string | null>
    readonly severities: Array<string | null>
    readonly languages: string[]
}

export interface RepositoryWithStats extends Repository {
    stats: RepositoryStats
}


export class ViewData {
    public static readonly RULE_ID_JOINER = "$$"

    constructor(
        public readonly meta: Metadata,
        public readonly repos: Map<string, RepositoryWithStats>,
        public readonly rules: Map<string, Map<string, RuleRow>>,
        public readonly ruleRows: RuleRow[],
        public readonly uniques: UniqueValues,
        public readonly collections: LoadedCollection<any>[],
    ) {
    }

    public static filterRulesForCollection(collection: DynamicCollection, rows: RuleRow[]) {
        // TODO: Add includeCategoryNull to dynamic rules
        return rows.filter(rule => {
            const matchSource = collection.sources.length === 0 || collection.sources.includes(rule.source)
            const matchCategory = collection.categories.length === 0 || collection.categories.find(category => rule.category === category) !== undefined
            const matchLanguage = collection.languages.length === 0 || collection.languages.find(language => rule.languages.includes(language)) !== undefined
            const matchSeverity = collection.severities.length === 0 || collection.severities.find(severity => rule.severity === severity) !== undefined
            const matchKeywords = collection.keywords.length === 0 || rule.id.includes(collection.keywords)

            return matchSource && matchCategory && matchLanguage && matchSeverity && matchKeywords
        })
    }

    public static loadCollection<T extends CollectionType>(collection: Collection<T>, rows: RuleRow[], rules: Map<string, Map<string, RuleRow>>): LoadedCollection<T> {
        let resolvedRules: RuleRow[] = []
        if (isDynamicCollection(collection)) {
            resolvedRules = ViewData.filterRulesForCollection(collection, rows)
        } else if (isStaticCollection(collection)) {
            resolvedRules = collection.rules.map(({source, id}) => {
                return rules.get(source)?.get(id)
            }).filter(collection => collection !== undefined)
        }

        return {...collection, resolvedRules}
    }

    public static fromDb(meta: Metadata, dbRepos: Repository[], dbRules: Rule[], collections: Collection<any>[]): ViewData {
        const repos = new Map<string, RepositoryWithStats>();
        const repoStats = calcStats(dbRules)

        dbRepos.forEach(repo => repos.set(repo.id, {
            ...repo,
            stats: repoStats.get(repo.id) ?? {numRules: 0, languages: new Map<string, number>()}
        }))

        const uniqueSources = new Set<string>()
        const uniqueCategories = new Set<string | null>()
        const uniqueSeverities = new Set<string | null>()
        const uniqueLanguages = new Set<string>()

        const rows: RuleRow[] = dbRules.map(rule => {
            const repo = repos.get(rule.source)
            if (repo === undefined) {
                console.warn("Found rule without repository")
                return null
            }

            uniqueSources.add(rule.source)
            uniqueCategories.add(rule.category)
            uniqueSeverities.add(rule.severity)
            rule.languages.forEach(lang => uniqueLanguages.add(lang))

            return {...rule, rule_id: rule.id, id: `${rule.source}${this.RULE_ID_JOINER}${rule.id}`, repo}
        }).filter(row => row !== null)

        const ruleLookup = new Map<string, Map<string, RuleRow>>()
        for (const rule of rows) {
            if (!ruleLookup.has(rule.source)) {
                ruleLookup.set(rule.source, new Map())
            }
            ruleLookup.get(rule.source)?.set(rule.rule_id, rule)
        }

        const loadedCollections = collections.map(collection => this.loadCollection(collection, rows, ruleLookup))

        return new ViewData(meta, repos, ruleLookup, rows, {
            sources: [...uniqueSources],
            categories: [...uniqueCategories],
            severities: [...uniqueSeverities],
            languages: [...uniqueLanguages],
        }, loadedCollections)
    }

    public copy(): ViewDataBuilder {
        return new ViewDataBuilder(this)
    }

}

class ViewDataBuilder {
    private _meta: Metadata
    private _repos: Map<string, RepositoryWithStats>
    private _rules: Map<string, Map<string, RuleRow>>
    private _ruleRows: RuleRow[]
    private _uniques: UniqueValues
    private _collections: LoadedCollection<any>[]

    constructor(private readonly data: ViewData) {
        this._meta = data.meta
        this._repos = data.repos
        this._rules = data.rules
        this._ruleRows = data.ruleRows
        this._uniques = data.uniques
        this._collections = data.collections
    }

    public repos(repos: Map<string, RepositoryWithStats>): ViewDataBuilder {
        this._repos = repos
        return this
    }

    public rules(rules: Map<string, Map<string, RuleRow>>): ViewDataBuilder {
        this._rules = rules
        return this
    }

    public ruleRows(ruleRows: RuleRow[]): ViewDataBuilder {
        this._ruleRows = ruleRows
        return this
    }

    public uniques(uniques: UniqueValues): ViewDataBuilder {
        this._uniques = uniques
        return this
    }

    public collections(collections: Collection<any>[]): ViewDataBuilder {
        if (collections === undefined) {
            return this
        }
        if (this._ruleRows === undefined || this._rules === undefined) {
            this._collections = []
        } else {
            this._collections = collections.map(collection => ViewData.loadCollection(collection, this._ruleRows, this._rules))
        }
        return this
    }

    public loadedCollections(collections: LoadedCollection<any>[]): ViewDataBuilder {
        this._collections = collections
        return this
    }

    public build(): ViewData {
        return new ViewData(this._meta, this._repos, this._rules, this._ruleRows, this._uniques, this._collections)
    }
}

export class CachedDatabase implements WritableDatabase {
    private static _instance: CachedDatabase
    public ready = false
    private _viewData: Writable<ViewData | null> = writable(null)
    public readonly viewData = readonly(this._viewData)

    private constructor() {
        Database.instanceAsync().then(db => {
            loading.set(true)
            requestAnimationFrame(async () => {
                this._viewData.set(ViewData.fromDb(db.meta, await db.getRepositories(), await db.getRules(), await db.getCollections()))

                db.onChange('collections', (_, collections) => {
                    this._viewData.update(data => {
                        if (data === null) {
                            return null
                        }
                        return data.copy().collections(collections).build()
                    })
                })

                this.ready = true
                loading.set(false)
            })
        })
    }

    public static instance(): CachedDatabase {
        if (this._instance === undefined) {
            this._instance = new CachedDatabase();
        }
        return this._instance;
    }

    public async putCollection(collection: Collection<any>) {
        if (isLoadedCollection(collection)) {
            delete (collection as any)['resolvedRules']
        }
        return Database.instanceAsync().then(db => db.putCollection({...collection}))
    }

    public async deleteCollection(id: string) {
        return Database.instanceAsync().then(db => db.deleteCollection(id))
    }
}

;(window as any).CachedDatabase = CachedDatabase