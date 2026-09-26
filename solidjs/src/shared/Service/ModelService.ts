import { indexdb } from "../indexdb";
import { Where } from "../Interface/TheType";
import apiClient from "../../lib/api-client";
import { Stores } from "./Store";

export class ModelService<model extends { id: number, updated_at: Date }> extends Stores<model> {
    public url: string = "";
    public model!: string;
    public run: boolean = false;

    async checkinit() {
        try {
            const i = await indexdb.The_getall<model[]>(this.model);
            if (this.run === false) {
                this.run = true;
                if (i.length > 0) {
                    this.setStore({ data: i as any });
                }
            }
        } catch (error) {
            console.error(`IndexedDB init failed for table '${this.model}':`, error);
            if (this.run === false) {
                this.run = true;
            }
        }
    }

    seTable(table: string) {
        this.table = table;
        this.model = table;
        return this;
    }

    /** Alias for seTable to maintain compatibility */
    setTable(table: string) {
        return this.seTable(table);
    }



    seturl(url: string) {
        this.url = url;
        return this;
    }

    /**
     * REST base for this table. Generated services used to pass "api/<table>" (a relative URL on the
     * frontend host, with no token). Those now map to the signed-in, owner-scoped backend routes
     * /api/v1/islogin/<table>/ (apiClient adds /api/v1 and the Bearer token).
     */
    get base(): string {
        const u = this.url || this.model;
        if (u.startsWith("http") || u.startsWith("/")) return u.endsWith("/") ? u : u + "/";
        const rest = u.replace(/^api\//, "").replace(/\/+$/, "");
        // "api/<table>" -> generated CRUD; "api/soil/health"-style custom paths -> /api/v1/soil/health/
        return /^[a-z_]+$/.test(rest) ? `/islogin/${rest}/` : `/${rest}/`;
    }

    /** Same contract as the old JFetch: resolves to the JSON body, or undefined on failure (logged). */
    private async send<T>(method: "GET" | "POST" | "PUT" | "DELETE", path: string, body?: any): Promise<T | undefined> {
        try {
            const r = method === "GET" ? await apiClient.get<T>(path, { cache: false })
                : method === "POST" ? await apiClient.post<T>(path, body)
                : method === "PUT" ? await apiClient.put<T>(path, body)
                : await apiClient.delete<T>(path);
            return r.data;
        } catch (error) {
            console.error(`${method} ${path} failed for '${this.model}':`, error);
            return undefined;
        }
    }

    async all() {
        if (!this.run) {
            await this.checkinit();
        }
        // The backend has no "changed since" filter, so fetch the (owner-scoped) list each time.
        const req = await this.send<model[]>("GET", this.base);
        if (req && Array.isArray(req)) {
            this.upsertstate(req);
        }
    }

    async create(body: any) {
        const req = await this.send<model>("POST", this.base, body);
        if (req && req.id) {
            this.upsertstate([req]);
        }
        return req as model;
    }

    /** Create or update several rows (rows with an id are updated). */
    async upsert(body: any) {
        const rows: any[] = Array.isArray(body) ? body : [body];
        const saved: model[] = [];
        for (const row of rows) {
            const req = row?.id ? await this.send<model>("PUT", this.base + row.id, row)
                : await this.send<model>("POST", this.base, row);
            if (req && req.id) saved.push(req);
        }
        if (saved.length) {
            this.upsertstate(saved);
        }
    }

    async get(id: number) {
        const req = await this.send<model>("GET", this.base + id);
        if (req && req.id) {
            this.upsertstate([req]);
        }
    }

    async update(i: number, body: any) {
        const req = await this.send<model>("PUT", this.base + (i ?? body?.id), body);
        if (req && req.id) {
            this.updatestate(req);
        }
        return req;
    }

    /** Filter the list: a value matches when equal, or when it is in an array of allowed values. */
    async where(body: Where) {
        const req = await this.send<model[]>("GET", this.base);
        if (req && Array.isArray(req)) {
            const rows = req.filter((row: any) => Object.entries(body).every(([k, v]) =>
                Array.isArray(v) ? (v as any[]).map(String).includes(String(row[k])) : String(row[k]) === String(v)));
            this.upsertstate(rows);
            return rows;
        }
        return [] as model[];
    }

    async del(id: number) {
        const req = await this.send("DELETE", this.base + id);
        if (req) {
            this.delstate(id);
        }
    }

    async bulkImport(body: any) {
        return await this.send("POST", this.base + "bulk_ai_import", body);
    }
}
