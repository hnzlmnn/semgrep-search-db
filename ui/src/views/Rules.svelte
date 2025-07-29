<script lang="ts">
    import {Button, Pagination, PaginationSkeleton, Search, Toggle} from "carbon-components-svelte";
    import PageTitle from "../components/layout/PageTitle.svelte";
    import type {Rule, RuleRow} from "../models/rule";
    import {loading} from "../storage/uistate";
    import ContentWidth from "../components/layout/ContentWidth.svelte";
    import Filter from "../components/rule/Filter.svelte";
    import type {MultiSelectItem} from "carbon-components-svelte/src/MultiSelect/MultiSelect.svelte";
    import {languageName} from "../util/languages";
    import RuleTile from "../components/rule/RuleTile.svelte";
    import {Filter as FilterIcon} from "carbon-icons-svelte";
    import {CachedDatabase, ViewData} from "../storage/cache";
    import {delay} from "../util/delay";
    import {capitalize} from "../util/text";
    import {onMount} from "svelte";
    import AddToCollectionModal from "../components/collection/AddToCollectionModal.svelte";
    import {isStaticCollection} from "../models/collection";


    type FilterKey = Pick<Rule, "source" | "languages" | "category" | "severity">
    type Filters = { [index in keyof FilterKey]: string[] } & { keyword: string }

    let sources: MultiSelectItem[] = []
    let categories: MultiSelectItem[] = []
    let languages: MultiSelectItem[] = []
    let severities: MultiSelectItem[] = []

    const filter: Filters = {
        source: [],
        languages: [],
        category: [],
        severity: [],
        keyword: "",
    }

    let viewData: ViewData | null = null
    let filteredRows: RuleRow[] = []

    let pageSize = 10;
    let page = 1;
    let includeCategoryNull = false
    let filtering = true
    let headerExpanded = false

    onMount(() => CachedDatabase.instance().viewData.subscribe(async data => {
        viewData = data

        if (data !== null) {
            sources = data.uniques.sources
                .map(source => data.repos.get(source))
                .filter(repo => !!repo)
                .map(repo => {
                    return {...repo, text: repo.name}
                })

            categories = data.uniques.categories
                .map(category => {
                    if (category === null) {
                        return {id: "", text: "None"}
                    }
                    return {id: category, text: capitalize(category)}
                })

            languages = data.uniques.languages
                .map(language => ({id: language, text: languageName(language)}))

            severities = data.uniques.severities
                .map(severity => {
                    if (severity === null) {
                        return {id: "", text: "None"}
                    }
                    return {id: severity, text: severity}
                })
        }

        doFilter()
    }))

    function doFilter() {
        const oldLength = filteredRows.length
        filtering = true
        requestAnimationFrame(async () => {
            filteredRows = (viewData?.ruleRows ?? []).filter(rule => {
                const filterSource = filter.source.length === 0 || filter.source.includes(rule.source)
                if (!filterSource) {
                    return false
                }

                const filterLanguage = filter.languages.length === 0 || new Set(filter.languages).intersection(new Set(rule.languages)).size > 0
                if (!filterLanguage) {
                    return false
                }

                const filterCategory = filter.category.length === 0 || (filter.category.includes(rule.category === null ? "" : rule.category))
                if (!filterCategory) {
                    return false
                }

                const filterKeyword = filter.keyword.length === 0 || rule.id.includes(filter.keyword)
                if (!filterKeyword) {
                    return false
                }

                return true
            })
            if (filteredRows.length < oldLength) {
                page = 1
            }
            filtering = false
        })
    }

    function toggleExpand(e: Event) {
        e.target !== null && ((e.target as any).closest("button") as HTMLButtonElement).blur()
        headerExpanded = !headerExpanded
    }

    let addRuleToCollectionOpen = false
    let addRuleToCollection: RuleRow | null = null

    function showCollectionPicker(rule: RuleRow) {
        addRuleToCollection = rule
        addRuleToCollectionOpen = true
    }

    function addToCollection(id: string) {
        const collection = viewData?.collections.find(collection => collection.id === id)
        if (addRuleToCollection === null || collection === undefined || !isStaticCollection(collection)) {
            return
        }
        console.debug(`adding ${addRuleToCollection.id} to collection ${collection.name}`)
        collection.rules.push({
            source: addRuleToCollection.source,
            id: addRuleToCollection.rule_id,
        })
        CachedDatabase.instance().putCollection(collection).then(() => {
            addRuleToCollection = null
            addRuleToCollectionOpen = false
        })
    }

    $: visibleRows = filteredRows.slice((page - 1) * pageSize, page * pageSize)
</script>

<AddToCollectionModal bind:open={addRuleToCollectionOpen} rule={addRuleToCollection} on:add={e => addToCollection(e.detail)}/>

<PageTitle bind:expanded={headerExpanded} text="Rules">
    <Search bind:value={filter.keyword} on:change={() => doFilter()} placeholder="Search for keywords..." size="sm"
            skeleton={$loading}/>
    <Button icon={FilterIcon} iconDescription="Apply filters" tooltipAlignment="end" kind="ghost" on:click={e => toggleExpand(e)}
            size="small"/>
    <ContentWidth slot="expand">
        <div class="filters">
            <Filter
                    bind:selectedIds={filter.source}
                    filterable
                    hideLabel
                    items={sources}
                    on:select={() => doFilter()}
                    placeholder="Source"
            />
            <Filter
                    bind:selectedIds={filter.category}
                    filterable
                    hideLabel
                    items={categories}
                    on:select={() => doFilter()}
                    placeholder="Category"
            />
            <Filter
                    bind:selectedIds={filter.languages}
                    filterable
                    hideLabel
                    items={languages}
                    on:select={() => doFilter()}
                    placeholder="Language"
            />
            <Filter
                    bind:selectedIds={filter.severity}
                    filterable
                    hideLabel
                    items={severities}
                    on:select={() => doFilter()}
                    placeholder="Severity"
            />
            <Toggle bind:toggled={includeCategoryNull} labelText="Include rules without category" on:toggle={() => doFilter()}
                    size="sm"/>
        </div>
    </ContentWidth>
