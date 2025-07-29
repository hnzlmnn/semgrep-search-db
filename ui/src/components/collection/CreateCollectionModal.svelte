<script lang="ts">
    import {createEventDispatcher, onMount} from "svelte";
    import {CachedDatabase, ViewData} from "../../storage/cache";
    import {
        type Collection,
        type CollectionType,
        type DynamicCollection,
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
    import type {Rule} from "../../models/rule";
    import {capitalize} from "../../util/text";
    import {languageName} from "../../util/languages";
    import { v4 as uuidv4 } from 'uuid';

    const dispatch = createEventDispatcher();

    type FilterKey = Pick<Rule, "source" | "languages" | "category" | "severity">
    type Filters = { [index in keyof FilterKey]: string[] } & { keyword: string }

    export let open: boolean

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

    function createCollection(id: string): DynamicCollection | StaticCollection {
        switch (type) {
            case "dynamic":
                return {
                    id,
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
                    id,
                    name,
                    type: 'static',
                    rules: [],
                }
        }
    }

    function doFilter() {
        if (viewData === null) {
            matchedRules = 0
        } else {
            matchedRules = ViewData.filterRulesForCollection(createCollection('') as DynamicCollection, viewData.ruleRows).length
        }
    }

    function create(collection: Collection<any>) {
        dispatch('add', collection)
    }

    async function nextStep() {
        error = ''
        if (formStep === 0) {
            if (name.length === 0) {
                error = 'Missing name'
            }
            if (names.includes(name)) {
                error = `A collection with name "${name}" already exists`
            }
        }
        if (error !== '') {
            return
        }

        if (formStep === 0 && type === 'dynamic') {
            doFilter()
        }

        if (formStep === 1) {
            await CachedDatabase.instance().putCollection(createCollection(uuidv4()))
        }

        formStep += 1
    }

    function close() {
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

        open = false
    }
</script>

<ComposedModal preventCloseOnClickOutside {...$$restProps} bind:open on:close={() => close()}>
    <ModalHeader label="Collections" title="Create a new collection"/>
    <ModalBody hasForm>
        <ProgressIndicator bind:currentIndex={formStep} spaceEqually preventChangeOnClick>
            <ProgressStep complete={formStep > 0} invalid={formStep === 0 && error !== ''} label="Basics"/>
            <ProgressStep complete={formStep > 1} invalid={formStep === 1 && error !== ''} label="Select rules"/>
        </ProgressIndicator>
        <div class="content">
            {#if formStep === 0}
                <FluidForm class="dark">
                    <RadioButtonGroup bind:selected={type}>
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
                </FluidForm>
            {:else if formStep === 1}
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
                {:else}
                    <p>Once this rule is created, you can add rules manually.</p>
                {/if}
            {:else if formStep === 2}
                <InlineNotification kind="success" hideCloseButton title="Success" subtitle="The collection was successfully created" />
            {/if}
            <InlineNotification class={error === '' ? 'hidden' : ''} hideCloseButton title="Error:" subtitle={error} />
        </div>
    </ModalBody>
    <ModalFooter>
        {#if formStep < 2}
            <Button on:click={() => formStep = Math.max(0, formStep - 1)} kind="secondary">Back</Button>
            <Button on:click={() => nextStep()}>{formStep < 1 ? 'Next' : 'Create'}</Button>
        {:else}
            <Button on:click={() => close()}>Close</Button>
        {/if}
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
</style>