<script lang="ts">
    import {
        Content,
        Header,
        HeaderGlobalAction,
        HeaderUtilities,
        SideNav,
        SkipToContent
    } from "carbon-components-svelte";
    import {
        Asleep,
        Awake, BrightnessContrast, ContainerRegistry,
        Dashboard,
        DocumentConfiguration,
        Favorite,
        Light, LogoGithub,
        RuleDataQuality
    } from "carbon-icons-svelte";
    import Router, {location} from "svelte-spa-router";
    import {routes} from "./routes";
    import {nextTheme, sideBarOpen, type Theme, theme} from "./storage/uistate";
    import Nav from "./components/menu/Nav.svelte";
    import Item from "./components/menu/Item.svelte";
    import {Database} from "./storage/database";
    import {onMount} from "svelte";

    location.subscribe(loc => {
        console.log(loc)
    })

    onMount(async () => {
        (window as any).db = await Database.create()
    })

    theme.subscribe(theme => {
        if (theme === null) {
            document.documentElement.removeAttribute("theme")
        } else {
            document.documentElement.setAttribute("theme", theme)
        }
    })

    function toggleTheme(e: Event) {
        nextTheme()
        if (e.currentTarget && 'blur' in e.currentTarget) {
            (e.currentTarget as any).blur()
        }
    }

    function getThemeIcon(theme: Theme): any {
        switch (theme) {
            case "dark":
                return Asleep
            case "light":
                return Light
            case null:
                return BrightnessContrast
        }
    }

    $: themeIcon = getThemeIcon($theme)

</script>

<Header bind:isSideNavOpen={$sideBarOpen} company="Semgrep" expandedByDefault={false} platformName="Search">
    <svelte:fragment slot="skip-to-content">
        <SkipToContent/>
    </svelte:fragment>
    <Nav kind="header">
        <Item activeCheck={loc => loc === '/'} href="/" icon={Dashboard} text="Dashboard"/>
        <Item activeCheck={loc => loc.startsWith('/rules')} href="/rules" icon={RuleDataQuality} text="Rules"/>
        <Item activeCheck={loc => loc.startsWith('/repositories')} href="/repositories" icon={ContainerRegistry}
              text="Sources"/>
        <Item activeCheck={loc => loc.startsWith('/collections')} href="/collections" icon={Favorite}
              text="Collections"/>
        <Item activeCheck={loc => loc.startsWith('/generator')} href="/generator" icon={DocumentConfiguration}
              text="Run Configuration"/>
    </Nav>
    <HeaderUtilities>
        <HeaderGlobalAction
                icon={LogoGithub}
                iconDescription="GitHub"
                href="https://github.com/hnzlmnn/semgrep-search"
                target="_blank"
                tooltipAlignment="end"
        />
        <HeaderGlobalAction
                icon={themeIcon}
                iconDescription="Toggle theme"
                on:click={toggleTheme}
                tooltipAlignment="end"
        />
    </HeaderUtilities>
</Header>

<SideNav bind:isOpen={$sideBarOpen}>
    <Nav kind="sidebar">
        <Item activeCheck={loc => loc === '/'} href="/" icon={Dashboard} text="Dashboard"/>
        <Item activeCheck={loc => loc.startsWith('/rules')} href="/rules" icon={RuleDataQuality} text="Rules"/>
        <Item activeCheck={loc => loc.startsWith('/repositories')} href="/repositories" icon={ContainerRegistry}
              text="Sources"/>
        <Item activeCheck={loc => loc.startsWith('/collections')} href="/collections" icon={Favorite}
              text="Collections"/>
        <Item activeCheck={loc => loc.startsWith('/generator')} href="/generator" icon={DocumentConfiguration}
              text="Run Configuration"/>
    </Nav>
</SideNav>

<Content>
    <Router {routes}/>
</Content>

<style lang="scss">
  :global(.bx--content) {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    min-height: 0;
    position: relative;
  }
</style>