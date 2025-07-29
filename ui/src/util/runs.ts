import type {LanguageName} from "./languages";
import base from "base-x";
import {derived, get, type Readable, readonly, writable, type Writable} from "svelte/store";

export type Enum<T extends string> = { [key in T]: number }
export type NullableEnum<T extends string> = Enum<T> & { null: number }
export type EnumNames<T extends Enum<any>> = Extract<keyof T, string>;
export type EnumValue<T extends Enum<any>> = T[keyof T];


export class BitFlag<T extends Enum<any>> {
    private bits: Set<number> = new Set()

    private constructor(private values: T, bits: number[] = [], public readonly flagStore: Writable<Array<{ value: EnumNames<T>, set: boolean }>>, private notifier?: (group: BitFlag<T>) => void) {
        this.setFromBits(bits)
    }

    private onUpdate() {
        this.flagStore.set(this.getFlags())
        this.notifier && this.notifier(this)
        return this
    }

    public static fromBits<T extends Enum<any>>(values: T, bits: number[], notifier?: (group: BitFlag<T>) => void) {
        return new BitFlag(values, bits, writable([]), notifier)
    }

    public static empty<T extends Enum<any>>(values: T, notifier?: (group: BitFlag<T>) => void) {
        return this.fromBits(values, [], notifier)
    }

    public reload(bits: number[]) {
        return new BitFlag(this.values, bits, this.flagStore, this.notifier).onUpdate()
    }

    public isSet(flag: EnumNames<T>): boolean {
        return this.bits.has(this.values[flag])
    }

    public set(flag: EnumNames<T>) {
        this.bits.add(this.values[flag])
        this.onUpdate()
    }

    public unset(flag: EnumNames<T>) {
        this.bits.delete(this.values[flag])
        this.onUpdate()
    }

    public getSetFlags(): string[] {
        const setFlags: string[] = []
        for (const key in this.values) {
            if (this.bits.has(this.values[key])) {
                setFlags.push(key)
            }
        }
        return setFlags
    }

    public getFlags(): Array<{ value: EnumNames<T>, set: boolean }> {
        const flags: Array<{ value: EnumNames<T>, set: boolean }> = []
        for (const key in this.values) {
            flags.push({
                value: key,
                set: this.isSet(key),
            })
        }
        return flags
    }

    public toBytes(trim = false): number[] {
        const bytes: number[] = []
        const numBytes = this.numBytes(trim)

        for (let i = 0; i < numBytes; i++) {
            // Last byte must not set the continue bit
            let byte = (i < numBytes - 1) ? BitMapper.CONTINUE_BIT : 0
            for (let j = i * 7; j < (i + 1) * 7; j++) {
                if (this.bits.has(j)) {
                    // Set the bit from LSB
                    byte += 1 << (j - (i * 7))
                }
            }
            bytes.push(byte)
        }

        return bytes
    }

    private numBytes(trim: boolean): number {
        return Math.max(1, Math.ceil(this.maxValue(trim) / 7))
    }

    private maxValue(trim: boolean): number {
        if (trim) {
            return Math.max(...this.bits)
        }

        let max = -1

        for (const key in this.values) {
            const value = this.values[key]
            if (value > max) {
                max = value
            }
        }

        return max
    }

    private setFromBits(bits: number[]) {
        this.bits = new Set(bits)
        return this
    }
}


class BitMapper {
    public static readonly CONTINUE_BIT = 1 << 7

    public static group(bytes: Uint8Array) {
        const groups: number[][] = []
        let currentGroup: number[] = []
        for (let i = 0; i < bytes.length; i++) {
            const byte = bytes[i]
            currentGroup.push(byte)
            if ((byte & BitMapper.CONTINUE_BIT) === 0) {
                groups.push(currentGroup)
                currentGroup = []
            }
        }
        if (currentGroup.length > 0) {
            groups.push(currentGroup)
        }
        return groups
    }

    public static getSetBits(group: number[]) {
        const bits: number[] = []

        // Extract the 7 LSB from the byte
        for (let g = 0; g < group.length; g++) {
            const byte = group[g]
            for (let i = 0; i < 7; i++) {
                if (BitMapper.bitSet(byte, i)) {
                    // We use 7 bits of each byte, thus the first (LSB) bit of the second byte is number 8
                    bits.push(i + g * 7)
                }
            }
        }

        return bits
    }

    private static bitSet(byte: number, i: number): boolean {
        return i < 8 && ((byte & (1 << i)) === (1 << i))
    }

