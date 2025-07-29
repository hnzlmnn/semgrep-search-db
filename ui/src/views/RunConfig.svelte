<script lang="ts">
    import ContentWidth from "../components/layout/ContentWidth.svelte";
    import PageTitle from "../components/layout/PageTitle.svelte";
    import {RunConfiguration,} from "../util/runs";
    import {Button, CodeSnippet, Form, TooltipDefinition} from "carbon-components-svelte";
    import {capitalize} from "../util/text";
    import {languageName} from "../util/languages";
    import SelectionGroup from "../components/run/SelectionGroup.svelte";
    import {DocumentImport, Launch} from "carbon-icons-svelte";

    const config = RunConfiguration.fromCode(localStorage.getItem("run-configuration") ?? "")

    let code = ""
    config.code.subscribe(c => {
        code = c
        if (code !== "") {
            localStorage.setItem("run-configuration", code)
        }
    })

    ;(window as any).runConfig = config
    ;(window as any).RunConfiguration = RunConfiguration

    function parseCode() {
        const code = prompt('Please enter the code');
        if (code) {
            config.parse(code);
        }
    }

</script>

<PageTitle text="Run Configuration">
    <Button on:click={parseCode} kind="secondary" icon={DocumentImport} iconDescription="Parse code" tooltipAlignment="end"/>
</PageTitle>
<ContentWidth>
    <p>
        Generate a short run configuration for use with
        <TooltipDefinition align="start">
            <span slot="tooltip">
                <CodeSnippet type="inline">sgs</CodeSnippet> is the CLI component of semgrep-search. It can be used standalone without this UI to search for rules and run semgrep.
            </span>
            sgs
        </TooltipDefinition>
        . When running this configuration, the ruleset will be evaluated using the available database.
    </p>
    <div class="form">
        <Form>
            <SelectionGroup {config} group="categories" textTransformer={capitalize}/>
            <SelectionGroup {config} group="languages" textTransformer={languageName}/>
            <SelectionGroup {config} group="severities"/>
            <SelectionGroup {config} group="features" textTransformer={capitalize}/>
        </Form>
    </div>
    <CodeSnippet {code}/>
</ContentWidth>

<style lang="scss">
  .form {

  }

</style>