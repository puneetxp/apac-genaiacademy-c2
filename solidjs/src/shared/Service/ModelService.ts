import { indexdb } from "../indexdb";
import { Where } from "../Interface/TheType";
import { JFetch, JGetFetch } from "../thelib";
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

    async all() {
        if (!this.run) {
            await this.checkinit();
            await this.all();
        } else {
            const r = this.allstate();
            if (r.length === 0) {
                const req: model[] = await JFetch(this.url);
                if (req && Array.isArray(req)) {
                    this.upsertstate(req);
                }
            } else {
                const sort = [...r].sort((x, y) =>
                    new Date(x.updated_at) < new Date(y.updated_at) ? 1 : -1
                );
                const latest = new Date((sort[0] as any).updated_at);
                if (isNaN(latest.getTime())) {
                    const req: model[] = await JFetch(this.url);
                    if (req && Array.isArray(req)) {
                        this.upsertstate(req);
                    }
                } else {
                    // sv-SE gives YYYY-MM-DD HH:mm:ss which is usually good for backends
                    const req: model[] = await JGetFetch(this.url, { 'latest': latest.toLocaleString("sv-SE") });
                    if (req && Array.isArray(req)) {
                        this.upsertstate(req);
                    }
                }
            }
        }
    }

    async create(body: any) {
        const req: model = await JFetch(this.url, {
            method: 'POST',
            body: JSON.stringify(body),
        });
        if (req && req.id) {
            this.upsertstate([req]);
        }
        return req;
    }

    async upsert(body: any) {
        const req: model[] = await JFetch(this.url, {
            method: 'PUT',
            body: JSON.stringify(body),
        });
        if (req && Array.isArray(req)) {
            this.upsertstate(req);
        }
    }

    async get(id: number) {
        const req: model = await JFetch(this.url + id);
        if (req && req.id) {
            this.upsertstate([req]);
        }
    }

    async update(i: number, body: any) {
        const req: model = await JFetch(this.url, {
            method: 'PUT',
            body: JSON.stringify(body),
        });
        if (req && req.id) {
            this.updatestate(req);
        }
    }

    async where(body: Where) {
        const req: model[] = await JFetch(this.url, {
            method: 'WHERE',
            body: JSON.stringify(body),
        });
        if (req && Array.isArray(req)) {
            this.upsertstate(req);
        }
    }

    async del(id: number) {
        const req = await JFetch(this.url + id, {
            method: 'DELETE'
        });
        if (req) {
            this.delstate(id);
        }
    }

    async bulkImport(body: any) {
        return await JFetch(this.url + "/bulk_ai_import", {
            method: 'POST',
            body: JSON.stringify(body),
        });
    }
}
