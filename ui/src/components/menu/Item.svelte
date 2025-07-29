<script lang="ts">
    import {getContext} from "svelte";
    import {HeaderNavItem, SideNavLink} from "carbon-components-svelte";
    import {location, push} from "svelte-spa-router";
    import {sideBarOpen} from "../../storage/uistate";

    export const isSelected: boolean = false;
    export let href: string;
    export let activeCheck: (loc: string) => boolean = () => false;
    const ctx = getContext("menu") as { kind: string }
    const component = ctx.kind === "header" ? HeaderNavItem : SideNavLink

    function goto(e: Event) {
        e.stopPropagation()
        e.preventDefault()
        if (e.currentTarget && 'blur' in e.currentTarget) {
            (e.currentTarget as any).blur()
        }
        push(href)
        sideBarOpen.set(false)
    }

    $: isActive = activeCheck($location)
</script>

{#if $$slots.default}
    <svelte:component this={component} {href} isSelected={isActive} {...$$restProps} on:click={goto}><slot/></svelte:component>
{:else}
    <svelte:component this={component} {href} isSelected={isActive} {...$$restProps} on:click={goto}>
        <div class="aligner">
            {#if $$props.icon && ctx.kind === "header"}<svelte:component this={$$props.icon}/>{/if}
            {#if $$props.text}<span>{$$props.text}</span>{/if}
        </div>
    </svelte:component>
{/if}

<style lang="scss">
    .aligner {
      display: flex;
      align-items: center;
      gap: var(--cds-spacing-03);
    }
</style>