<script lang="ts">
    import {setContext} from "svelte";
    import {HeaderNav, SideNavItems} from "carbon-components-svelte";

    export let kind: "header" | "sidebar"

    setContext('menu', {
        kind,
    });

    const component = kind === "header" ? HeaderNav : SideNavItems
</script>

<svelte:component this={component}>
    <slot/>
</svelte:component>
