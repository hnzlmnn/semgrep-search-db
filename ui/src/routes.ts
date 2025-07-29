import Dashboard from "./views/Dashboard.svelte";
import Rules from "./views/Rules.svelte";
import RuleDetails from "./views/RuleDetails.svelte";
import NotFound from "./views/NotFound.svelte";
import Collections from "./views/Collections.svelte";
import Repositories from "./views/Repositories.svelte";
import RunConfig from "./views/RunConfig.svelte";

export const routes = {
    // Exact path
    '/': Dashboard,

    // Using named parameters, with last being optional
    '/rules': Rules,
    '/rules/:source/:id': RuleDetails,

    '/repositories': Repositories,

    '/collections': Collections,

    '/generator': RunConfig,

    // Catch-all
    // This is optional, but if present it must be the last
    '*': NotFound,
}