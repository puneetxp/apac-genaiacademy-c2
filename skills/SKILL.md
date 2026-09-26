---
name: the-framework
description: >
  Design, build, extend, and debug applications using the custom framework family "the"
  (including PHP, MySQL, Deno, Angular, SolidJS, and VueJS). Use this skill when asked to
  develop, modify, debug, or understand code in repositories prefixed with `the_`, `the-`, or `the`.
  Trigger on mentions of: 'the framework', 'the_lib', 'autosetup.php', 'setup.php', 'Karl framework',
  'TPHP', 'puneetxp/the', 'the_deno', or any reference to model definitions under `database/Model/`
  or `_setup/model/`.
---

# The Framework ("the" / TPHP)

A custom, high-performance web framework family designed by Puneet Sharma (`puneetxp`), featuring multi-language backend options (PHP, Deno), a MySQL ORM with eager relation loading, dynamic/static routing, and an automated code generator (`puneetxp/compile-php`) that scaffolds full-stack modules.

---

## 1. Code Generation & Model Schema

The foundation of the framework is declarative model schemas written in JSON. The setup compiler (`setup.php` at the project root) parses these schemas to generate SQL tables, PHP models/controllers/routes, and frontend TypeScript interfaces/services/stores.

### Schema Definition Format
Model schemas are placed under `database/Model/[model_name].json` (or legacy `_setup/model/[model_name].json`).

```json
{
  "name": "client",
  "table": "clients",
  "crud": {
    "isuper": ["c", "r", "u", "a", "d"],
    "roles": {
      "executive": ["c", "r", "u", "a", "d"]
    }
  },
  "enable": 1,
  "data": [
    {
      "name": "name",
      "mysql_data": "varchar(255)",
      "datatype": "string"
    },
    {
      "name": "email",
      "mysql_data": "varchar(255)",
      "datatype": "string",
      "default": "NULL"
    }
  ],
  "relation": [
    {
      "name": "user",
      "default": "NULL"
    }
  ]
}
```

### Schema Parameters
- **`name`** *(string)*: Model name (singular lowercase).
- **`table`** *(string)*: MySQL database table name (plural).
- **`crud`** *(object or array)*: Operations allowed per role/guard namespace. 
  - Valid operations: `"c"` (create), `"r"` (read), `"u"` (update), `"d"` (delete), `"a"` (read all), `"p"` (upsert/bulk).
- **`data`** *(array)*: Individual database column configurations.
- **`relation`** *(array)*: Defines foreign-key relations.

---

## 2. Compilation Configuration (`config.json`)

The generation behavior is configured in `config.json` at the root of the project:

```json
{
  "fresh": true,
  "controller": true,
  "model": true,
  "mysql": true,
  "interface": true,
  "front-end": [
    "angular"
  ],
  "back-end": [
    "php"
  ],
  "public": "./public_html/",
  "table": {
    "user": true,
    "client": true
  }
}
```

### Scaffolding Command
To compile the schemas, run the setup script at the root directory of the application:
```bash
php setup.php
```

---

## 3. Platform Reference Manuals

For deep implementation guides, API schemas, and platform-specific code structures, refer to these guides:

* **PHP Backend**: [php-backend.md](file:///Users/puneetsharma/NetBeansProjects/intaxing23/.agents/skills/the-framework/references/php-backend.md) (TPHP ORM, Routing, Roles, and Custom Controllers).
* **Deno Backend**: [deno-backend.md](file:///Users/puneetsharma/NetBeansProjects/intaxing23/.agents/skills/the-framework/references/deno-backend.md) (the_deno fast router setup, wildcard parameters, and guards).
* **.NET Backend**: [dotnet-backend.md](file:///Users/puneetsharma/NetBeansProjects/intaxing23/.agents/skills/the-framework/references/dotnet-backend.md) (The.DotNet.Lib parameterized queries and user auth).
* **Angular Frontend**: [angular-frontend.md](file:///Users/puneetsharma/NetBeansProjects/intaxing23/.agents/skills/the-framework/references/angular-frontend.md) (NGXS stores, IndexedDB synchronization, material tables, and dynamic forms).

---

## 4. Development Guidelines & Best Practices

1. **Avoid manual SQL updates**: Always update `database/Model/*.json` first, and run `setup.php` to rebuild the schema files. Do not modify generated migrations or tables directly in development.
2. **Controller Customization Protection**: If you write custom logic in a generated PHP controller (e.g. `IsuperEmailController.php`), you MUST set its configuration table value to `true` in `config.json` (e.g. `"email": true`). This tells the setup compiler not to overwrite your customized controller code during subsequent builds.
3. **Nullable fields constraint**: If a field can be null, explicitly set `"default": "NULL"` in the JSON definition. By default, fields are defined as `NOT NULL`.
4. **Session cookie security**: Ensure `env.php` has correct parameters for cookie domain and SSL settings:
   - Development: `define('secure', false);`
   - Production: `define('secure', true);`
5. **Case sensitivity on file paths**: The framework is case sensitive. E.g., `solidjs/src/shared/Interface/Model/User.ts` must exactly align with casing configuration of your front-end TypeScript loaders.
6. **Local Database Override (`local_db.json`)**: To run database migrations locally without altering production configuration, create a `local_db.json` at the root of the project specifying local database connection details (`dbhost`, `dbuser`, `dbpwd`). The compiler automatically reads this file to override connection credentials for setup migrations.

