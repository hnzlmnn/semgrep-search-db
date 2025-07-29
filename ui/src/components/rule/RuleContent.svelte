<script lang="ts">

import {CodeSnippet} from "carbon-components-svelte";
import type {RuleRow} from "../../models/rule";
import {afterUpdate, onMount} from "svelte";

export let rule: RuleRow | undefined
export let expanded: boolean = false
export let light: boolean = false

/** Specify the padding of the tile (number of pixels) */
export let tilePadding = 0;

export let ref: Element = null as unknown as Element;


afterUpdate(() => {
    const style = getComputedStyle(ref);

    tilePadding =
        parseInt(style.getPropertyValue("padding-top"), 10) +
        parseInt(style.getPropertyValue("padding-bottom"), 10);
});
</script>


<div class="content bx--tile"
     bind:this={ref}
     class:expanded={expanded}
     class:bx--tile--light={light}
     class:bx--tile--is-expanded={expanded}
     aria-expanded="{expanded}"
     style:max-height={expanded ? "none" : `${0}px`}>
    <CodeSnippet code={rule?.content} {light} type="multi"/>
</div>

<style lang="scss">
  .content {
    overflow: hidden;
    min-height: 0;
    padding: 0;
    &.expanded {
      margin-top: var(--cds-spacing-04);
    }

    & > :global(.bx--snippet) {
      max-width: 100%;
    }
  }
</style>