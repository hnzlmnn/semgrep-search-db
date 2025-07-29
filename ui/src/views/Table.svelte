<script lang="ts">
    import {
        Button,
        DataTable,
        DataTableSkeleton, MultiSelect,
        OverflowMenu,
        OverflowMenuItem,
        Pagination, PaginationSkeleton,
        Toolbar,
        ToolbarContent,
        ToolbarMenu,
        ToolbarMenuItem,
        ToolbarSearch
    } from "carbon-components-svelte";
    import PageTitle from "../components/layout/PageTitle.svelte";
    import type {Repository} from "../models/repository";
    import type {Rule} from "../models/rule";
    import {Database} from "../storage/database";
    import {loading} from "../storage/uistate";
    import ContentWidth from "../components/layout/ContentWidth.svelte";
    import type {DataTableHeader} from "carbon-components-svelte/src/DataTable/DataTable.svelte";
    import {BookmarkAdd} from "carbon-icons-svelte";

    let repos: Repository[] = []
    let rules: Rule[] = []

    let rows: Rule[] = [];

    Database.instanceAsync().then(db => {
        db.onChange("meta", async db => {
            repos = [...await db.getRepositories()]
            rules = [...await db.getRules()]
            rows = rules.map(rule => ({...rule, rule_id: rule.id, id: `${rule.source}$$$${rule.id}`}))
        })
    })
    let pageSize = 25;
    let page = 1;

    const headers: DataTableHeader[] = [
        {key: "source", value: "Source"},
        {key: "rule_id", value: "ID"},
        {key: "category", value: "Category"},
        // { key: "rule", value: "Rule" },
        {key: "actions", empty: true}
    ]
</script>

<PageTitle text="Rules"/>
<ContentWidth class="full-height">
    {#if $loading}
        <DataTableSkeleton {headers} rows={pageSize}/>
        <PaginationSkeleton />
    {:else}
        <DataTable
                sortable
                stickyHeader
                title="Search for rules"
                description="This list of all rules can be filtered"
                {headers}
                {pageSize}
                {page}
                {rows}
        >
            <Toolbar>
                <ToolbarContent>
                    <ToolbarSearch/>
                    <ToolbarMenu>
                        <ToolbarMenuItem primaryFocus>Restart all</ToolbarMenuItem>
                        <ToolbarMenuItem href="https://cloud.ibm.com/docs/loadbalancer-service">
                            API documentation
                        </ToolbarMenuItem>
                        <ToolbarMenuItem hasDivider danger>Stop all</ToolbarMenuItem>
                    </ToolbarMenu>
                    <Button>Create balancer</Button>
                    <MultiSelect
                            type="inline"
                            titleText="Contact"
                            label="Select contact methods..."
                            items={[
    { id: "0", text: "Slack" },
    { id: "1", text: "Email" },
    { id: "2", text: "Fax" },
  ]}
                    />
                </ToolbarContent>
            </Toolbar>
            <svelte:fragment slot="cell" let:row let:cell>
                {#if cell.key === "actions"}
                    actions
                    <!--                    <Button icon={BookmarkAdd} iconDescription="Add to collection" />-->
                    <!--                    <OverflowMenu flipped>-->
                    <!--                        <OverflowMenuItem text="Add to collection"/>-->
                    <!--                    </OverflowMenu>-->
                {:else}{cell.value}{/if}
            </svelte:fragment>
        </DataTable>
        <Pagination
                bind:pageSize
                bind:page
                totalItems={rows.length}
                pageSizes={[
                10,
                25,
                50,
                100,
            ]}
        />
    {/if}
</ContentWidth>

<style lang="scss">
  :global(.content--max-width.full-height) {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    min-height: 0;
    position: relative;

    & :global(.bx--select__item-count), & :global(.bx--select__item-count + .bx--pagination__text) {
      display: flex;
    }

    & > :global(.bx--data-table-container) {
      //height: calc(100% - 40px);
      //max-height: calc(100% - 40px);
      display: flex;
      flex-direction: column;
      flex-grow: 1;
      min-height: 0;

      & > :global(.bx--data-table_inner-container) {
        flex-grow: 1;
        display: flex;
        flex-direction: column;
        min-height: 0;

        & > :global(.bx--toolbar-content) {
          display: flex;
        }

        & > :global(.bx--data-table) {
          flex-grow: 1;
          overflow: auto;
          max-height: 100%;

          & > :global(thead) {
            display: table-header-group;
            & > :global(tr) {
              display: table-row;
              & > :global(th) {
                display: table-cell;
                border-bottom: none;
              }
            }
          }

          & > :global(tbody) {
            display: table-row-group;
            & > :global(tr) {
              display: table-row;
              & > :global(td) {
                display: table-cell;
              }
            }
          }
        }
      }
    }
  }
</style>