import type {Repository} from "./repository";

export interface Rule {
    source: string
    id: string
    severity: string | null
    languages: string[]
    category: string | null
    description: string
    content: string
}

export type RuleRow = Rule & { rule_id: string, repo: Repository }