import type {RuleRow} from "./rule";

export type CollectionType = "dynamic" | "static"

export interface Collection<T extends CollectionType> {
    id: string
    type: T
    name: string
}

export function isCollectionType<T extends CollectionType>(collection: Collection<any>, type: CollectionType): collection is Collection<T>  {
    return collection.type == type
}

export function isStaticCollection(collection: Collection<any>): collection is StaticCollection {
    return isCollectionType(collection, "static")
}

export function isDynamicCollection(collection: Collection<any>): collection is DynamicCollection {
    return isCollectionType(collection, "dynamic")
}

export function isLoadedCollection<T extends CollectionType>(collection: Collection<T>): collection is LoadedCollection<T> {
    return 'resolvedRules' in collection
}

export interface StaticCollection extends Collection<"static"> {
    rules: Array<{
        source: string,
        id: string
    }>
}

export interface DynamicCollection extends Collection<"dynamic"> {
    sources: string[]
    categories: string[]
    languages: string[]
    severities: string[]
    keywords: string
}

export interface LoadedCollection<T extends CollectionType> extends Collection<T> {
    resolvedRules: RuleRow[]
}