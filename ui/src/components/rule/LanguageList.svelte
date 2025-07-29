<script lang="ts">
    import {Tag} from "carbon-components-svelte";
    import {languageName} from "../../util/languages";

    export let languages: string[] | undefined
    export let skeleton = false

    const skeletalData: string[] = [...new Array(5)].map(() => "")
</script>

<div>
    {#each (skeleton ? skeletalData : (languages ?? [])) as language}
        <Tag {skeleton}>{languageName(language)}</Tag>
    {/each}
</div>