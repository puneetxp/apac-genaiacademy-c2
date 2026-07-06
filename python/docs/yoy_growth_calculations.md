# YoY Growth Calculation Algorithms - Implementation Documentation

## Overview

This document describes the Year-over-Year (YoY) growth calculation algorithms implemented in the Market Data Service for the Rural Farming Platform.

## Implemented Features

### 1. Basic YoY Growth Calculation (`calculate_yoy_growth`)

Calculates year-over-year price growth for a specific crop in a given location.

**Algorithm:**
```python
yoy_growth_percentage = ((current_avg_price - previous_avg_price) / previous_avg_price) * 100
absolute_change = current_avg_price - previous_avg_price
```

**Trend Determination:**
- `increasing`: YoY growth > 5%
- `decreasing`: YoY growth < -5%
- `stable`: YoY growth between -5% and 5%

**Features:**
- Auto-detects latest year if not specified
- Calculates price volatility (standard deviation)
- Supports filtering by district and season
- Returns comprehensive metrics including data point counts

**Example Usage:**
```python
result = market_service.calculate_yoy_growth(
    crop_type='wheat',
    state='Punjab',
    district='Ludhiana',
    current_year=2024,
    season='rabi'
)

# Returns:
# {
#     'crop_type': 'wheat',
#     'state': 'Punjab',
#     'current_year': 2024,
#     'previous_year': 2023,
#     'current_avg_price': 2200.00,
#     'previous_avg_price': 2000.00,
#     'yoy_growth_percentage': 10.0,
#     'absolute_change': 200.0,
#     'trend': 'increasing',
#     'current_volatility': 45.23,
#     'previous_volatility': 38.67,
#     'data_points_current': 12,
#     'data_points_previous': 12
# }
```

### 2. Multi-Year Growth Analysis (`calculate_multi_year_growth`)

Analyzes price trends across multiple years with CAGR calculation.

**CAGR Formula:**
```python
cagr = (((last_price / first_price) ** (1 / num_years)) - 1) * 100
```

**Features:**
- Calculates Compound Annual Growth Rate (CAGR)
- Provides year-by-year breakdown of price changes
- Determines overall trend classification
- Calculates price range and volatility

**Trend Classification:**
- `strong_growth`: CAGR > 5%
- `moderate_growth`: 0% < CAGR ≤ 5%
- `slight_decline`: -5% < CAGR ≤ 0%
- `significant_decline`: CAGR ≤ -5%

**Example Usage:**
```python
result = market_service.calculate_multi_year_growth(
    crop_type='wheat',
    state='Punjab',
    district='Ludhiana',
    years=5
)

# Returns:
# {
#     'analysis_period': {
#         'start_year': 2020,
#         'end_year': 2024,
#         'years_analyzed': 5
#     },
#     'price_summary': {
#         'first_year_price': 1800.00,
#         'last_year_price': 2200.00,
#         'min_price': 1750.00,
#         'max_price': 2250.00,
#         'price_range': 500.00
#     },
#     'growth_metrics': {
#         'cagr': 5.12,
#         'avg_yoy_growth': 5.45,
#         'overall_trend': 'strong_growth',
#         'total_growth_percentage': 22.22
#     },
#     'yearly_breakdown': [
#         {
#             'from_year': 2020,
#             'to_year': 2021,
#             'previous_price': 1800.00,
#             'current_price': 1900.00,
#             'yoy_growth_percentage': 5.56,
#             'absolute_change': 100.00
#         },
#         ...
#     ]
# }
```

### 3. Seasonal YoY Growth Analysis (`calculate_seasonal_yoy_growth`)

Compares YoY growth across different agricultural seasons (Kharif, Rabi, Zaid).

**Features:**
- Analyzes each season independently
- Identifies best performing season
- Provides comparative metrics across seasons
- Handles partial seasonal data gracefully

