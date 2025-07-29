<script lang="ts">
    import {FluidForm, RadioButton, RadioButtonGroup, TextInput, Tooltip} from "carbon-components-svelte";

    let name = ''
    let type = 'dynamic'
</script>

<FluidForm>
    <TextInput bind:value={name} labelText="Name" placeholder="Enter a name for the collection..." required/>
    <RadioButtonGroup bind:selected={type}>
        <div slot="legendText" style:display="flex">
            Collection Type
            <Tooltip>
                <p>
                    <b>Dynamic</b> collections consist of a set of filters and automatically select all rules matching
                    the filters.
                </p>
                <p>
                    <b>Static</b> collections only contain manually added rules.
                </p>
            </Tooltip>
        </div>
        <RadioButton labelText="Dynamic" value="dynamic"/>
        <RadioButton labelText="Static" value="static"/>
    </RadioButtonGroup>
</FluidForm>

<style lang="scss">
  i {
    font-style: italic;
  }

  b {
    font-weight: bold;
  }

  p {
    margin-bottom: var(--cds-spacing-03);
  }
</style>