</PageTitle>
<ContentWidth class="full-height">
    <div class="container">
        <!--        <div class="header-wrapper">-->
        <!--            <div class="header">-->
        <!--            <Search placeholder="Search for keywords..." bind:value={filter.keyword} on:change={() => doFilter()} skeleton={$loading}/>-->
        <!--            <div class="filter-container bx&#45;&#45;tile bx&#45;&#45;tile&#45;&#45;light">-->
        <!--                <FilterPanel light tileExpandedLabel="Hide" tileCollapsedLabel="Show">-->
        <!--                    <div slot="above">-->
        <!--                        <h5>Additional Filters</h5>-->
        <!--                    </div>-->
        <!--                    <div slot="below">-->
        <!--                        <div class="filters">-->
        <!--                            <Filter-->
        <!--                                    filterable-->
        <!--                                    hideLabel-->
        <!--                                    placeholder="Source"-->
        <!--                                    items={sources}-->
        <!--                                    bind:selectedIds={filter.source}-->
        <!--                                    on:select={() => doFilter()}-->
        <!--                            />-->
        <!--                            <Filter-->
        <!--                                    filterable-->
        <!--                                    hideLabel-->
        <!--                                    placeholder="Category"-->
        <!--                                    items={categories}-->
        <!--                                    bind:selectedIds={filter.category}-->
        <!--                                    on:select={() => doFilter()}-->
        <!--                            />-->
        <!--                            <Filter-->
        <!--                                    filterable-->
        <!--                                    hideLabel-->
        <!--                                    placeholder="Language"-->
        <!--                                    items={languages}-->
        <!--                                    bind:selectedIds={filter.languages}-->
        <!--                                    on:select={() => doFilter()}-->
        <!--                            />-->
        <!--                            <Filter-->
        <!--                                    filterable-->
        <!--                                    hideLabel-->
        <!--                                    placeholder="Severity"-->
        <!--                                    items={severities}-->
        <!--                                    bind:selectedIds={filter.severity}-->
        <!--                                    on:select={() => doFilter()}-->
        <!--                            />-->
        <!--                            <Toggle size="sm" labelText="Include rules without category" bind:toggled={includeCategoryNull} on:toggle={() => doFilter()} />-->
        <!--                        </div>-->
        <!--                    </div>-->
        <!--                </FilterPanel>-->
        <!--            </div>-->
        <!--            </div>-->
        <!--        </div>-->
        <div class="rule-list">
            {#if $loading || filtering}
                <div class="rule">
                    <RuleTile skeleton/>
                </div>
            {:else if visibleRows.length === 0}
                <p>No rules found for the selected filters</p>
            {:else}
                {#each visibleRows as row, i}
                    <div class="rule">
                        <RuleTile rule={row} on:add={e => showCollectionPicker(e.detail)} />
                    </div>
                {/each}
            {/if}
        </div>
    </div>
    <div class="pagination">
        {#if $loading}
            <PaginationSkeleton/>
        {:else}
            <Pagination
                    bind:pageSize
                    bind:page
                    totalItems={filteredRows.length}
                    pageSizes={[
                    5,
                    10,
                    20,
                    50,
                ]}
            />
        {/if}
    </div>
</ContentWidth>

<style lang="scss">
  .filters {
    margin: 0 calc(-1 * var(--cds-spacing-03, 1rem));
    margin-top: var(--cds-spacing-04, 1rem);
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    justify-content: start;

    & > :global(*) {
      padding: var(--cds-spacing-03, 1rem);
      width: 33%;
      @media screen and (max-width: 890px) {
        width: 50%;
      }
      @media screen and (max-width: 600px) {
        width: 100%;
      }
    }
  }

  :global(.content--max-width.full-height) {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    min-height: 0;
    position: relative;
    transition: margin-bottom;
    margin-bottom: var(--cds-spacing-07, 2rem);
    @media screen and (max-width: 600px) {
      margin-bottom: 0;
    }

    .container {
      flex-grow: 1;
      display: flex;
      flex-direction: column;
      overflow-y: auto;
      overflow-x: hidden;

      .header-wrapper {
        position: sticky;
        z-index: 1000;
        top: calc(-1 * var(--cds-spacing-05, 1rem));
        margin: calc(-1 * var(--cds-spacing-05, 1rem));
        background-color: var(--cds-ui-01, #f4f4f4);

        .header {
          padding: var(--cds-spacing-05, 1rem);

          .filter-container {
            margin-top: var(--cds-spacing-04, 1rem);
            flex-shrink: 0;
          }
        }

      }

      .rule-list {
        flex-grow: 1;
        //overflow-y: auto;

        display: flex;
        flex-direction: row;
        flex-wrap: wrap;
        padding: var(--cds-spacing-04, 1rem) 0;
        margin: 0 calc(-1 * var(--cds-spacing-05, 1rem));
        @media screen and (max-width: 1100px) {
          //margin: 0 calc(-1 * var(--cds-spacing-03, .7125rem));
        }

        .rule {
          width: 100%;
          //width: 50%;
          padding: var(--cds-spacing-05, 1rem);
          @media screen and (max-width: 1100px) {
            width: 100%;
            //padding: var(--cds-spacing-03, .7125rem);
          }
        }
      }
    }

    .pagination {
      position: sticky;
      bottom: 0;
    }
  }
</style>