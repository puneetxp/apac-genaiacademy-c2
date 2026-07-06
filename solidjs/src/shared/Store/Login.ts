import { createStore } from "solid-js/store";
import { Login } from "../Interface/TheType";
import { Farm } from "../Interface/Model/Farm";
import { FarmService } from "../Service";
import { JFetch } from "../thelib";
import { setactivefarm } from "./Active_Farm";

interface LoginStateModel {
    login: null | Login;
}

const local = localStorage.getItem("login");
let intialstate = null;
if (local && local.trim() !== "") {
    try {
        intialstate = JSON.parse(local);
    } catch (error) {
        console.warn("Failed to parse login from localStorage:", error);
        localStorage.removeItem("login"); // Clear invalid data
        intialstate = null;
    }
}

const [state, set] = createStore<LoginStateModel>({ login: intialstate });
let inflightFarms: Promise<Farm[] | undefined> | null = null;

const fetchFarmsOnce = async (): Promise<Farm[]> => {
    if (!inflightFarms) {
        inflightFarms = JFetch("/api/farm").finally(() => {
            inflightFarms = null;
        });
    }
    const farms = await inflightFarms;
    return Array.isArray(farms) ? farms : [];
};

export class LoginStore {
    static get() {
        return state;
    }
    static async set(i: Login | false | string) {
        if (typeof i != "string" && i != false) {
            set({ login: i });
            let farms = FarmService.allstate();
            if (!farms.length) {
                farms = await fetchFarmsOnce();
                farms.length && FarmService.setstate(farms);
            }
            farms.length && setactivefarm(farms[0]);
            localStorage.setItem("login", JSON.stringify(i));
        } else {
            set({ login: null });
            FarmService.setstate([]);
            setactivefarm(false);
        }
    }
}
