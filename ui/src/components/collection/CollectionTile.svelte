<script lang="ts">
    import type {LoadedCollection} from "../../models/collection";
    import {CachedDatabase} from "../../storage/cache";
    import {Edit, FlashFilled, PinFilled, TrashCan, Download} from "carbon-icons-svelte";
    import {Button, TooltipIcon, Modal, truncate} from "carbon-components-svelte";
    import {capitalize} from "../../util/text";
    import {createEventDispatcher} from "svelte";

    const dispatch = createEventDispatcher();

    export let collection: LoadedCollection<any>
    export let skeleton = false

    let downloadAlert = false

    function edit() {
        dispatch('edit', collection)
    }

    function download() {
        downloadAlert = true
    }

    $: icon = collection.type === 'dynamic' ? FlashFilled : PinFilled
</script>

<Modal
        bind:open={downloadAlert}
        modalHeading="Not yet implemented"
        on:click:button--primary={() => (downloadAlert = false)}
        primaryButtonText="Ok"
>
    <p>This feature is currently under development.</p>
</Modal>

<div class="bx--tile collection">
    <div class="header">
        <div class="icon">
            <TooltipIcon {icon} tooltipText={capitalize(collection.type)}/>
        </div>
        <div class="title">
            <h2 class:bx--skeleton__text={skeleton} use:truncate>{collection.name}</h2>
        </div>
        <div class="actions">
            <Button icon={Download} iconDescription="Download Rules" kind="primary"
                    on:click={() => download()} size="small"
                    tooltipAlignment="end"/>
            <Button icon={Edit} iconDescription="Edit Collection" kind="tertiary"
                    on:click={() => edit()} size="small"
                    tooltipAlignment="end"/>
            <Button icon={TrashCan} iconDescription="Delete Collection" kind="danger-tertiary"
                    on:click={() => CachedDatabase.instance().deleteCollection(collection.id)} size="small"
                    tooltipAlignment="end"/>
        </div>
    </div>
    <span class="muted">{collection.id}</span>
    <p>{collection.resolvedRules.length} rules</p>
</div>

<style lang="scss">
  .collection {
    .header {
      display: flex;
      flex-direction: row;
      margin-bottom: var(--cds-spacing-01);
      align-items: center;

      .icon {
        margin-right: var(--cds-spacing-02);
      }

      .title {
        flex-grow: 1;
        margin-right: var(--cds-spacing-04);

        h2 {
          font-size: var(--cds-productive-heading-03-font-size, 2rem);
          color: var(--cds-text-01);
          width: 100%;
        }

        h5 {
          margin-top: .2rem;
          color: var(--cds-text-02);
          width: 100%;
          display: flex;
          flex-direction: row;
          align-items: center;

          span {
            flex-grow: 1;
            margin-bottom: 0;
            margin-left: var(--cds-spacing-04);
          }
        }

        & :global(.bx--tag) {
          margin-left: 0;
          margin-right: var(--cds-spacing-03);
        }
      }
    }
  }

  span {
    display: block;
    margin-bottom: var(--cds-spacing-01);

    &.muted {
      color: var(--cds-text-03);
    }
  }


</style>