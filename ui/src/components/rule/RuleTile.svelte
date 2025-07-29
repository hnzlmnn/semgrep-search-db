<script lang="ts">

    import {Button, Modal, Tag, Tile, truncate} from "carbon-components-svelte";
    import {AddLarge, DataCategorical, Launch, Maximize, Minimize} from "carbon-icons-svelte";
    import type {RuleRow} from "../../models/rule";
    import LanguageList from "./LanguageList.svelte";
    import {severityColor} from "../../util/severities";
    import {capitalize} from "../../util/text";
    import RuleContent from "./RuleContent.svelte";
    import AddToCollectionModal from "../collection/AddToCollectionModal.svelte";
    import {createEventDispatcher} from "svelte";
    import type {StaticCollection} from "../../models/collection";

    const dispatch = createEventDispatcher();

    export let rule: RuleRow | undefined = undefined
    export let skeleton: boolean = false
    export let expanded = false

    let addRuleToCollectionOpen = false
    let addRuleToCollection: RuleRow | null = null

    function addToCollection() {
        if (rule === undefined) {
            return
        }
        dispatch('add', rule)
    }
</script>

<div class="container">
    <Tile>
        <div class="header">
            <div class="title">
                <h2 class:bx--skeleton__text={skeleton} use:truncate>{rule?.rule_id}</h2>
                <!-- TODO: Make this a link? -->
                <h5>
                    <Tag {skeleton} type={severityColor(rule?.severity)}>{rule?.severity}</Tag>
                    <Tag icon={DataCategorical} {skeleton}>{capitalize(rule?.category ?? "Unknown Category")}</Tag>
                </h5>
            </div>
            <div class="actions">
                <Button disabled={skeleton} icon={expanded ? Minimize : Maximize}
                        iconDescription={expanded ? "Close" : "Expand"}
                        kind="secondary" on:click={() => expanded = !expanded} size="small" tooltipAlignment="end"/>
                {#if rule !== undefined}
                    <Button disabled={skeleton} icon={AddLarge} iconDescription="Add to collection"
                            kind="secondary" size="small" tooltipAlignment="end"
                            on:click={() => addToCollection()}/>
                {/if}
                <Button disabled={skeleton} href={rule?.id} icon={Launch}
                        iconDescription="Open repository"
                        kind="secondary" size="small" target="_blank" tooltipAlignment="end"/>
            </div>
        </div>

        <div class="description">
            <p class:bx--skeleton__text={skeleton} class:bx--text-truncate--end={!expanded}
               class:muted={!rule?.description}>{rule?.description ?? "No description"}</p>
        </div>

        <div class="footer">
            <LanguageList languages={rule?.languages} {skeleton}/>
            <div class="spacer"/>
            <span class="source" class:bx--skeleton__text={skeleton} class:muted={true}>
                by {rule?.repo.name}
            </span>
        </div>

        <RuleContent {expanded} light {rule}/>

    </Tile>
</div>

<!--<Modal-->
<!--        bind:open-->
<!--        modalHeading="Create database"-->
<!--        on:click:button&#45;&#45;secondary={() => (open = false)}-->
<!--        on:close-->
<!--        on:open-->
<!--        on:submit-->
<!--        primaryButtonText="Confirm"-->
<!--        secondaryButtonText="Cancel"-->
<!--&gt;-->
<!--    <p>Create a new Cloudant database in the US South region.</p>-->
<!--</Modal>-->

<style lang="scss">
  .container {
    position: relative;

    .muted {
      color: var(--cds-text-02);
    }

    .header {
      display: flex;
      flex-direction: row;
      margin-bottom: var(--cds-spacing-04);

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

    .description {
      margin-bottom: var(--cds-spacing-04);

      p {
        width: 100%;
        overflow: hidden;
        display: inline-block;
      }
    }

    .footer {
      display: flex;
      flex-direction: row;
      align-items: center;

      & :global(.bx--tag) {
        margin-left: 0;
        margin-right: var(--cds-spacing-02);
      }

      .spacer {
        flex-grow: 1;
      }

    }

  }
</style>