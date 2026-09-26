# `The.DotNet.Lib` (.NET Backend)

A standard .NET Class Library port of the framework core, enabling parameterized database operations and user authentication.

## 1. Database Connection (`The.DotNet.Lib.DB`)
The `DB` class wraps ADO.NET connections to execute safe parameterized SQL queries.

```csharp
using The.DotNet.Lib;
using Microsoft.Data.Sqlite;

var connection = new SqliteConnection("Data Source=app.db");
IDB db = new DB(connection);
```

---

## 2. ORM Model (`The.DotNet.Lib.Model`)
All .NET database models extend `Model` and receive built-in CRUD capability.

```csharp
public class Product : Model
{
    public Product(IDB db) : base(db)
    {
        this.Table = "products";
        this.Name = "product";
    }
}
```

Usage in controllers:
```csharp
var productModel = new Product(db);

// Find single record
var product = productModel.Find(1);

// Retrieve all records
var allProducts = productModel.All().Items;

// Filtered retrieval
var activeProducts = productModel.Where(new Dictionary<string, object>
{
    { "enable", 1 }
}).Items;
```

---

## 3. Database Authentication (`The.DotNet.Lib.Auth`)
Provides safe SHA256 hashed password registration and login verification.

```csharp
// Register a new user
var result = Auth.Register(db, "John Doe", "john@example.com", "SecurePassword123");

// Verify login
var loginResult = Auth.Login(db, "john@example.com", "SecurePassword123");
```
