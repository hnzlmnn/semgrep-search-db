<script lang="ts">
    import {afterUpdate, onMount} from "svelte";

    export let text: string

    export let light: boolean = false
    export let expanded: boolean = false

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

<div class="bx--tile elevate-1"
     bind:this={ref}
     class:expanded={expanded}
     class:bx--tile--light={light}
     class:bx--tile--is-expanded={expanded}
     aria-expanded="{expanded}"
     style:max-height={expanded ? "none" : `${tileMaxHeight + tilePadding}px`}>
    <div bind:this="{refAbove}" class="bx--tile-content">
        <div class="row content--max-width">
            <h1>{text}</h1>
            <div class="action">
                <slot/>
            </div>
        </div>
    </div>
    {#if $$slots.expand}
        <div class="bx--tile-content expansion">
            <span class:bx--tile-content__below-the-fold={true}>
                <slot name="expand"></slot>
            </span>
        </div>
    {/if}
</div>

<style lang="scss">
  :global(.bx--header ~ .bx--content) .bx--tile {
    top: 3rem;
  }

  .bx--tile {
    position: sticky;
    top: 0;
    z-index: 5000;
    margin: -2rem;
    margin-bottom: 2rem;
    padding: 1rem 2rem;
    min-height: auto;

    .row {
      display: flex;
      align-items: start;

      @media screen and (max-width: 580px) {
        flex-direction: column;
        h1 {
          margin-bottom: var(--cds-spacing-04, .75rem);
          width: 100%;
        }
        .action {
          width: 100%
        }
      }

      h1 {
        flex-grow: 1;
        font-size: var(--cds-heading-04-font-size);
      }

      .action {
        display: flex;
        flex-direction: row;

        //& > :global(.bx--btn) {
        //  width: 100%;
        //  max-width: 100%;
        //}
      }
    }

    .expansion {
      pointer-events: none;
    }

    &.bx--tile--is-expanded {
      .expansion {
        pointer-events: inherit;
      }
    }
  }
</style>