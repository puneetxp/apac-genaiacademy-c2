import { tables } from "./run";

let dbName: string = "rural_farming_db";

export type UseStore = <T>(
    txMode: IDBTransactionMode,
    callback: (store: IDBObjectStore) => T | PromiseLike<T>
) => Promise<T>;

class IndexedDBService {
    dbVersion = 0;
    tables: string[] = tables;
    private initPromise: Promise<IDBDatabase> | null = null;

    private async ensureDatabase(): Promise<IDBDatabase> {
        if (this.initPromise) {
            return this.initPromise;
        }

        this.initPromise = new Promise((resolve, reject) => {
            const request = this.dbVersion > 0
                ? indexedDB.open(dbName, this.dbVersion)
                : indexedDB.open(dbName);

            request.onerror = () => {
                const error = request.error;
                if (error && (error.name === "VersionError" || (error.message && error.message.indexOf("higher version") !== -1))) {
                    const deleteRequest = indexedDB.deleteDatabase(dbName);
                    deleteRequest.onsuccess = () => {
                        this.initPromise = null;
                        this.dbVersion = 0;
                        resolve(this.ensureDatabase());
                    };
                    deleteRequest.onerror = () => reject(error);
                } else {
                    reject(error);
                }
            };

            request.onsuccess = () => {
                const db = request.result;
                if (!this.dbVersion) {
                    this.dbVersion = db.version || 1;
                }

                const missingStores = this.tables.filter(table => !db.objectStoreNames.contains(table));
                if (missingStores.length > 0) {
                    const nextVersion = (db.version || this.dbVersion || 0) + 1;
                    db.close();
                    this.dbVersion = nextVersion;
                    this.initPromise = null;
                    resolve(this.ensureDatabase());
                } else {
                    resolve(db);
                }
            };

            request.onupgradeneeded = () => {
                const db = request.result;
                this.init(db, this.tables);
            };
        });

        return this.initPromise;
    }

    async The_putSomeData<T>(table: string, data: T | T[]) {
        const payload = Array.isArray(data) ? data : [data];
        if (!payload.length) return;

        try {
            const db = await this.ensureDatabase();
            const tx = db.transaction(table, 'readwrite');
            const store = tx.objectStore(table);

            payload.forEach((element) => {
                store.put(element);
            });

            await this.promisifyRequest(tx);
        } catch (error) {
            console.error(`[IndexedDB] Error putting data into '${table}':`, error);
            throw error;
        }
    }

    async The_delSomeData(table: string, del: string | number) {
        try {
            const db = await this.ensureDatabase();
            const tx = db.transaction(table, 'readwrite');
            const store = tx.objectStore(table);
            store.delete(del);
            await this.promisifyRequest(tx);
        } catch (error) {
            console.error('Error deleting data:', error);
            throw error;
        }
    }

    async The_getAllData(table: string, callback: (value: any) => void) {
        try {
            const db = await this.ensureDatabase();
            const tx = db.transaction(table, 'readonly');
            const store = tx.objectStore(table);
            const request = store.getAll();

            request.onsuccess = () => {
                callback(request.result);
            };

            request.onerror = () => {
                throw request.error;
            };
        } catch (error) {
            console.error('Error getting all data:', error);
            throw error;
        }
    }

    promisifyRequest<T = undefined>(
        request: IDBRequest<T> | IDBTransaction | any
    ): Promise<T> {
        return new Promise<T>((resolve, reject) => {
            const resolveValue = () => {
                if ('result' in request) {
                    resolve(request.result as T);
                } else {
                    resolve(undefined as T);
                }
            };
            const rejectValue = () => reject(request.error);

            request.oncomplete = request.onsuccess = resolveValue;
            request.onabort = request.onerror = rejectValue;
        });
    }

    getTable(table: string): UseStore {
        return async (txMode, callback) => {
            const db = await this.ensureDatabase();
            const tx = db.transaction(table, txMode);
            const store = tx.objectStore(table);
            const result = await callback(store);
            await this.promisifyRequest(tx);
            return result;
        };
    }

    async The_getall<T>(table: string): Promise<T> {
        const t = this.getTable(table);
        return t('readonly', (store) => this.promisifyRequest(store.getAll()));
    }

    async The_get(table: string, where: string | number) {
        const t = this.getTable(table);
        return t('readonly', async (store) => this.promisifyRequest(store.get(where)));
    }

    async The_clearobject(table: string) {
        const db = await this.ensureDatabase();
        const tx = db.transaction(table, 'readwrite');
        const store = tx.objectStore(table);
        store.clear();
        await this.promisifyRequest(tx);
    }

    The_clearData() {
        return new Promise<void>((resolve, reject) => {
            const deleteRequest = indexedDB.deleteDatabase(dbName);
            deleteRequest.onsuccess = () => {
                this.initPromise = null;
                this.dbVersion = 0;
                resolve();
            };
            deleteRequest.onerror = () => reject(deleteRequest.error);
        });
    }

    async The_setData(table: string, data: any) {
        await this.The_clearobject(table);
        await this.The_putSomeData(table, data);
    }

    init(db: IDBDatabase, tableList: Array<string>) {
        tableList.forEach((element) => {
            if (!db.objectStoreNames.contains(element)) {
                db.createObjectStore(element, { keyPath: 'id' });
            }
        });
    }
}

export const indexdb = new IndexedDBService();
