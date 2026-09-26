# `the_deno` (Deno Backend)

`the_deno` is an ultra-fast TS port of the framework designed for the Deno runtime, yielding up to 33%+ faster request handling than Oak.

## 1. Setup and Route Compilation
Routes are defined as arrays and compiled via `compile_routes` to optimize route matching.

```ts
import { compile_routes, response, Router } from "jsr:@puneetxp/the@0.1.0";

const _routes = [
  {
    path: "/users",
    child: [
      { path: "/", handler: UserController.all, islogin: true },
      { path: "/.+", handler: UserController.show }
    ]
  }
];

const routes = compile_routes(_routes);

Deno.serve({ port: 3333 }, async (req: Request) => {
  return await new Router(routes).route(req);
});
```

---

## 2. Handler Signatures
- **Public/Standard handler**: `(request: Request, params: any[]) => Promise<Response>`
- **Authenticated handler**: `(session: Session, params: any[]) => Promise<Response>`

---

## 3. Route Wildcards & Parameters
Use `/.+` in paths to match variable segments. Parameters are injected into the handler as an ordered array:
```ts
// Route path: "/users/.+/posts/.+"
// URL: "/users/42/posts/100"
static async showPost(session: Session, params: string[]) {
  const userId = params[0]; // "42"
  const postId = params[1]; // "100"
}
```

---

## 4. Authentication Guards and Roles
Guards are asynchronous functions returning `false` (allowed) or a string error message (denied).

```ts
// Define guard
export const AdminGuard = async (): Promise<false | string> => {
  return isAdmin ? false : "Not Authorized";
};

// Route attachment
const routes = [{
  path: "/admin",
  islogin: true,
  guard: [AdminGuard],
  roles: ["superadmin"],
  handler: AdminController.dashboard
}];
```
