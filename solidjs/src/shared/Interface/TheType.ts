export type Where = Record<string, string[] | string | number | number[]>;
export interface Login {
    name: string;
    email: string;
    id: number;
    roles: string[];
}
