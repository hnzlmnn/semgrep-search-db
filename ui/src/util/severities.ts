import type {KnownSeverity} from "./runs";

export type SeverityColors = "red"
    | "magenta"
    | "purple"
    | "blue"
    | "cyan"
    | "teal"
    | "green"
    | "gray"
    | "cool-gray"
    | "warm-gray"
    | "high-contrast"
    | "outline"

export function severityColor(severity: KnownSeverity | string | null | undefined): SeverityColors {
    switch (severity) {
        case null:
        case undefined:
            return 'teal'
        case "INVENTORY":
            return 'green'
        case "INFO":
            return 'blue'
        case "WARNING":
            return 'purple'
        case "ERROR":
            return 'red'
    }
    return 'cool-gray'
}