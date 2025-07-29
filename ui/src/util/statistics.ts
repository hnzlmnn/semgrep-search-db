import type {Rule} from "../models/rule";

export interface RepositoryStats {
    numRules: number
    languages: Map<string, number>
}

export function calcStats(rules: Rule[]): Map<string, RepositoryStats> {
    const statsMap = new Map<string, RepositoryStats>()

    rules.forEach(rule => {
        let stats = statsMap.get(rule.source)
        if (stats === undefined) {
            stats = {
                numRules: 0,
                languages: new Map(),
            }
        }
        stats.numRules += 1
        rule.languages.forEach(language => {
            let languageCounter = stats.languages.get(language)
            if (languageCounter === undefined) {
                languageCounter = 0
            }
            stats.languages.set(language, languageCounter + 1)
        })
        statsMap.set(rule.source, stats)
    })

    return statsMap
}