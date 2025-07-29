<script lang="ts">
    import {createEventDispatcher, onMount} from "svelte";
    import {CachedDatabase, ViewData} from "../../storage/cache";
    import {
        type Collection,
        type CollectionType,
        type DynamicCollection, isDynamicCollection, isStaticCollection, type LoadedCollection,
        type StaticCollection
    } from "../../models/collection";
    import {
        Button,
        ComposedModal,
        FluidForm, InlineNotification,
        ModalBody,
        ModalFooter,
        ModalHeader,
        ProgressIndicator,
        ProgressStep,
        RadioButton,
        RadioButtonGroup,
        TextInput, Toggle,
        Tooltip
    } from "carbon-components-svelte";
    import Filter from "../rule/Filter.svelte";
    import type {MultiSelectItem} from "carbon-components-svelte/src/MultiSelect/MultiSelect.svelte";
    import type {Rule, RuleRow} from "../../models/rule";
    import {capitalize} from "../../util/text";
    import {languageName} from "../../util/languages";
    import { v4 as uuidv4 } from 'uuid';
    import {TrashCan} from "carbon-icons-svelte";

    const dispatch = createEventDispatcher();

    type FilterKey = Pick<Rule, "source" | "languages" | "category" | "severity">
    type Filters = { [index in keyof FilterKey]: string[] } & { keyword: string }

    export let open: boolean
    export let editCollection: LoadedCollection<any> | null

    const filter: Filters = {
        source: [],
        languages: [],
        category: [],
        severity: [],
        keyword: "",
    }

    let viewData: ViewData | null = null

    let formStep = 0
    let names: string[] = []
    let type: CollectionType = 'dynamic'
    let name = ''
    let error = ''
    let includeCategoryNull = false
    let rules: RuleRow[] = []

    let sources: MultiSelectItem[] = []
    let categories: MultiSelectItem[] = []
    let languages: MultiSelectItem[] = []
    let severities: MultiSelectItem[] = []
    let matchedRules = 0

    onMount(() => CachedDatabase.instance().viewData.subscribe(async data => {
        viewData = data

        if (data !== null) {
            names = data.collections.map(collection => collection.name)

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
        } else {
            names = []
        }
    }))

    function createCollection(collection: LoadedCollection<any>): DynamicCollection | StaticCollection {
        switch (collection.type as CollectionType) {
            case "dynamic":
                return {
                    id: collection.id,
                    name,
                    type: 'dynamic',
                    languages: filter.languages,
                    sources: filter.source,
                    severities: filter.severity,
                    categories: filter.category,
                    keywords: '',
                }
            case "static":
                return {
                    id: collection.id,
                    name,
                    type: 'static',
                    rules: rules.map(rule => {
                        return {
                            source: rule.source,
                            id: rule.rule_id,
                        }
                    }),
                }
        }
    }

    function doFilter() {
        if (viewData === null || editCollection === null) {
            matchedRules = 0
        } else {
            matchedRules = ViewData.filterRulesForCollection(createCollection(editCollection) as DynamicCollection, viewData.ruleRows).length
        }
    }

    function onOpen() {
        names = []
        type = 'dynamic'
        name = ''
        error = ''

        includeCategoryNull = false
        filter.category = []
        filter.source = []
        filter.severity = []
        filter.languages = []
        filter.keyword = ''
        rules = []

        if (editCollection === null) {
            return
        }
        name = editCollection.name
        type = editCollection.type

        if (isDynamicCollection(editCollection)) {
            filter.category = editCollection.categories
            filter.source = editCollection.sources
            filter.languages = editCollection.languages
            filter.severity = editCollection.severities
            filter.keyword = editCollection.keywords

            doFilter()
        } else if (isStaticCollection(editCollection)) {
            rules = editCollection.resolvedRules
        }

    }

    function remove(rule: RuleRow) {
        rules = rules.filter(r => r.source !== rule.source || r.rule_id !== rule.rule_id)
    }

    async function save() {
        if (editCollection === null) {
            return
        }

        await CachedDatabase.instance().putCollection(createCollection(editCollection))
        open = false
    }

    function close() {
        open = false
    }
</script>

<ComposedModal preventCloseOnClickOutside {...$$restProps} bind:open on:open={() => onOpen()} on:close={() => close()}>
    <ModalHeader label="Collections" title="Edit collection"/>
    <ModalBody hasForm>
        <FluidForm class="dark">
            <RadioButtonGroup bind:selected={type} disabled>
                <div slot="legendText" style:display="flex">
                    Collection Type
                    <Tooltip>
                        <div class="tooltip">
                            <p>
                                <b>Dynamic</b> collections consist of a set of filters and automatically select
                                all rules matching
                                the filters.
                            </p>
                            <p>
                                <b>Static</b> collections only contain manually added rules.
                            </p>
                        </div>
                    </Tooltip>
                </div>
                <RadioButton labelText="Dynamic" value="dynamic"/>
                <RadioButton labelText="Static" value="static"/>
            </RadioButtonGroup>
            <TextInput labelText="Name of the collection*"
                       placeholder="Enter a helpful name for this collection..." bind:value={name}/>
            {#if (type === 'dynamic')}
                <FluidForm class="dark">
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
                </FluidForm>
                <p>
                    Currently matches {matchedRules} rules.
                </p>
            {:else if (type === 'static')}
                <ul class="rule-list">
                    {#each rules as rule}
                        <li class="rule">
                            <div class="text">
                                <h3>{rule.id}</h3>
                                <span class="muted">{rule.source}</span>
                            </div>
                            <div>
                                <Button icon={TrashCan} iconDescription="Delete" tooltipPosition="left" size="small"
                                        on:click={() => remove(rule)} />
                            </div>
                        </li>
                    {/each}
                </ul>
            {/if}
        </FluidForm>
        <InlineNotification class={error === '' ? 'hidden' : ''} hideCloseButton title="Error:" subtitle={error} />
    </ModalBody>
    <ModalFooter>
        <Button on:click={() => open = false} kind="secondary">Cancel</Button>
        <Button on:click={() => save()}>Save</Button>
    </ModalFooter>
</ComposedModal>

<style lang="scss">
  .content {
    padding-top: var(--cds-spacing-06);
  }

  .navigation {
    display: flex;
    justify-content: end;
    margin-top: var(--cds-spacing-04);
  }

  .tooltip {
    i {
      font-style: italic;
    }

    b {
      font-weight: bold;
    }

    p {
      margin-bottom: var(--cds-spacing-03);

      &:last-child {
        margin-bottom: 0;
      }
    }
  }

  .rule-list {
    margin: var(--cds-spacing-06) 0;
    overflow-y: auto;
    overflow-x: hidden;
    min-height: 16rem;

    .rule {
      display: flex;
      flex-direction: row;
      align-items: center;
      margin: var(--cds-spacing-02) 0;
      padding: var(--cds-spacing-02) var(--cds-spacing-04);

      &:hover {
        background-color: var(--cds-ui-background);
      }

      .text {
        flex-grow: 1;

        h3 {
          font-size: var(--cds-productive-heading-02-font-size, 2rem);
          color: var(--cds-text-01);
        }

        span {
          display: block;
          margin-bottom: var(--cds-spacing-01);

          &.muted {
            color: var(--cds-text-03);
          }
        }
      }
    }
  }
</style>