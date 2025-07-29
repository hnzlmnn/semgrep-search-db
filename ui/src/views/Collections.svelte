<script lang="ts">
    import {CachedDatabase, ViewData} from "../storage/cache";
    import {AddLarge, Filter as FilterIcon} from "carbon-icons-svelte";
    import {Button, RadioButton, RadioButtonGroup} from "carbon-components-svelte";
    import PageTitle from "../components/layout/PageTitle.svelte";
    import {onMount} from "svelte";
    import ContentWidth from "../components/layout/ContentWidth.svelte";
    import {
        type CollectionType,
        isDynamicCollection,
        isStaticCollection,
        type LoadedCollection
    } from "../models/collection";
    import CollectionTile from "../components/collection/CollectionTile.svelte";
    import CollectionManagement from "../components/collection/CollectionManagement.svelte";
    import AddToCollectionModal from "../components/collection/AddToCollectionModal.svelte";
    import CreateCollectionModal from "../components/collection/CreateCollectionModal.svelte";
    import EditCollectionModal from "../components/collection/EditCollectionModal.svelte";

    let viewData: ViewData | null
    let headerExpanded = false
    let filterType: CollectionType | '' = ''

    onMount(() => CachedDatabase.instance().viewData.subscribe(async data => {
        viewData = data
    }))

    function toggleExpand(e: Event) {
        e.target !== null && ((e.target as any).closest("button") as HTMLButtonElement).blur()
        headerExpanded = !headerExpanded
    }

    function filterCollections(collections: LoadedCollection<any>[] | undefined, filter: CollectionType | ''): LoadedCollection<any>[] {
        if (collections === undefined) {
            return []
        }
        if (filter === '') {
            return collections
        }
        return collections.filter(collection => {
            switch (filter) {
                case "dynamic":
                    return isDynamicCollection(collection)
                case "static":
                    return isStaticCollection(collection)
            }
        })
    }

    function edit(e: CustomEvent<LoadedCollection<any>>) {
        editCollection = e.detail
        editCollectionOpen = true
    }

    let createNewCollectionOpen = false
    let editCollectionOpen = false
    let editCollection: LoadedCollection<any> | null = null

    $: filteredCollections = filterCollections(viewData?.collections, filterType)
</script>

<CreateCollectionModal bind:open={createNewCollectionOpen} />
<EditCollectionModal bind:open={editCollectionOpen} bind:editCollection />

<PageTitle bind:expanded={headerExpanded} text="My Collections">
    <Button icon={AddLarge} iconDescription="Create collection"
            kind="ghost" on:click={() => createNewCollectionOpen = true} size="small"
            tooltipAlignment="end"/>
    <Button icon={FilterIcon} iconDescription="Apply filters" kind="ghost" on:click={e => toggleExpand(e)}
            size="small"
            tooltipAlignment="end"/>
    <ContentWidth slot="expand">
        <div class="filter">
            <RadioButtonGroup bind:selected={filterType} legendText="Collection Type">
                <RadioButton labelText="All" value=""/>
                <RadioButton labelText="Dynamic" value="dynamic"/>
                <RadioButton labelText="Static" value="static"/>
            </RadioButtonGroup>
        </div>
    </ContentWidth>
</PageTitle>
<ContentWidth>
    <div class="collection-list">
        {#each filteredCollections as collection}
            <div class="collection">
                <CollectionTile {collection} on:edit={edit}/>
            </div>
        {/each}
    </div>
</ContentWidth>


<style lang="scss">
  .filter {
    margin-top: var(--cds-spacing-05);
  }

  .collection-list {
    margin: 0 calc(-1 * (var(--cds-spacing-05, 1rem) + 1rem));
    display: flex;
    flex-wrap: wrap;

    .collection {
      width: 50%;
      padding: var(--cds-spacing-05, 1rem);

      @media screen and (max-width: 1100px) {
        width: 100%;
        padding: var(--cds-spacing-03, .7125rem);
      }
    }
  }
</style>