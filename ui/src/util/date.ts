import {DateTime} from "luxon";

export function parseDate(date: string): DateTime {
    const parsed = DateTime.fromISO(date.replace(" ", "T"))
    if (!parsed.isValid) {
        throw new Error("Invalid date")
    }
    return parsed
}