import { Login } from "../Interface/TheType";
import { setactivefarm } from "../Store/Active_Farm";
import { LoginStore } from "../Store/Login";

const loginUrl = "/api/login";
const logoutUrl = "/api/logout";
const CHECK_THROTTLE_MS = 3000;

export class LoginService {
    private static checkingPromise: Promise<void> | null = null;
    private static lastCheckAt = 0;

    static get() {
        return LoginStore.get();
    }

    static set(i: Login | false) {
        LoginStore.set(i);
    }

    static async check(force = false): Promise<void> {
        const now = Date.now();
        if (!force) {
            if (this.checkingPromise) {
                return this.checkingPromise;
            }
            if (now - this.lastCheckAt < CHECK_THROTTLE_MS) {
                return;
            }
        }

        this.checkingPromise = (async () => {
            try {
                const response = await fetch(loginUrl, {
                    method: "GET",
                    credentials: "include",
                    headers: {
                        "Content-Type": "application/json",
                    },
                });

                if (response.ok) {
                    const data = await response.json();
                    if (data && typeof data === "object" && data.id) {
                        this.set(data as Login);
                    } else {
                        this.set(false);
                    }
                } else if (response.status === 401 || response.status === 403) {
                    this.set(false);
                } else {
                    console.error(
                        "Error checking login status:",
                        response.status,
                        response.statusText,
                    );
                }
            } catch (error) {
                console.error("Network error checking login status:", error);
            } finally {
                this.lastCheckAt = Date.now();
                this.checkingPromise = null;
            }
        })();

        return this.checkingPromise;
    }

    static async login(credentials: {
        email: string;
        password: string;
    }): Promise<Login | string> {
        try {
            const response = await fetch(loginUrl, {
                method: "POST",
                credentials: "include",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(credentials),
            });

            const data = await response.json();

            if (response.ok) {
                if (data && typeof data === "object" && data.id) {
                    this.set(data as Login);
                    return data as Login;
                } else {
                    return "Invalid login response";
                }
            } else {
                return typeof data === "string" ? data : "Login failed";
            }
        } catch (error) {
            console.error("Login error:", error);
            return "Network error during login";
        }
    }

    static async logout(): Promise<void> {
        try {
            const response = await fetch(logoutUrl, {
                method: "GET",
                credentials: "include",
                headers: {
                    "Content-Type": "application/json",
                },
            });

            this.set(false);
            setactivefarm(false);

            if (!response.ok) {
                console.warn(
                    "Logout request failed on server, but local state cleared",
                );
            }
        } catch (error) {
            console.error("Logout error:", error);
            this.set(false);
            setactivefarm(false);
        }
    }

    static isLoggedIn(): boolean {
        const loginState = this.get();
        return !!(loginState && loginState.login);
    }

    static getUser(): Login | false {
        return this.get().login || false;
    }
}
