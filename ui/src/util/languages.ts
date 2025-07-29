export type LanguageName =
    "apex"
    | "bash"
    | "c"
    | "cairo"
    | "clojure"
    | "cpp"
    | "csharp"
    | "dart"
    | "dockerfile"
    | "ex"
    | "generic"
    | "go"
    | "html"
    | "java"
    | "js"
    | "json"
    | "jsonnet"
    | "julia"
    | "kt"
    | "lisp"
    | "lua"
    | "ocaml"
    | "php"
    | "python"
    | "r"
    | "ruby"
    | "rust"
    | "scala"
    | "scheme"
    | "solidity"
    | "swift"
    | "tf"
    | "ts"
    | "yaml"
    | "xml"

const LANGUAGES: { [index in LanguageName]: string } = {
    apex: 'Apex',
    bash: 'Bash',
    c: 'C',
    cairo: 'Cairo',
    clojure: 'Clojure',
    cpp: 'C++',
    csharp: 'C#',
    dart: 'Dart',
    dockerfile: 'Dockerfile',
    ex: 'Elixir',
    generic: 'Generic',
    go: 'Go',
    html: 'HTML',
    java: 'Java',
    js: 'JavaScript',
    json: 'JSON',
    jsonnet: 'Jsonnet',
    julia: 'Julia',
    kt: 'Kotlin',
    lisp: 'Lisp',
    lua: 'Lua',
    ocaml: 'OCaml',
    php: 'PHP',
    python: 'Python',
    r: 'R',
    ruby: 'Ruby',
    rust: 'Rust',
    scala: 'Scala',
    scheme: 'Scheme',
    solidity: 'Solidity',
    swift: 'Swift',
    tf: 'Terraform',
    ts: 'TypeScript',
    yaml: 'YAML',
    xml: 'XML',
}

export function languageName(language: string): string {
    if (language.toLowerCase() in LANGUAGES) {
        return LANGUAGES[language.toLowerCase() as LanguageName]
    }
    return language
}