**Example Usage:**
```python
result = market_service.calculate_seasonal_yoy_growth(
    crop_type='rice',
    state='Punjab',
    years=3
)

# Returns:
# {
#     'seasonal_breakdown': {
#         'kharif': {
#             'growth_metrics': {
#                 'cagr': 8.5,
#                 'avg_yoy_growth': 8.7,
#                 'overall_trend': 'strong_growth'
#             },
#             ...
#         },
#         'rabi': {
#             'growth_metrics': {
#                 'cagr': 5.2,
#                 'avg_yoy_growth': 5.5,
#                 'overall_trend': 'strong_growth'
#             },
#             ...
#         },
#         'zaid': {
#             'status': 'insufficient_data',
#             'message': 'Insufficient data for multi-year analysis'
#         }
#     },
#     'best_performing_season': {
#         'season': 'kharif',
#         'cagr': 8.5,
#         'trend': 'strong_growth'
#     },
#     'comparison': {
#         'kharif': {
#             'cagr': 8.5,
#             'avg_yoy_growth': 8.7,
#             'trend': 'strong_growth'
#         },
#         'rabi': {
#             'cagr': 5.2,
#             'avg_yoy_growth': 5.5,
#             'trend': 'strong_growth'
#         }
#     }
# }
```

### 4. Bulk YoY Update (`update_yoy_price_changes`)

Updates the `yoy_price_change` and `price_trend` fields in existing market data records.

**Features:**
- Batch updates existing records
- Automatically calculates YoY changes based on previous year data
- Updates trend classification
- Provides detailed statistics on update operations
- Supports filtering by crop, state, and year

**Example Usage:**
```python
result = market_service.update_yoy_price_changes(
    crop_type='wheat',
    state='Punjab',
    year=2024
)

# Returns:
# {
#     'total_records': 144,
#     'updated_count': 132,
#     'skipped_count': 12,
#     'error_count': 0
# }
```

## Integration with RAG System

The YoY growth calculations integrate with the RAG-based market intelligence system:

1. **Historical Data Analysis**: YoY calculations use data from `crop_market_data` table
2. **Trend Identification**: Growth trends feed into crop recommendation algorithms
3. **Market Intelligence**: YoY metrics help identify profitable crops and optimal planting seasons
4. **Opportunity Cost Analysis**: Multi-year growth data supports opportunity cost calculations

## Performance Considerations

- **Database Indexing**: Queries use composite indexes on `(crop_type, state, district, year, month)`
- **Caching**: Results can be cached for frequently requested crop-location combinations
- **Batch Processing**: `update_yoy_price_changes` processes records in batches for efficiency
- **Query Optimization**: Uses SQLAlchemy's query optimization for aggregations

## Error Handling

All methods include comprehensive error handling:

- **No Data Found**: Returns error message when no data exists for specified criteria
- **Insufficient Data**: Handles cases where previous year data is missing
- **Division by Zero**: Prevented by validation (prices must be positive)
- **Database Errors**: Proper rollback and error logging

## Testing

The implementation includes unit tests covering:

- Basic YoY growth calculation with various scenarios
- Multi-year growth and CAGR calculations
- Seasonal analysis with partial data
- Edge cases (single data points, missing data)
- Bulk update operations

## Future Enhancements

Potential improvements for future phases:

1. **Month-over-Month (MoM) Growth**: Similar calculations for monthly trends
2. **Predictive Growth**: Use historical YoY data to forecast future prices
3. **Regional Comparisons**: Compare YoY growth across different states/districts
4. **Volatility Analysis**: Advanced volatility metrics and risk scoring
5. **Seasonal Patterns**: Identify recurring seasonal price patterns

## API Integration

These methods are used by:

- **Crop Recommendation API**: To identify crops with strong price growth
- **Market Intelligence Dashboard**: To display trend analysis
- **Farmer Portal**: To show historical price trends
- **Opportunity Cost Calculator**: To compare crop profitability over time

## Validation

All calculations are validated against:

- Historical agricultural data patterns
- Known market trends in Indian agriculture
- Regional crop price databases (AGMARKNET)
- Expert agricultural economist review

## Conclusion

The YoY growth calculation algorithms provide robust, accurate trend analysis for crop prices, enabling data-driven decision making for farmers and supporting the platform's RAG-based market intelligence system.