    public static toBytes(flags: BitFlag<any>[]): number[] {
        return flags.map(flag => flag.toBytes()).flat()
    }

}

export type KnownCategory = "best-practice" | "correctness" | "maintainability" | "performance" | "portability" | "security"
export type KnownLanguage = LanguageName
export type KnownSeverity = "INVENTORY" | "INFO" | "WARNING" | "ERROR"
export type KnownFeature = "export_text" | "export_sarif" | "export_json"

const CategoryMapping: NullableEnum<KnownCategory> = {
    null: 0,
    "best-practice": 1,
    correctness: 2,
    maintainability: 3,
    performance: 4,
    portability: 5,
    security: 6,
}

const LanguageMapping: Enum<KnownLanguage> = {
    apex: 0,
    bash: 1,
    c: 2,
    cairo: 3,
    clojure: 4,
    cpp: 5,
    csharp: 6,
    dart: 7,
    dockerfile: 8,
    ex: 9,
    generic: 10,
    go: 11,
    html: 12,
    java: 13,
    js: 14,
    json: 15,
    jsonnet: 16,
    julia: 17,
    kt: 18,
    lisp: 19,
    lua: 20,
    ocaml: 21,
    php: 22,
    python: 23,
    r: 24,
    ruby: 25,
    rust: 26,
    scala: 27,
    scheme: 28,
    solidity: 29,
    swift: 30,
    tf: 31,
    ts: 32,
    yaml: 33,
    xml: 34,
}

const SeverityMapping: NullableEnum<KnownSeverity> = {
    null: 0,
    INVENTORY: 1,
    INFO: 2,
    WARNING: 3,
    ERROR: 4,
}

// TODO: Heavy work in progress
const FeatureMapping: Enum<KnownFeature> = {
    export_text: 0,
    export_sarif: 1,
    export_json: 2,
}

export type Pick<T, V> = {[k in keyof T as T[k] extends V ? k : never]: T[k] };
export type AllConfigurationGroups = Pick<RunConfiguration, BitFlag<any>>
export type ConfigurationGroupName = keyof AllConfigurationGroups
export type ConfigurationGroup<T extends ConfigurationGroupName> = RunConfiguration[T]
export type ConfigurationFlag<T extends ConfigurationGroupName> = ConfigurationGroup<T> extends BitFlag<infer F> ? F : never
export type ConfigurationFlagName<T extends ConfigurationGroupName> = keyof ConfigurationFlag<T>

export class RunConfiguration {
    private readonly _code: Writable<string>
    public readonly code: Readable<string>
    public categories: BitFlag<typeof CategoryMapping> = BitFlag.empty(CategoryMapping, () => {
        this._code.set(this.calculate())
    })
    public languages: BitFlag<typeof LanguageMapping> = BitFlag.empty(LanguageMapping, () => {
        this._code.set(this.calculate())
    })
    public severities: BitFlag<typeof SeverityMapping> = BitFlag.empty(SeverityMapping, () => {
        this._code.set(this.calculate())
    })
    public features: BitFlag<typeof FeatureMapping> = BitFlag.empty(FeatureMapping, () => {
        this._code.set(this.calculate())
    })
    

    private readonly order: Array<ConfigurationGroupName> = [
        'categories',
        'languages',
        'severities',
        'features',
    ]

    private static readonly base58 = base('123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz')

    constructor(config: Uint8Array, private trim = false) {
        this._code = writable(this.calculate())
        this.code = readonly(this._code)
        this.setConfig(config)
    }

    public setConfig(config: Uint8Array) {
        const groups = BitMapper.group(config)

        for (let i = 0; i < this.order.length && i < groups.length; i++) {
            const k = this.order[i]
            // @ts-ignore
            this[k] = this[k].reload(BitMapper.getSetBits(groups[i]))
        }
    }

    public static fromCode(code: string) {
        return new RunConfiguration(RunConfiguration.base58.decode(code))
    }

    public calculate(trim = this.trim): string {
        const bytes = this.order.map(k => this[k]).map(flag => flag.toBytes(trim)).flat()

        let trimmed = bytes
        if (trim) {
            const trimmed_reversed = []
            for (const byte of bytes.reverse()) {
                if (byte === 0 && trimmed_reversed.length === 0) {
                    continue
                }
                trimmed_reversed.push(byte)
            }
            trimmed = trimmed_reversed.reverse()
        }

        return RunConfiguration.base58.encode(trimmed)
    }

    public parse(code: string) {
        const config = RunConfiguration.base58.decode(code)
        this.setConfig(config)
        this._code.set(this.calculate())
    }


}

// export enum