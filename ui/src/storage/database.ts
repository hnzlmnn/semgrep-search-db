import {type DBSchema, type IDBPDatabase, openDB, type StoreNames, type StoreValue} from "idb";
import type {Repository} from "../models/repository";
import type {Metadata} from "../models/metadata";
import shippedData from '../assets/db.json'
import type {Rule} from "../models/rule";
import {parseDate} from "../util/date";
import {type Writable, type Readable, derived, writable} from "svelte/store";
import type {Collection, CollectionType} from "../models/collection";

interface SemgrepSearchDB extends DBSchema {
    meta: {
        key: string
        value: Metadata & {id: string}
    }
    repos: {
        key: string
        value: Repository
    }
    rules: {
        key: string
        value: Rule
        indexes: {
            source: string
            category: string
            severity: string
            languages: string[]
        }
    }
    collections: {
        key: string
        value: Collection<any>
        indexes: {
            type: CollectionType
        }
    }
}

interface SemgrepSearchJSON {
    meta: { [key: string]: Metadata }
    repos: { [key: string]: Repository }
    rules: { [key: string]: Rule }
}

export interface WritableDatabase {
    putCollection(collection: Collection<any>): Promise<string>;
}

export class Database implements WritableDatabase {
    private static readonly VERSION = 2
    private static _instance: Database
    private static readyListeners: Array<(db: Database) => void> = []
    private readonly onUpdate: Writable<StoreNames<SemgrepSearchDB> | StoreNames<SemgrepSearchDB>[]> = writable()
    private readonly changeListeners: { [Name in StoreNames<SemgrepSearchDB>]: Readable<StoreValue<SemgrepSearchDB, Name>[]> }
    private _metadata?: Metadata

    public static async create() {
        if (this._instance === undefined) {
            this._instance = new Database(await Database.open());
            this._instance._metadata = await this._instance.update()
            this.readyListeners.splice(0, this.readyListeners.length).forEach(resolve => resolve(this._instance));
            this._instance.onUpdate.set(["meta", "repos", "rules", "collections"])
        }
        return this._instance
    }

    public static instance(): Database {
        if (this._instance === undefined) {
            throw new Error("database is not initialized");
        }
        return this._instance;
    }

    public static async instanceAsync(): Promise<Database> {
        if (this._instance !== undefined) {
            return this._instance
        }
        return new Promise(resolve => {
            Database.readyListeners.push(resolve)
        })
    }

    public get meta(): Metadata {
        if (this._metadata === undefined) {
            throw new Error("database is not initialized");
        }
        return this._metadata
    }

    private constructor(private db: IDBPDatabase<SemgrepSearchDB>) {
        this.changeListeners = {} as any
        for (const name of db.objectStoreNames) {
            this.changeListeners[name] = derived(this.onUpdate, (topics, set) => {
                if (!Array.isArray(topics)) {
                    topics = [topics]
                }
                if (topics.includes(name)) {
                    this.db.getAll(name).then(values => set(values as any))
                }
            }) as any
        }
    }

    private static async open() {
        return openDB<SemgrepSearchDB>('semgrep-search', Database.VERSION, {
            upgrade(db: IDBPDatabase<SemgrepSearchDB>, oldVersion: number, newVersion: number) {
                console.log(oldVersion, newVersion)
                if (oldVersion === newVersion) {
                    return
                }
                switch (oldVersion) {
                    case 0:
                        console.log('Initializing database')
                    case 1:
                        console.log('Upgrading to DB version 1')
                        db.createObjectStore('meta', {
                            keyPath: 'id'
                        })

                        db.createObjectStore('repos', {
                            keyPath: 'id'
                        })

                        const rules = db.createObjectStore('rules', {
                            keyPath: ['source', 'id']
                        })
                        rules.createIndex('source', 'source')
                        rules.createIndex('category', 'category')
                        rules.createIndex('severity', 'severity')
                        rules.createIndex('languages', 'languages')
                    case 2:
                        console.log('Upgrading to DB version 2')
                        const collections = db.createObjectStore('collections', {
                            keyPath: 'id'
                        })

                        collections.createIndex('type', 'type')
                }
            }
        })
    }

    private async bulkWrite<Name extends StoreNames<SemgrepSearchDB>>(name: Name, items: { [index: string]: StoreValue<SemgrepSearchDB, Name> }, clear = false) {
        const tx = this.db.transaction(name, "readwrite")
        const store = tx.objectStore(name)

        if (clear) {
            store.clear()
        }

        for (const item of Object.values(items)) {
            store.put(item)
        }
        await tx.done
    }

    private async update(): Promise<Metadata> {
        const updateData = shippedData as SemgrepSearchJSON
        const updateMeta = Object.values(updateData.meta)[0]
        const currentMeta = await this.getMetadata()

        if (currentMeta !== undefined && parseDate(currentMeta.created_on) >= parseDate(updateMeta.created_on)) {
            // No need to update, already on same version
            console.info("Already on the latest version")
            console.debug(currentMeta.created_on, updateMeta.created_on)
            return currentMeta
        }

        await this.db.put("meta", {...updateMeta, id: "meta"})

        await this.bulkWrite("repos", updateData.repos, true)
        await this.bulkWrite("rules", updateData.rules, true)

        return updateMeta
    }

    private signalUpdate<T>(name: StoreNames<SemgrepSearchDB>): (result: T) => T {
        return result => {
            console.debug("Updating", name)
            this.onUpdate.set([name])
            return result
        }
    }

    public onChange<T extends StoreNames<SemgrepSearchDB>>(name: T, fn: (db: Database, values: StoreValue<SemgrepSearchDB, T>[]) => void) {
        return this.changeListeners[name].subscribe(values => fn(this, values))
    }

    public async getMetadata(): Promise<Metadata | undefined> {
        return this.db.get("meta", "meta")
    }

    public async getRepositories(): Promise<Repository[]> {
        return this.db.getAll("repos")
    }

    public async getRules(): Promise<Rule[]> {
        return this.db.getAll("rules")
    }

    public async getCollections(): Promise<Collection<any>[]> {
        return this.db.getAll("collections")
    }

    public async putCollection(collection: Collection<any>) {
        return this.db.put("collections", collection).then(this.signalUpdate("collections"))
    }

    public async deleteCollection(id: string) {
        return this.db.delete("collections", id).then(this.signalUpdate("collections"))
    }
    
}