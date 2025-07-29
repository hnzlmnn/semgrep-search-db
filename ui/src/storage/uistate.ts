import {writable} from "svelte/store";

export type Theme = "light" | "dark" | null;

function normalizeTheme(theme: string | null): Theme {
    if (theme == null) {
        return null
    }
    return theme === "light" ? "light" : "dark"
}

function getNextTheme(current: Theme): Theme {
    switch (current) {
        case "light":
            return "dark"
        case "dark":
            return null
        case null:
            return "light"
    }
}

export const loading = writable(true)
export const sideBarOpen = writable(false)
export const theme = writable<Theme>(normalizeTheme(localStorage.getItem("theme")))

theme.subscribe(theme => {
    if (theme === null) {
        localStorage.removeItem("theme")
    } else {
        localStorage.setItem("theme", theme)
    }
})

export function nextTheme() {
    theme.update(getNextTheme)
}