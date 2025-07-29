<script lang="ts">
    import ContentWidth from "../components/layout/ContentWidth.svelte";
    import PageTitle from "../components/layout/PageTitle.svelte";
    import RepositoryTile from "../components/repo/RepositoryTile.svelte";
    import {CachedDatabase, type RepositoryWithStats, ViewData} from "../storage/cache";
    import {loading} from "../storage/uistate";
    import {Dropdown} from "carbon-components-svelte";
    import type {DropdownItem, DropdownItemId} from "carbon-components-svelte/src/Dropdown/Dropdown.svelte";
    import {onMount} from "svelte";

    let viewData: ViewData | null = null

    type SortMode = {id: string, text: string, sort: (repos: RepositoryWithStats[]) => RepositoryWithStats[]}

    const sortModes: SortMode[] = [
        {
            id: 'rules_desc',
            text: '# rules (desc)',
            sort: (repos: RepositoryWithStats[]) => repos.sort(
                (a: RepositoryWithStats, b: RepositoryWithStats) => b.stats.numRules - a.stats.numRules
            ),
        },
        {
            id: 'rules_asc',
            text: '# rules (asc)',
            sort: (repos: RepositoryWithStats[]) => repos.sort(
                (a: RepositoryWithStats, b: RepositoryWithStats) => a.stats.numRules - b.stats.numRules
            ),
        },
        {
            id: 'lang_desc',
            text: '# languages (desc)',
            sort: (repos: RepositoryWithStats[]) => repos.sort(
                (a: RepositoryWithStats, b: RepositoryWithStats) =>
                    [...b.stats.languages.keys()].length - [...a.stats.languages.keys()].length
            ),
        },
        {
            id: 'lang_asc',
            text: '# languages (asc)',
            sort: (repos: RepositoryWithStats[]) => repos.sort(
                (a: RepositoryWithStats, b: RepositoryWithStats) =>
                    [...a.stats.languages.keys()].length - [...b.stats.languages.keys()].length
            ),
        },
    ]
    let sortFunc = sortModes[0].sort

    let sortedRepos: RepositoryWithStats[] = []

    onMount(() => CachedDatabase.instance().viewData.subscribe(data => {
        viewData = data
        doSort()
    }))

    function doSort() {
        if (viewData === null) {
            sortedRepos = []
        } else {
            sortedRepos = sortFunc([...viewData.repos.values()])
        }
    }

    function setSortMode(e: CustomEvent<{
        selectedId: DropdownItemId;
        selectedItem: DropdownItem;
    }>) {
        sortFunc = (e.detail.selectedItem as SortMode).sort
        doSort()
    }
</script>

<PageTitle text="Sources">
    <Dropdown
            size="sm"
            type="inline"
            titleText="Sort by"
            selectedId={sortModes[0].id}
            on:select={setSortMode}
            items={sortModes}
    />
</PageTitle>
<ContentWidth>
    <p>Semgrep Search currently contains rules from these repositories:</p>
    <div class="repositories-container">
        {#if $loading || viewData === null}
            <div class="repository">
                <RepositoryTile skeleton/>
            </div>
        {:else}
            {#each sortedRepos as repo}
                <div class="repository">
                    <RepositoryTile repo={repo} stats={repo.stats}/>
                </div>
            {/each}
        {/if}
    </div>
</ContentWidth>

<style lang="scss">
  .repositories-container {
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    padding: var(--cds-spacing-04, 1rem) 0;
    margin: 0 calc(-1 * var(--cds-spacing-05, 1rem));
    @media screen and (max-width: 920px) {
      margin: 0 calc(-1 * var(--cds-spacing-03, .7125rem));
    }

    .repository {
      width: 50%;
      padding: var(--cds-spacing-05, 1rem);
      @media screen and (max-width: 920px) {
        width: 100%;
        padding: var(--cds-spacing-03, .7125rem);
      }
    }
  }
</style>