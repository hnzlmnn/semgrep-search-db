import './app.scss'
import App from './App.svelte'
import {Database} from "./storage/database";
import {loading} from "./storage/uistate";

const app = new App({
  target: document.getElementById('app')!,
})

export default app
