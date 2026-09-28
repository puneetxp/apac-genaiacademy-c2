---
name: the-framework
description: >
  Design, build, extend, and debug applications using the "the" framework family by
  puneetxp: the schema-first generator (puneetxp/compile-php + setup.php), the PHP runtime
  (puneetxp/the / the_lib), the Deno runtime (@puneetxp/the / the_deno), the Python/FastAPI
  output, and the Angular (the-angular) and SolidJS frontends. Use this skill when working in
  repositories prefixed with `the_`, `the-`, or `the`, or in apps built on them (e.g. the_billing / INTAX).
  Trigger on mentions of: 'the framework', 'the_lib', 'compile-php', 'setup.php', 'autosetup.php',
  'TPHP', 'puneetxp/the', 'the_deno', '@puneetxp/the', 'the-angular', 'the-solid-router',
  `database/Model/*.json`, `config.json` "back-end"/"front-end", or role namespaces isuper/islogin/ipublic.
---

# The Framework ("the")

A schema-first framework family by Puneet Sharma (`puneetxp`). You describe each table **once** in JSON. The generator `puneetxp/compile-php` then writes the SQL, a role-guarded REST backend (PHP, Deno or Python), and typed frontend code (Angular or SolidJS). The generated code runs on small per-language runtimes that share the same concepts: a `Model` ORM with eager relations, a router with `islogin`/`roles`/`guard`, and a CRUD shorthand.

## 0. Repository map (under `/Users/waseemakram/Downloads/puneetxp/`)

