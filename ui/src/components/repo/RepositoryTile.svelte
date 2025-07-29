<script lang="ts">

    import {Button, Tile} from "carbon-components-svelte";
    import type {GitRepository, Repository} from "../../models/repository";
    import {Launch, Rule, Translate} from "carbon-icons-svelte";
    import type {RepositoryStats} from "../../util/statistics";

    export let repo: Repository | GitRepository | undefined = undefined
    export let stats: RepositoryStats | undefined = undefined
    export let skeleton: boolean = false

    function isGit(repo: Repository | GitRepository | undefined): repo is GitRepository {
        return repo !== undefined && ["GitHub", "GitLab"].includes((repo as GitRepository).type ?? "")
    }
</script>

<div class="container">
    <Tile>
        <h2 class:bx--skeleton__text={skeleton}>{repo?.name}</h2>
        <h5 class:bx--skeleton__text={skeleton}>{repo?.id}</h5>

        {#if isGit(repo)}
            <div class="link">
                <Button kind="secondary" icon={Launch} iconDescription="Open repository" tooltipAlignment="end" href={repo.url} target="_blank"/>
            </div>
        {/if}

        <div class="stats">
            {#if stats !== undefined || skeleton}
                <div class="stat">
                    <Tile light>
                        <h5># Rules</h5>
                        <h2 class:bx--skeleton__text={skeleton}>{stats?.numRules}</h2>
                        <span class="icon" style="color: var(--cds-support-02)"><Rule size={32} /></span>
                    </Tile>
                </div>
                <div class="stat">
                    <Tile light>
                        <h5># Languages</h5>
                        <h2 class:bx--skeleton__text={skeleton}>{[...(stats?.languages?.keys() ?? [])].length}</h2>
                        <span class="icon" style="color: var(--cds-support-04)"><Translate size={32} /></span>
                    </Tile>
                </div>
            {/if}
        </div>

        <div class="footer">
            <!-- TODO: Add commit ID/last updated -->
            <div class="spacer"/>
            <span class="license" class:bx--skeleton__text={skeleton} class:muted={repo?.license === null}>
                {repo?.license ?? "Unknown"}
            </span>
        </div>
    </Tile>
</div>

<style lang="scss">
  .container {
    position: relative;

    h2 {
      font-size: var(--cds-productive-heading-04-font-size, 2rem);
    }

    h5 {
      margin-top: .2rem;
      color: var(--cds-text-03);
    }

    .link {
      position: absolute;
      right: 0;
      top: 0;
    }

    .stats {
      display: flex;
      flex-direction: row;
      flex-wrap: wrap;
      margin: var(--cds-spacing-04) 0;

      .stat {
        width: 50%;
        @media screen and (max-width: 520px) {
          width: 100%;
        }

        padding: var(--cds-spacing-04);
        position: relative;

        h5 {
          color: var(--cds-text-02);
          margin-bottom: var(--cds-spacing-04);
        }

        .icon {
          position: absolute;
          top: calc(var(--cds-spacing-04) + var(--cds-spacing-05));
          right: calc(var(--cds-spacing-04) + var(--cds-spacing-05));
        }
      }
    }

    .footer {
      display: flex;
      flex-direction: row;

      .spacer {
        flex-grow: 1;
      }

      .source {
        &.muted {
          color: var(--cds-text-03);
        }
      }
    }
  }
</style>