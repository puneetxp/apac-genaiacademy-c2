import { createStore } from "solid-js/store";
import { Farm } from "../Interface/Model/Farm";

interface ActiveFarmStateModel {
    farm: null | Farm;
}

const local = localStorage.getItem("activefarm");
let intialstate: Farm | null = null;
if (local && local.trim() !== "") {
    try {
        intialstate = JSON.parse(local) as Farm;
    } catch (error) {
        console.warn("Failed to parse activefarm from localStorage:", error);
        localStorage.removeItem("activefarm"); // Clear invalid data
        intialstate = null;
    }
}

const [activestate, activeset] = createStore<ActiveFarmStateModel>({
    farm: intialstate,
});

export function activefarm() {
    return activestate;
}

export function setactivefarm(i: Farm | false | string) {
    if (typeof i != "string" && i != false) {
        activeset({ farm: i });
        localStorage.setItem("activefarm", JSON.stringify(i));
    } else {
        activeset({ farm: null });
    }
}