| Repo | Role | Package / status |
|---|---|---|
| `compile-php` | **The generator**, plus the HTML→PHP view compiler | Composer `puneetxp/compile-php` (tag 0.2.24). Active. `compiley-php` is an older snapshot without git; ignore it. |
| `the_lib` | PHP runtime (`The\` namespace) | Composer `puneetxp/the` (tag 0.1.304, PHP ≥ 8.2). Active. |
| `the_deno` | Deno runtime | JSR `@puneetxp/the` 0.1.16 (HEAD). Apps may still pin deno.land/x `the@0.0.2`. |
| `the_template_php` | Starter template (`composer create-project`) | Composer `puneetxp/the_template_php`. Its README is stale. |
| `the-angular` | Angular UI library | npm `the-angular` 0.0.13, Angular 21. Active. |
| `the-angular-material` | Angular 16 predecessor | Legacy. |
| `the_web_component` | Vanilla custom elements (`<editable-list>`, `<wysiwyg-bs>`) | Prototype. |
| `the_dotnet` / `the_dotnet_api` | .NET 10 runtime port and sample API | Early. The generator for it is not wired in. |
| `the_go`, `the_spring` | Go and Java helper skeletons | Stubs only. |
| `the_billing` | INTAX GST billing app (Deno + SolidJS + MySQL) | The reference Deno app. The active copy is `/Users/waseemakram/Documents/the_billing`. |
| `intaxing23` | intaxing.in production app (PHP + Angular + MySQL) | The reference PHP app. Clone it with `git clone git@github.com-personal:puneetxp/intaxing23.git` (the SSH alias uses `~/.ssh/id_rsa_personal`). |
| `apac-genaiacademy-c2` | Rural farming platform (Python/FastAPI + SolidJS + PostgreSQL), at `/Users/waseemakram/Documents/apac-genaiacademy-c2` | The reference Python app, and the source of the template's `app/core`. It has its own Firebase `auth.py` and farm-specific `ownership.py` rules. Its SolidJS `apiClient` adds `/api/v1` to the generated `/islogin/<model>/` URLs. |
| `the`, `thesolidmarket` | 2022 start pack and Solid demo | Historical. |
| `the_doc` | Hugo/Doks documentation site | `content/en/docs/**` |

## 1. Workflow

1. Edit `database/Model/<name>.json`. **Never hand-edit generated SQL or models.**
2. Run `php setup.php` at the project root. It calls `Puneetxp\CompilePhp\setup`:
   ```php
   use Puneetxp\CompilePhp\setup;
   require "./vendor/autoload.php";
   $setup = new setup(__DIR__);
   $setup->config();          // table_set + every selected back-end/front-end + write()
   // or pick steps by hand: $setup->table_set(); $setup->deno_set(param:"URLPatternResult"); $setup->solidjs_set(); $setup->write();
   // $setup->migrate();       // apply SQL (drops the DB first if "fresh": true)
   ```
3. Apply `database/Migration.sql`, or call `migrate()`. There is also `sync()`, which adds missing columns and foreign keys to an existing DB.
4. PHP only: run `php php/set.php` to compile `Routes/pre/*` into `Routes/web.php`.

Real apps often call only some steps. intaxing23 runs `$setup->table_set()->php_set(); $setup->migratealter();`, and the_billing runs `table_set()`, `deno_set(param:"URLPatternResult")`, `solidjs_set()` and `write()`. Keep to whatever the app already does.

## 2. Model schema (quick form)

```json
{
  "name": "client",                     // singular
  "table": "clients",                   // plural
  "crud": {
    "isuper":  ["c","r","u","d","a","p","w"],
    "islogin": ["c","r","u","a","w"],
    "ipublic": ["r","a"],
    "roles":   { "executive": ["r","a"] }
  },
  "enable": 1,                          // adds enable TINYINT(1) DEFAULT 1
  "additional": ["slug","seo","delete"],// spelled "additional" ("addtional" is wrong)
  "unique": ["email"],
  "data": [
    { "name": "name",  "mysql_data": "varchar(255)", "datatype": "string" },
    { "name": "email", "mysql_data": "varchar(255)", "datatype": "string", "default": "NULL" },
    { "name": "status","mysql_data": "varchar(20)",  "datatype": "string", "sql_attribute": " NOT NULL DEFAULT 'draft'" }
  ],
  "relations": ["user", { "name": "photo", "default": "NULL" }]
}
```

- **CRUD letters:**
  - `c` create
  - `r` read one
  - `u` update
  - `d` delete
  - `a` read all (supports `?latest=<updated_at>` delta sync)
  - `w` where (`POST /where`)
  - `p` upsert or bulk
- A column is **NOT NULL by default**. Make it nullable with `"default": "NULL"`.
- `datatype` must match the SQL type: `string` for varchar/text, `number` for int/decimal/tinyint. `json`, `array` and `vector` are also accepted.
- Relations can take three forms:
  - a string, `"user"`, which gives `user_id` → `users.id`;
  - an object `{name, alias?, default?}`;
  - the explicit keyed form `"buyer": {"name":"buyer_id","table":"users","key":"id"}`.
  `relations` and the legacy `relation` are both accepted.

## 3. `config.json` essentials

- **`back-end`:** `"php"`, `"deno"` or `"python"`.
- **`front-end`:** `"angular"` or `"solidjs"`.
- **Values that do nothing today:**
  - `dotnet`, `golang` and `spring` are not wired into `config()`.
  - `vuets` is recognised but generates no files.
- **`env`:**
  - PHP writes each key as `define()` in `php/env.php`.
  - Deno writes `deno/.env` (`DBHOST`, `DBUSER`, `DBPWD`, `DBNAME`, `HOST`).
- **`fresh: true`:** the migration drops and recreates the DB. **`postgresql: true`:** emits PostgreSQL SQL.
- **Protecting a controller (`table` map):** the PHP generator only writes a controller when `table.<model>` **is not set**. The check is `isset`, so `false` protects the controller as well as `true`. `write()` adds `false` for every new model after the first run.
  - To regenerate a controller, **delete its key**.
  - To protect custom code, keep the key; use `true` so the intent is clear.
- **Keys the generator ignores:** `controller`, `model`, `mysql`, `interface`, `public`. `local_db.json` is not read by the current generator.

## 4. Roles and URLs

- **Role namespaces:**
  - `isuper` (admin): `/api/isuper/<model>`
  - `islogin` (any logged-in user): `/api/islogin/<model>`
  - `ipublic` (no auth): `/api/ipublic/<model>`
  - custom role `x`: `/api/x/<model>`, with controllers in `Controller/Ix/` (PHP)
- **PHP:** `isuper` is hard-wired to **user id 1**. Other roles come from `active_roles` → `roles.name`.
- **Deno HEAD:** user id 1 also bypasses role checks.
- **Built-in auth:**
  - `POST /api/login` with `{email,password}`
  - `GET /api/login` (status)
  - `POST /api/register` with `{name,email,password}`
  - `GET /api/logout`
- **Guards and roles only run when `islogin` is true**, either set on the route or inherited from its parent.

CRUD verb mapping differs by runtime. Always check which runtime version the app pins:

| Letter | PHP (`the_lib`) | Deno `the@0.0.2` | Deno `@puneetxp/the` 0.1.x |
|---|---|---|---|
| a | GET `/` | GET `/` | GET `/` |
| r | GET `/.+` | GET `/:id` | GET `/:id` |
| c | POST `/` | POST `/` | POST `/` |
| w | POST `/where` | POST `/where` | POST `/where` |
| u | **PATCH** `/.+` | **POST** `/:id` | **PATCH / PUT** `/:id` |
| p | **PUT** `/` | PATCH `/` | PATCH / PUT `/` |
| d | DELETE `/.+` | DELETE `/:id` | DELETE `/:id` + DELETE `/perma_delete/:id` (isuper) |

PHP also accepts `$_POST['_method']` to override the HTTP method, and `$_POST['_action']` to batch several requests in one call.

## 5. Generated output

| Target | Paths |
|---|---|
| SQL | `database/Mysql/{Structure,Relations,Insert,Alter}/*.sql`, plus the combined files `database/structure.sql`, `relation.sql`, `insert.sql` and `Migration.sql`. With `postgresql: true`, only the combined files are written. |
| PHP | `php/App/Model/<Name>.php`, `php/App/Controller/<Role>/<Role><Name>Controller.php`, `php/Routes/pre/api/<Role>.php`, `php/env.php`, plus the `template/php` scaffold, which is copied without overwriting. |
| Deno | `deno/App/{Model,Interface/Model}/<Name>.ts`, `deno/App/Controller/<Role>/<Name>Controller.ts`, `deno/App/Routes/<Role>.ts` and `deno/.env`. The isuper routes go to `Routes/Isuper.ts`, exporting `isuper` with `roles: ["isuper"]`. The generated `delete` soft-deletes (sets `deleted_at`) only when the model has `additional: ["delete"]`, and hard-deletes otherwise. Models are factories (`X$()`). The scaffold (`index.ts` on :9000, `dep.ts` on `jsr:@puneetxp/the@0.1.16`, AuthController, placeholder route files) is copied only when missing. |
| Python (FastAPI) | `python/app/{models,orm,services}/<snake>.py`, `python/app/api/<scope>/<model>/<model>.py` and `python/app/api/routers.py`. `app/main.py` runs uvicorn on :8000. Routes: GET `/`, POST `/where`, GET `/{item_id}`, POST `/` (201), PUT `/{item_id}`, POST `/upsert`, DELETE `/{item_id}`. isuper routes use `Depends(get_current_admin)`. islogin and custom-role routes call `service.*(…, owner=current_user)`. Needs `postgresql: true`. The runtime is in `app/core`; see below. |
| Angular | `angular/src/app/shared/{Service/Model/<Name>.service.ts, Ngxs/State, Ngxs/Action, Interface/Model, Form/Validation, db/tables.ts}`. It also patches `angular.json`. |
| SolidJS | `solidjs/src/shared/{Interface/Model/<Name>.ts, Service/Services.ts, run.ts}`. `Services.ts` keeps hand-added `export * from` lines. Each service is `new ModelService<T>().seTable("x").seturl("/islogin/x/")`. **Don't change that URL in the generator:** apps add their own prefix in `ModelService`/`apiClient` (apac adds `/api/v1`). **`ModelService` itself is not generated:** `Services.ts` imports it from `./ModelService` or `./Service`; copy it from the reference app that matches the backend: apac `Service/ModelService.ts` (Python; PUT update, uses `apiClient` + Bearer) or the_billing `Service/Service.ts` (Deno 0.0.2; POST update, cookie, `?latest=` delta sync). Both extend `Stores<T>` (a Solid `createStore` mirrored to IndexedDB). Routing uses `the-solid-router` (the_billing) or `@solidjs/router` (apac). See references/solidjs-frontend.md. |

**Python `app/core`** (template, ported from apac):
  - `db.py`: psycopg 3 plus an SQLAlchemy pool, configured by `POSTGRES_*`.
  - `model.py`.
  - `crud_service.py`: `CrudService`.
  - `ownership.py`: rules; by default, tables with `user_id` are scoped and `user_id` is forced on create.
  - `auth.py`: HS256 JWT with `JWT_SECRET`. Passwords are sha3-256 hex, the same as PHP. `isuper` means user 1 or the `active_roles` → `isuper` role. It exposes `get_current_active_user` and `get_current_admin`.
  - Plus `api/auth.py` (`/login`, `/register`), and a `main.py` that enforces custom `crud.roles` with `require_role(scope, "isuper")`.
  New projects (no `app/main.py`) get the full scaffold; existing ones only get missing `app/core` files. `the_python` is a separate helper library that the generated code doesn't use.

Other generator notes:
- A relation that points to an unknown table prints a warning and is skipped.
- `php compile.php` compiles the `Resource/View` HTML files (`<t-l.guest>`, `@props`, `{$var}`, `@foreach`) into `\The\PageBase` classes. Tag aliases come from `config.json` `alias`.

## 6. Known issues (check before relying on a feature)

| Where | Issue | Status |
|---|---|---|
| `the_lib` `Auth::profile()`/`profileupdate()` | These filter on `user_id`, but `users` has no such column. `Model::where()` silently drops unknown keys (`Req::get($this->model, …)`), so GET returns the **first user** and POST updates **every user**. | **Open, security.** The fix is `where(["id" => [$_SESSION['user_id']]])` and allowing only name, phone and email (plus a hashed password). Ask the user before editing `the_lib`. |
| `the_lib` `Auth::login` | A wrong password falls through to 404 "User Not Found" because the `Response::why(...)` result isn't returned. | Open. Keep the 404 status if you fix it; the-angular treats any 2xx as a successful login. |
| `Model::where()` (PHP and Deno) | Unknown column keys are dropped, and `update()` without a where updates every row. | By design. Always use real column names and array values: `["id" => [$id]]`. |
| PHP template ≤ 0.2.24 | `"ilogin" => true` is a typo, which leaves `/api/env` and `/api/isuper` **unprotected**. `/reset` routes to a missing method. | Fixed in the template after 0.2.24 (login and register moved to `Inotlogin.php`, the intaxing23 layout). Existing projects must be fixed by hand. |
| Generator ≤ 0.2.24 | A model with no relations crashes PHP and Deno generation. Deno always soft-deleted. The Deno scaffold pinned `the@0.0.0.4.8` and used the removed `.route(req)`. The Python scaffold had no `app/core`, and its `main.py` imported the empty `app.api.all_routers`. | Fixed (uncommitted, after 0.2.24). Verified that intaxing23 and apac regenerate byte-for-byte identically. |
| `php_set()` | It rewrites `php/env.php` from `config.json` → `env` on every run, which discards hand edits. intaxing23's `env.php` has `samesite "None"` while its config says `"Strict"`. | Keep `config.json` in sync before regenerating. |
| Deno `the@0.0.2` | `SessionRoles` gives every user every role, the update verb is POST, and there's no 404. | Fixed in 0.1.x. the_billing works around it with `withRealRoles()`. |
| the_billing | Its Deno routes have no `/api` prefix. nginx strips it with `proxy_pass …:9000/;`, and the Vite proxy now has a matching `rewrite`. Its hand-edited `Routes/Islogin.ts` and `Isuper.ts` would be overwritten by `deno_set()`. | Don't regenerate the_billing's routes without saving those files first. |
| Python ownership | A table with no `OWNERSHIP` rule and no `user_id` column is unscoped for `/islogin/*`: any signed-in user can read and write every row. | By design (shared data). Add a rule, or grant `islogin` only `r`/`a`. |
| `vuets`, `dotnet`, `golang`, `spring` | These produce no files. | Open. |

## 7. Platform references

- [references/php-backend.md](references/php-backend.md): `the_lib` router arrays, `Model` ORM, `Auth`/`Sessions`, `Response`/`Req` and `FileAct`.
- [references/deno-backend.md](references/deno-backend.md): `the_deno` bootstrap, URLPattern params, `Session` on Deno KV, `Model`, version differences and per-tenant scoping.
- [references/python-backend.md](references/python-backend.md): FastAPI output, the `app/core` runtime (DB, CrudService, ownership, JWT auth), custom-role guards in `main.py`, and apac specifics.
- [references/dotnet-backend.md](references/dotnet-backend.md): `The.DotNet.Lib`, plus the status of Go and Spring.
- [references/solidjs-frontend.md](references/solidjs-frontend.md): generated `Services.ts`/`run.ts`, the two `ModelService` implementations (apac → Python, the_billing → Deno), a verb matrix per backend, apiClient and cookie auth, IndexedDB and routing.
- [references/angular-frontend.md](references/angular-frontend.md): `the-angular` components, generated services, NGXS and IndexedDB.

## 8. Guidelines

1. **Change the schema first, then regenerate.** Put custom logic in controllers, and keep those controllers' keys in the `table` map.
2. **Scope every per-user query.** Filter per-user routes by the session user: `$_SESSION['user_id']` in PHP, `session.Login.id` in Deno. For per-tenant (for example per-book) routes, verify ownership of the URL id before querying. See `ownedBook()` in the_billing.
3. **Nullable columns** need an explicit `"default": "NULL"`.
4. **Cookies:**
   - In development, set `"secure": false` in `env`.
   - In production, set `"secure": true` and `sslhost: ".domain"`.
   - Deno sessions need `--unstable-kv`.
5. **Case matters in paths.** For example `Interface/Model/User.ts` must match the generated casing exactly.
6. **Don't disturb existing apps.** intaxing23 and the_billing are live, so never change their columns, `active_roles`/`roles` semantics, session shape, route prefixes or `table` protection. After any generator change, prove the app's generated output is unchanged:
   - copy the app, excluding `.git`, `vendor`, `node_modules`, `.venv`, `__pycache__` and `.claude` (it has symlink loops);
   - run the app's own setup steps against the local `compile-php/src`, using a small `spl_autoload_register` for `Puneetxp\CompilePhp\`;
   - run it before and after the change, then `diff -r` the two copies.
   Template files are only copied when missing, so template edits affect new projects only.
7. **Don't trust the old READMEs.** The READMEs of `the_template_php`, `the` and `thesolidmarket` describe `App/Karl/setup/autosetup.php` and a flat `crud` array with `roles{read,write,...}`. That format is obsolete; use the per-role `crud` object.
8. **After changes, run the relevant checks and report failures honestly:**
   - `deno check index.ts` (or `npx -y deno check index.ts` when Deno isn't installed)
   - `npx vite build`
   - `php -l`
