<script lang="ts">
    import type {RuleRow} from "../../models/rule";
    import {createEventDispatcher, onMount} from "svelte";
    import {CachedDatabase, ViewData} from "../../storage/cache";
    import {isStaticCollection, type StaticCollection} from "../../models/collection";
    import {Button, ComposedModal, ModalBody, ModalFooter, ModalHeader} from "carbon-components-svelte";
    import {AddLarge} from "carbon-icons-svelte";

    const dispatch = createEventDispatcher();

    export let open: boolean
    export let rule: RuleRow | null

    let staticCollections: StaticCollection[] = []

    onMount(() => CachedDatabase.instance().viewData.subscribe(async data => {
        if (data !== null) {
            staticCollections = data.collections.filter(collection => isStaticCollection(collection))
        } else {
            staticCollections = []
        }
    }))

    $: availableCollections = rule === null ? [] : staticCollections.filter(collection => !collection.rules.includes({
        source: rule.source,
        id: rule.id,
    }))

    function alreadyInCollection(collection: StaticCollection) {
        if (rule === null) {
            return false
        }
        return collection.rules.find(r => r.source === rule.source && r.id === rule.rule_id) !== undefined
    }

    function add(collection: StaticCollection) {
        dispatch('add', collection.id)
    }
</script>

<ComposedModal bind:open {...$$restProps}>
    <ModalHeader label="Collections" title="Add rule to collection" />
    <ModalBody hasScrollingContent>
        <p>Select a collection to add rule "{rule?.rule_id}" to</p>
        <ul class="collection-list">
            {#each availableCollections as collection}
                <li role="none" class="collection" on:click={() => add(collection)}>
                    <span>{collection.name}</span>
                    <Button icon={AddLarge} size="small" iconDescription="Add to collection" tooltipPosition="left"
                            disabled={alreadyInCollection(collection)} />
                </li>
            {/each}
        </ul>
    </ModalBody>
    <ModalFooter primaryButtonText="Proceed" />
</ComposedModal>

<style lang="scss">
    .collection-list {
      margin: var(--cds-spacing-05) 0;
      .collection {
        display: flex;
        list-style: none;
        align-items: center;
        margin: var(--cds-spacing-02) 0;
        padding: var(--cds-spacing-02) var(--cds-spacing-02);
        background-color: rgba(0, 0, 0, .1);

        span {
          flex-grow: 1;
        }
      }
    }
</style>