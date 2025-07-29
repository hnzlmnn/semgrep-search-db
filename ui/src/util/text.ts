export function capitalize(s: string | null | undefined) {
    if (s === null || s === undefined) {
        return ""
    }
    return s.split(" ").map(s => s.charAt(0).toUpperCase() + s.slice(1)).join(" ");
}