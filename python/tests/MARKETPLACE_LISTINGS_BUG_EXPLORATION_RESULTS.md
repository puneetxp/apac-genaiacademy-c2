# Marketplace Listings Bug Exploration Results

## Bug Confirmation

✓ **BUG CONFIRMED**: The marketplace listings query error exists in the unfixed code.

## Bug Details

- **Endpoint**: `GET /api/v1/marketplace/listings`
- **Error Message**: "Column expression, FROM clause, or other columns clause element expected, got <class 'app.orm.marketplace_listing.MarketplaceListing'>."
- **HTTP Status**: 500 Internal Server Error
- **Error Location**: `marketplace_service.py` line 437 in `get_listings()` method
- **Root Cause**: SQLAlchemy query API incompatible with custom ORM model

## Test Results Summary

- **Total Tests**: 21
- **Failed as Expected**: 21 (100%)
- **Passed Unexpectedly**: 0 (0%)

All test scenarios failed with HTTP 500 errors, confirming the bug exists across all query variations.

## Counterexamples Found

### 1. Basic Query Failure
**Test**: GET /api/v1/marketplace/listings
**Result**: HTTP 500 - Column expression error
**Confirms**: Even the simplest query without parameters fails

### 2. Sorting Scenarios - All Failed
All sorting variations failed with HTTP 500:
- `?sort_by=harvest_date&sort_order=asc` → HTTP 500
- `?sort_by=harvest_date&sort_order=desc` → HTTP 500
- `?sort_by=quantity&sort_order=asc` → HTTP 500
- `?sort_by=quantity&sort_order=desc` → HTTP 500
- `?sort_by=quality_grade&sort_order=desc` → HTTP 500
- `?sort_by=price&sort_order=desc` → HTTP 500

**Confirms**: The sorting logic at line 437 using `getattr(MarketplaceListing, sort_column_name)` fails because MarketplaceListing extends custom ORM, not SQLAlchemy's declarative base.

### 3. Filtering Scenarios - All Failed
All filtering variations failed with HTTP 500:
- `?crop_type=rice` → HTTP 500
- `?state=Punjab` → HTTP 500
- `?crop_type=rice&state=Punjab` → HTTP 500
- `?district=Ludhiana` → HTTP 500
- `?min_quantity=100` → HTTP 500
- `?max_quantity=500` → HTTP 500
- `?quality_grade=A` → HTTP 500

**Confirms**: The filtering logic using SQLAlchemy's `.filter()` method fails with custom ORM model.

### 4. Pagination Scenarios - All Failed
All pagination variations failed with HTTP 500:
- `?limit=10` → HTTP 500
- `?limit=10&offset=0` → HTTP 500
- `?limit=5&offset=20` → HTTP 500

**Confirms**: The pagination logic using SQLAlchemy's `.limit()` and `.offset()` methods fails with custom ORM model.

### 5. Combined Scenarios - All Failed
All combined parameter variations failed with HTTP 500:
- `?crop_type=wheat&sort_by=harvest_date&sort_order=desc` → HTTP 500
- `?sort_by=quantity&sort_order=desc&limit=10&offset=0` → HTTP 500
- `?state=Punjab&limit=10&offset=0` → HTTP 500
- `?crop_type=rice&state=Punjab&sort_by=harvest_date&sort_order=desc&limit=10&offset=0` → HTTP 500

**Confirms**: Any combination of query parameters fails due to the fundamental incompatibility.

## Root Cause Analysis

### Problem
The `get_listings()` method in `marketplace_service.py` uses SQLAlchemy's query API:
```python
query = self.db.query(MarketplaceListing).filter(MarketplaceListing.status == 'active')
```

At line 437, it attempts to access column attributes:
```python
sort_column = getattr(MarketplaceListing, sort_column_name, None)
```

### Why It Fails
1. **MarketplaceListing extends custom Model base class**, not SQLAlchemy's declarative base
2. **Custom ORM doesn't expose column attributes** the way SQLAlchemy does
3. **getattr() returns the class itself** or an unexpected value instead of a SQLAlchemy column object
4. **SQLAlchemy's query methods** (`.filter()`, `.order_by()`, `.limit()`, `.offset()`, `.all()`) don't work with the custom Model class

### Expected Behavior
The custom ORM provides its own query interface:
- `Model.where({'field': value})` - for filtering
- `model.and_where_custom([['field', 'op', 'value']])` - for custom conditions
- `model.db.rawsql(" ORDER BY column DESC ")` - for sorting
- `model.db.limit_q(limit).offset_q(offset)` - for pagination
- `model.get()` - to execute and fetch results

## Server Log Evidence

The server logs show the exact error for every request:
```
ERROR - Error getting listings: Column expression, FROM clause, or other columns clause element expected, got <class 'app.orm.marketplace_listing.MarketplaceListing'>.
```

This error appears consistently across all 21 test scenarios, confirming the bug is systematic and affects all query variations.

## Conclusion

The bug exploration test successfully confirmed the marketplace listings query error exists in the unfixed code. The error occurs because the service uses SQLAlchemy's query API with a model that extends a custom ORM base class, causing incompatibility at line 437 when attempting to access column attributes for sorting.

**Next Steps**: Implement the fix by replacing SQLAlchemy query API with the custom ORM's query methods as specified in the design document.
