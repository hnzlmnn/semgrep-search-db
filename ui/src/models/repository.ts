export interface Repository {
    id: string
    name: string
    license: string
}

export interface GitRepository extends Repository {
    repo: string
    branch: string
    type: string
    url: string
}
