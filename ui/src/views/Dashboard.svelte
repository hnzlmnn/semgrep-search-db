<script lang="ts">
    import {Button, Column, Grid, Link, Row, Tile} from "carbon-components-svelte";
    import PageTitle from "../components/layout/PageTitle.svelte";
    import Widget from "../components/dashboard/Widget.svelte";
    import {ContainerRegistry, DataBase, Favorite, Information, Rule, Time, Timer} from "carbon-icons-svelte";
    import {CachedDatabase, ViewData} from "../storage/cache";
    import {GaugeChart} from "@carbon/charts-svelte";
    import {parseDate} from "../util/date";
    import {DateTime} from "luxon";

    let viewData: ViewData | null = null
    let createdOnExact: string = ''
    let createdOn: string = ''

    CachedDatabase.instance().viewData.subscribe(data => {
        viewData = data
        if (data !== null) {
            const date = parseDate(data.meta.created_on)
            createdOnExact = date.toRFC2822() as string
            const age = DateTime.now().diff(date).shiftTo("days", "hours","minutes","seconds")
            if (age.days > 0) {
                createdOn = `${age.days} days ago`
            } else if (age.hours > 0) {
                createdOn = `${age.hours} hours ago`
            } else if (age.minutes > 0) {
                createdOn = `${age.minutes} minutes ago`
            } else {
                createdOn = `${age.seconds} seconds ago`
            }
        }
    })

    $: skeleton = viewData === null
</script>


<PageTitle text="Dashboard">
    <Button>Action</Button>
</PageTitle>
<div class="wrapper content--max-width">
    <div class="grid">
        <Widget title="Database Info">
            <div class="stat">
                <h5>Created</h5>
                <h2 class:bx--skeleton__text={skeleton} title={createdOnExact}>{createdOn}</h2>
                <span class="icon" style="color: var(--cds-support-02)"><Time size={32} /></span>
            </div>
        </Widget>
        <Widget title="Total Rules">
            <div class="stat">
                <h2 class:bx--skeleton__text={skeleton}>{viewData?.ruleRows.length ?? 0}</h2>
                <span class="icon" style="color: var(--cds-support-02)"><Rule size={32} /></span>
            </div>
        </Widget>
        <Widget title="Total Sources">
            <div class="stat">
                <h2 class:bx--skeleton__text={skeleton}>{viewData?.repos.size ?? 0}</h2>
                <span class="icon" style="color: var(--cds-support-02)"><ContainerRegistry size={32} /></span>
            </div>
        </Widget>
        <Widget title="Number of Collections">
            <div class="stat">
                <h2 class:bx--skeleton__text={skeleton}>{viewData?.collections.length ?? 0}</h2>
                <span class="icon" style="color: var(--cds-support-02)"><Favorite size={32} /></span>
            </div>
        </Widget>
    </div>
</div>
<Grid>
    <Row>
        <Column>


        </Column>
    </Row>
</Grid>

<style lang="scss" global>
  $spacing: .6rem;

  .wrapper {

    .grid {
      display: flex;
      flex-wrap: wrap;
      justify-content: start;
      margin: 0 calc(-1 * $spacing);

      & > :global(.widget.bx--aspect-ratio.bx--aspect-ratio--1x1) {
        width: 25%;
        max-width: 25%;
        overflow: hidden;
        @media screen and (max-width: 820px) {
          width: 50%;
          max-width: 50%;
        }
        @media screen and (max-width: 600px) {
          width: 100%;
          max-width: 100%;
        }
      }

      & > :global(.widget.bx--aspect-ratio.bx--aspect-ratio--2x1) {
        width: 50%;
        max-width: 50%;
        overflow: hidden;
        @media screen and (max-width: 820px) {
          width: 100%;
          max-width: 100%;
        }
      }

      & > :global(.widget.bx--aspect-ratio > .bx--aspect-ratio--object) {
        top: $spacing;
        left: $spacing;
        width: calc(100% - 2 * #{$spacing});
        height: calc(100% - 2 * #{$spacing});
        overflow: hidden;
      }
    }
  }

  .stat {
    width: 100%;

    padding: var(--cds-spacing-04);
    position: relative;

    h5 {
      color: var(--cds-text-02);
      margin-bottom: var(--cds-spacing-04);
    }

    .icon {
      position: absolute;
      top: calc(var(--cds-spacing-04) + var(--cds-productive-heading-05-font-size, 2rem) / 2 - 16px);
      right: calc(var(--cds-spacing-04));
    }

    &:has(h5) {
      .icon {
        top: calc(var(--cds-spacing-04) + var(--cds-productive-heading-02-font-size, 1rem) / 2 - 16px);
      }
    }
  }
</style>