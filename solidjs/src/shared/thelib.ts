/**
 * Low-level utility functions for networking and DOM
 */
import { LoginService } from "./Service";


export const dq = (query: string) => document.querySelector(query);
export const dqa = (query: string) => document.querySelectorAll(query);

export function capitalizeFirstLetter(val: string) {
    return String(val).charAt(0).toUpperCase() + String(val).slice(1);
}

export const arraycolsum = (array: any[], col: string) => {
    let value = 0;
    array.forEach((element) => {
        value += Number(element[col]);
    });
    return value;
};

export const Fetch = async (url: string, init?: RequestInit) => {
    try {
        const fullInit = {
            ...init,
            credentials: "include" as const,
        };
        const req = await fetch(url, fullInit);

        if (req.status === 401 || req.status === 403) {
            LoginService.check();
            console.warn(`Unauthorized or Forbidden access - ${req.status}`);
        }

        if (req.status === 200) {
            return req;
        }
    } catch (e) {
        console.error("Fetch error:", e);
    }
};


export const JFetch = async (url: string, init?: RequestInit): Promise<any | undefined> => {
    const formattedUrl = url.replace(/\/$/, "");
    const response = await Fetch(formattedUrl, init);
    return response?.json();
};

export const JGetFetch = async (url: string, params: Record<string, any>) => {
    const searchParams = new URLSearchParams(params).toString();
    return await JFetch(`${url}?${searchParams}`);
};
