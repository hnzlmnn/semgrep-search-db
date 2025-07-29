<script lang="ts">
    import {AspectRatio} from "carbon-components-svelte";

    export let title: string = ''
    export let large = false

    $: ratio = (large ? "2x1" : "1x1") as "2x1" | "1x1"
</script>

<AspectRatio {ratio} class="widget">
    <div class="bx--tile elevate-0">
        <div class="title">
            <h2>{#if title === ''}&nbsp;{:else}{title}{/if}</h2>
            <slot name="link"></slot>
        </div>
        <div class="divider"/>
        <div class="content">
            <slot/>
        </div>
        <div class="cta">
            <slot name="cta"></slot>
        </div>
    </div>
</AspectRatio>

<style lang="scss">
  .bx--tile {
    height: 100%;
    font-size: var(--cds-caption-02-font-size);
    padding: var(--cds-spacing-04, 1rem);
    display: flex;
    flex-direction: column;
    & > .title {
      margin: calc(-1 * var(--cds-spacing-04, 1rem));
      margin-bottom: 0;
      padding: var(--cds-spacing-04, 1rem);
      display: flex;
      & > h2 {
        font-size: inherit;
        font-weight: bold;
        flex-grow: 1;
      }
    }
    .divider {
      border-bottom: 1px solid var(--cds-border-subtle, #e0e0e0);
      margin: 0 calc(-1 * var(--cds-spacing-04, 1rem));
      margin-bottom: var(--cds-spacing-06, 1rem);
    }
    .content {
      flex-grow: 1;
    }
    .cta {
      flex-shrink: 0;
      display: flex;
      justify-content: end;
    }
  }
</style>