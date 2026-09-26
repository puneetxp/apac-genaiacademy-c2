# TPHP / `the_lib` (PHP Backend)

A lightweight, high-performance PHP backend framework featuring dynamic routing, an active record ORM, and eager relation loading.

## 1. Dynamic Routing (`Route`)
Routes are chain-loaded using the nullsafe builder pattern. Each route returns the `Route` instance.

```php
use The\{Route, Auth};
use App\Controller\{UserController, PageController};

(new Route())
  ?->get('/', [PageController::class, 'Home'])
  ?->post('register', [Auth::class, 'register'])
  ?->post('login', [Auth::class, 'login'])
  ?->get('logout', [Auth::class, 'logout'])
  ?->crud(['c', 'r', 'u'], 'user', [
      'read' => ['admin'],
      'write' => ['admin'],
      'update' => ['admin'],
      'delete' => ['-']
  ], UserController::class)
  ?->not_found();
```

> [!NOTE]
> Route controllers use standard method signatures: `index()`, `store()`, `show($id)`, `update($id)`, `upsert()`, and `delete($id)`.

---

## 2. Generated Controller Architecture
When compile setup runs, standard controllers are generated under `php/App/Controller/` split by role folders (e.g., `Isuper/`, `Islogin/`, `Ipublic/`, `Iexecutive/`).

### Role-Based Prefix Conventions
- `Isuper`: System admin dashboard actions.
- `Islogin`: Standard authenticated user actions.
- `Ipublic`: Public unauthenticated endpoints.
- `Iexecutive`: Field or support agent operations.

### Standard Controller Structure
Each controller class implements static CRUD actions corresponding to the permissions in the model schema:
```php
namespace App\Controller\Isuper;

use App\Model\Role;

class IsuperRoleController {
    public static function all() {
        if (isset($_GET["latest"])) {
            return Role::wherec([["updated_at", ">", $_GET["latest"]]])->get();
        }
        return Role::all();
    }
    public static function show($id) {
        return Role::find($id);
    }
    public static function store() {
        return Role::create($_POST)->getInserted();
    }
    public static function update($id) {
        Role::where(["id" => [$id]])->update($_POST);
        return Role::find($id);
    }
    public static function upsert() {
        return Role::upsert(json_decode($_POST["roles"]))->getsInserted();
    }
}
```

---

## 3. ORM Model (`The\Model`)
All generated models inherit from `The\Model`.

### Standard Query Methods
```php
// Find by primary key (default: id)
$user = User::find($id);

// Fetch all entries
$users = User::all();

// Filtered retrieval
$activeUsers = User::where(['enable' => 1])->get();

// Conditional operators (custom SQL clauses)
$flaggedUsers = User::wherec(['status = ? AND score > ?', [$status, $minScore]])->get();
```

### Eager Loading & Relations
The ORM supports rapid nested and multi-relation eager loading. Call `->with()` and chain `->sort()` to structure output.

```php
// Eager load relation "profile" and "orders"
$userWithRelations = User::find($id)->with(['profile', 'orders'])->sort();

// Nested relation loading
$userWithNested = User::all()->with([
    'orders' => ['items' => ['product']]
])->sort();
```

> [!TIP]
> If a model's `fillable` array contains the key `'sort'`, calling `->sort()` automatically sorts child collections by their `sort` field ascending.

### Pagination
```php
// Paginate query (reads $_GET['page'] and $_GET['pageItems'] automatically)
$paginatedUsers = User::all()->paginate(1, 25);
```
