import {type AxiosInstance} from "axios";
import axios from "axios";

export default class Client {
    private static readonly REPOSITORY = "hnzlmnn/semgrep-search-db"
    private static readonly TAG = "main"
    private url: string;
    private static _instance: Client

    public static instance(): Client {
        if (this._instance === undefined) {
            this._instance = new Client();
        }
        return this._instance;
    }

    private constructor() {
        this.url = `https://github.com/${Client.REPOSITORY}/releases/download/${Client.TAG}/db.json`
    }

    private async getJson() {
        return fetch(this.url, {
            method: "GET",
            mode: "cors",
            credentials: "omit",
            redirect: "follow",
        }).then(res => {
            if (!res.ok) {
                throw new Error("Could not retrieve data");
            }
            return res.body?.getReader()
        })
    }
}