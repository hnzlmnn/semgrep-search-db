<script lang="ts">

import {capitalize} from "../../util/text";
import {Checkbox, FormGroup} from "carbon-components-svelte";
import {
    BitFlag, type ConfigurationFlagName,
    type ConfigurationGroup,
    type ConfigurationGroupName,
    type EnumNames,
    type RunConfiguration
} from "../../util/runs";

export let config: RunConfiguration
export let group: ConfigurationGroupName
export let title: string = capitalize(group)
export let textTransformer: (value: EnumNames<ConfigurationGroup<any>>) => string = value => value

function updateCheckbox<T extends ConfigurationGroupName>(group: T, flag: ConfigurationFlagName<T>) {
    return (e: CustomEvent<boolean>) => {
        const g = config[group]
        if (e.detail) {
            g.set(flag as never)
        } else {
            g.unset(flag as never)
        }
    }
}

const flagStore = config[group].flagStore
</script>

<div class="group">
    <h4>{title}</h4>
    <FormGroup>

        {#each $flagStore as {value, set: isSet}}
            <Checkbox labelText={textTransformer(value)} checked={isSet}
                      on:check={updateCheckbox(group, value)}/>
        {/each}
    </FormGroup>
</div>

<style lang="scss">
  .group {
    h4 {
      font-size: var(--cds-productive-heading-03-font-size, 1.25rem);
      margin-top: var(--cds-spacing-04);
    }

    & :global(.bx--fieldset) {
      display: flex;
      flex-wrap: wrap;
      margin-top: var(--cds-spacing-04);

      & :global(.bx--form-item) {
        min-width: 10rem;
        flex-grow: 0;
        padding: 0 var(--cds-spacing-04, 1rem);
        padding: 0;

        & :global(.bx--checkbox-label-text) {
          white-space: nowrap;
        }
      }
    }
  }
</style>