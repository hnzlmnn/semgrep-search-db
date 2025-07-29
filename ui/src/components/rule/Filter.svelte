<script lang="ts">
    import {MultiSelect, SelectSkeleton} from "carbon-components-svelte";
    import {loading} from "../../storage/uistate";

    export let selectedIds: string[]
</script>

{#if $loading}
    <SelectSkeleton/>
{:else}
    <MultiSelect spellcheck="false" bind:selectedIds on:select {...$$restProps} />
{/if}

<style lang="scss">
</style>