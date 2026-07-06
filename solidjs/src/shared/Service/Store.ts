import { createStore, SetStoreFunction, unwrap } from "solid-js/store";
import { indexdb } from "../indexdb";

export class Stores<model extends { id: number }> {
    public table!: string;
    public store: { data: model[] }
    public setStore: SetStoreFunction<{ data: model[]; }>

    public constructor() {
        [this.store, this.setStore] = createStore({ data: [] as model[] });
    }

    allstate() {
        return this.store.data;
    }

    keyById = () => this.store.data.reduce((acc, item) => {
        acc[item.id] = item;
        return acc;
    }, {} as { [key: string]: model });

    setstate(i: model[]) {
        this.setStore({ data: i });
        indexdb.The_putSomeData(this.table, i);
    }

    upsertstate(i: model[]) {
        if (!i || (i as any) === "Not Found") return;

        let prepare: model[] = unwrap(this.store.data);
        if (prepare.length) {
            indexdb.The_putSomeData(this.table, i);
            i.forEach(element => {
                prepare = prepare.filter(a => a.id !== element.id);
                prepare = [...prepare, element];
            });
            this.setStore({ data: prepare });
        } else {
            this.setStore({ data: i });
            indexdb.The_setData(this.table, i);
        }
    }

    delstate(i: number) {
        indexdb.The_delSomeData(this.table, i);
        this.setStore({ data: unwrap(this.store.data).filter(a => a.id !== i) });
    }

    addstate(i: model) {
        indexdb.The_putSomeData<model>(this.table, [i]);
        this.setStore({ data: [...unwrap(this.store.data), i] });
    }

    updatestate(i: model) {
        indexdb.The_putSomeData<model>(this.table, [i]);
        this.setStore({ data: [...unwrap(this.store.data).filter(a => a.id !== i.id), i] });
    }

    findState(i: number) {
        return this.store.data.find(a => a.id === i);
    }

    getState(i: number, key: any = null) {
        if (key) {
            return unwrap(this.store.data).filter(a => (a as any)[key] === i);
        } else {
            return unwrap(this.store.data).filter(a => a.id === i);
        }
    }
}
