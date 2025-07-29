<script lang="ts">
    import {ChevronDown, ChevronUp} from "carbon-icons-svelte";
    import {afterUpdate, onMount} from "svelte";

    export let expanded: boolean = false
    export let light: boolean = false
    export let tileExpandedLabel: string = ""
    export let tileCollapsedLabel: string = ""

    /** Specify the max height of the tile  (number of pixels) */
    export let tileMaxHeight = 0;

    /** Specify the padding of the tile (number of pixels) */
    export let tilePadding = 0;

    export let ref: Element = null as unknown as Element;
    let refAbove: Element = null as unknown as Element;

    onMount(() => {
        const resizeObserver = new ResizeObserver(([elem]) => {
            tileMaxHeight = elem.contentRect.height;
        });

        resizeObserver.observe(refAbove);

        return () => {
            resizeObserver.disconnect();
        };
    });

    afterUpdate(() => {
        if (tileMaxHeight === 0) {
            tileMaxHeight = refAbove.getBoundingClientRect().height;
        }

        const style = getComputedStyle(ref);

        tilePadding =
            parseInt(style.getPropertyValue("padding-top"), 10) +
            parseInt(style.getPropertyValue("padding-bottom"), 10);
    });
</script>

<div class="bx--tile"
     bind:this={ref}
     class:expanded={expanded}
     class:bx--tile--light={light}
     class:bx--tile--is-expanded={expanded}
     aria-expanded="{expanded}"
     style:max-height={expanded ? "none" : `${tileMaxHeight + tilePadding}px`}>
    <div bind:this="{refAbove}" class="bx--tile-content">
        <span class:bx--tile-content__above-the-fold={true}>
            <slot name="above"/>
        </span>
    </div>
    <div role="none" class:bx--tile__chevron="{true}" on:click={() => expanded = !expanded}>
        <span>{expanded ? tileExpandedLabel : tileCollapsedLabel}</span>
        <ChevronDown />
    </div>
    <div class="bx--tile-content">
        <span class:bx--tile-content__below-the-fold={true}>
            <slot class="below" name="below"/>
        </span>
    </div>
</div>

<style lang="scss">
    .bx--tile {
      display: flex;
      flex-direction: column;
      position: relative;

      .below {
        will-change: max-height, height;
        transition: height 1s, max-height 1s;
      }
    }
</style>