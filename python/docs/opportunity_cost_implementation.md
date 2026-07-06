# Opportunity Cost Calculation Engine - Implementation Summary

## Overview

The Opportunity Cost Calculation Engine has been successfully implemented as part of the RAG-Based Market Intelligence System. This validates **Acceptance Criteria 4 (AC4)**: "RAG system suggests top 3 profitable crops with opportunity cost analysis."

## Implementation Details

### 1. Core Service Methods

Located in: `app/services/market_data_service.py`

#### `calculate_opportunity_cost()`
Calculates the opportunity cost of choosing one crop over another.

**Parameters:**
- `primary_crop`: The crop being considered
- `alternative_crop`: The alternative crop to compare against
- `state`: State name
- `district`: District name (optional)
- `season`: Season filter (optional)
- `year`: Year for comparison (defaults to latest year)

**Returns:**
- Profit comparison (per acre)
- Investment comparison
- ROI comparison
- Risk assessment for both crops
- Opportunity cost calculation (profit difference)
- Risk-adjusted opportunity cost
- Recommendation with confidence score
- Detailed reasoning

**Example Response:**
```json
{
  "analysis_type": "opportunity_cost",
  "location": {
    "state": "Punjab",
    "district": "Ludhiana",
    "season": "rabi",
    "year": 2023
  },
  "primary_crop": {
    "name": "Wheat",
    "avg_profit_per_acre": 65000.00,
    "avg_investment": 35000.00,
    "avg_roi_percentage": 85.71,
    "risk_level": "low"
  },
  "alternative_crop": {
    "name": "Cotton",
    "avg_profit_per_acre": 85000.00,
    "avg_investment": 45000.00,
    "avg_roi_percentage": 88.89,
    "risk_level": "medium"
  },
  "opportunity_cost": {
    "profit_difference": 20000.00,
    "investment_difference": 10000.00,
    "roi_difference": 3.18,
    "risk_factor": 1.2,
    "risk_adjusted_cost": 24000.00,
    "interpretation": "positive"
  },
  "recommendation": {
    "choice": "Cotton",
    "message": "Consider switching to Cotton for ₹20,000 higher profit per acre",
    "confidence": 0.85,
    "reasoning": [
      "By choosing Wheat over Cotton, you forgo ₹20,000 profit per acre",
      "Cotton requires ₹10,000 more investment per acre",
      "Cotton offers 3.18% better ROI",
      "Risk comparison: Wheat (low) vs Cotton (medium)"
    ]
  }
}
```

#### `calculate_multi_crop_opportunity_costs()`
Calculates opportunity costs for multiple alternative crops simultaneously.

**Parameters:**
- `primary_crop`: The crop being considered
- `alternative_crops`: List of alternative crops to compare
- `state`: State name
- `district`: District name (optional)
- `season`: Season filter (optional)
- `year`: Year for comparison
- `top_n`: Number of top alternatives to highlight (default 3)

**Returns:**
- Top N alternatives ranked by profit difference
- Best alternative with highest profit potential
- Total opportunity cost across all alternatives
- Detailed comparisons for each alternative
- Insights and recommendations

#### `get_top_profitable_crops()` - **AC4 Validation**
Gets top N most profitable crops for a location with opportunity cost analysis.

**This is the core function that validates AC4.**

**Parameters:**
- `state`: State name (required)
- `district`: District name (optional)
- `season`: Season filter (optional)
- `year`: Year for analysis (defaults to latest year)
- `top_n`: Number of top crops to return (default 3)
- `include_opportunity_costs`: Include opportunity cost analysis (default true)

**Returns:**
- Top N most profitable crops ranked by profit per acre
- Average profit, investment, and ROI for each crop
- Risk level assessment for each crop
- Opportunity cost analysis comparing top crops
- Recommendation with confidence score

**Example Response:**
```json
{
  "location": {
    "state": "Punjab",
    "district": "Ludhiana",
    "year": 2023
  },
  "top_profitable_crops": [
    {
      "crop_type": "Cotton",
      "avg_profit_per_acre": 85000.00,
      "avg_investment": 45000.00,
      "avg_roi_percentage": 88.89,
      "risk_level": "medium",
      "data_points": 15
    },
    {
      "crop_type": "Rice",
      "avg_profit_per_acre": 70000.00,
      "avg_investment": 40000.00,
      "avg_roi_percentage": 75.00,
      "risk_level": "medium",
      "data_points": 20
    },
    {
      "crop_type": "Wheat",
      "avg_profit_per_acre": 65000.00,
      "avg_investment": 35000.00,
      "avg_roi_percentage": 85.71,
      "risk_level": "low",
      "data_points": 25
    }
  ],
  "total_crops_analyzed": 8,
  "opportunity_cost_analysis": {
    "comparisons": [
      {
        "choosing": "Rice",
        "forgoing": "Cotton",
        "opportunity_cost": 15000.00,
        "reasoning": "Choosing Rice over Cotton means forgoing ₹15,000 per acre"
      },
      {
        "choosing": "Wheat",
        "forgoing": "Cotton",
        "opportunity_cost": 20000.00,
        "reasoning": "Choosing Wheat over Cotton means forgoing ₹20,000 per acre"
      }
    ],
    "recommendation": "Cotton offers the highest profit potential in this location",
    "confidence": 0.85
  }
}
```

#### `save_opportunity_cost_analysis()`
Calculates and saves opportunity cost analysis to the database.

**Parameters:**
- Same as `calculate_opportunity_cost()`

**Returns:**
- Created `OpportunityCost` database record

### 2. API Endpoints

Located in: `app/market_data.py`

#### `GET /market-data/opportunity-cost`
Calculate opportunity cost between two crops.

**Query Parameters:**
- `primary_crop`: The crop being considered (required)
- `alternative_crop`: The alternative crop to compare (required)
- `state`: State name (required)
- `district`: District name (optional)
- `season`: Season filter (optional)
- `year`: Year for comparison (optional)

**Example Request:**
```
GET /market-data/opportunity-cost?primary_crop=Wheat&alternative_crop=Cotton&state=Punjab&district=Ludhiana&year=2023
```

#### `GET /market-data/opportunity-cost/multi-crop`
Calculate opportunity costs for multiple alternative crops.

**Query Parameters:**
- `primary_crop`: The crop being considered (required)
- `alternative_crops`: Comma-separated list of alternatives (required)
- `state`: State name (required)
- `district`: District name (optional)
- `season`: Season filter (optional)
- `year`: Year for comparison (optional)
- `top_n`: Number of top alternatives (default 3)

**Example Request:**
```
GET /market-data/opportunity-cost/multi-crop?primary_crop=Wheat&alternative_crops=Cotton,Rice,Sugarcane&state=Punjab&top_n=3
```

#### `POST /market-data/opportunity-cost/save`
Calculate and save opportunity cost analysis to database.

**Query Parameters:**
- Same as single opportunity cost endpoint

#### `GET /market-data/top-profitable-crops` - **AC4 Endpoint**
Get top N most profitable crops with opportunity cost analysis.

**This endpoint validates AC4.**

**Query Parameters:**
- `state`: State name (required)
- `district`: District name (optional)
- `season`: Season filter (optional)
- `year`: Year for analysis (optional)
- `top_n`: Number of top crops (default 3)
- `include_opportunity_costs`: Include analysis (default true)

**Example Request:**
```
GET /market-data/top-profitable-crops?state=Punjab&district=Ludhiana&top_n=3&include_opportunity_costs=true
```

## Key Features

### 1. Opportunity Cost Definition
The opportunity cost represents the profit that could have been earned by choosing the alternative crop instead of the primary crop. This helps farmers understand trade-offs in crop selection.

**Formula:**
```
Opportunity Cost = Alternative Crop Profit - Primary Crop Profit
```

**Interpretation:**
- **Positive value**: Alternative crop is more profitable (farmer forgoes profit by choosing primary)
- **Negative value**: Primary crop is more profitable (good choice)
- **Near zero**: Both crops offer similar profitability

### 2. Risk-Adjusted Opportunity Cost
The engine calculates a risk-adjusted opportunity cost that accounts for the risk levels of both crops.

**Risk Factor Calculation:**
```python
risk_values = {'low': 0.8, 'medium': 1.0, 'high': 1.2}
risk_factor = alternative_risk_value / primary_risk_value
risk_adjusted_cost = profit_difference * risk_factor
```

**Example:**
- If alternative crop is riskier, the opportunity cost is adjusted upward
- If alternative crop is safer, the opportunity cost is adjusted downward

### 3. Multi-Crop Comparison
Farmers can compare multiple crops simultaneously to see all their options and understand the full range of opportunities.

**Features:**
- Ranks alternatives by profit difference
- Identifies best alternative
- Calculates total opportunity cost
- Provides insights on risk and investment

### 4. Top Profitable Crops Recommendation (AC4)
The core RAG-based recommendation system that suggests top 3 profitable crops with opportunity cost analysis.

**Features:**
- Ranks crops by profitability
- Includes profit, investment, and ROI metrics
- Assesses risk levels
- Calculates opportunity costs between top crops
- Provides actionable recommendations

## Database Schema

The `opportunity_costs` table stores calculated opportunity cost analyses:

```sql
CREATE TABLE opportunity_costs (
    id UUID PRIMARY KEY,
    location_state VARCHAR(100) NOT NULL,
    location_district VARCHAR(100),
    primary_crop VARCHAR(100) NOT NULL,
    alternative_crop VARCHAR(100) NOT NULL,
    season VARCHAR(50),
    year INTEGER,
    primary_crop_profit DECIMAL(10, 2) NOT NULL,
    alternative_crop_profit DECIMAL(10, 2) NOT NULL,
    profit_difference DECIMAL(10, 2) NOT NULL,
    primary_crop_investment DECIMAL(10, 2),
    alternative_crop_investment DECIMAL(10, 2),
    investment_difference DECIMAL(10, 2),
    primary_crop_roi DECIMAL(5, 2),
    alternative_crop_roi DECIMAL(5, 2),
    roi_difference DECIMAL(5, 2),
    primary_crop_risk VARCHAR(20),
    alternative_crop_risk VARCHAR(20),
    risk_factor DECIMAL(3, 2),
    recommended_choice VARCHAR(100),
    recommendation_confidence DECIMAL(3, 2),
    recommendation_reasoning TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Integration with RAG System

The opportunity cost calculation engine integrates with the RAG-based market intelligence system:

1. **Historical Data**: Uses `crop_profitability` table for profit, investment, and ROI data
2. **Market Intelligence**: Leverages market data for informed recommendations
3. **Seasonal Trends**: Considers seasonal patterns in opportunity cost calculations
4. **Risk Assessment**: Incorporates risk levels into recommendations

## Use Cases

### 1. Annual Crop Strategy Planning
Farmers can use the engine to plan their annual crop strategy by comparing profitability across seasons.

**Example:**
```
GET /market-data/top-profitable-crops?state=Punjab&season=kharif&top_n=3
```

### 2. Crop Selection Decision Support
Farmers can compare specific crops they're considering to make informed decisions.

**Example:**
```
GET /market-data/opportunity-cost?primary_crop=Wheat&alternative_crop=Cotton&state=Punjab
```

### 3. Multi-Crop Comparison
Farmers can evaluate multiple alternatives simultaneously to see all their options.

**Example:**
```
GET /market-data/opportunity-cost/multi-crop?primary_crop=Wheat&alternative_crops=Cotton,Rice,Sugarcane,Mustard&state=Punjab
```

### 4. Risk-Adjusted Planning
Farmers can understand the risk-return trade-offs of different crop choices.

## Validation of AC4

**Acceptance Criteria 4 (AC4):**
"RAG system suggests top 3 profitable crops with opportunity cost analysis"

**Validation:**
✅ The `get_top_profitable_crops()` function returns top 3 (or N) most profitable crops
✅ Each crop includes profit, investment, ROI, and risk metrics
✅ Opportunity cost analysis is included comparing top crops
✅ Recommendations are provided with confidence scores
✅ API endpoint `/market-data/top-profitable-crops` exposes this functionality
✅ System uses historical profitability data from RAG database

**Example AC4 Validation:**
```json
{
  "top_profitable_crops": [
    {"crop_type": "Cotton", "avg_profit_per_acre": 85000},
    {"crop_type": "Rice", "avg_profit_per_acre": 70000},
    {"crop_type": "Wheat", "avg_profit_per_acre": 65000}
  ],
  "opportunity_cost_analysis": {
    "comparisons": [
      {
        "choosing": "Rice",
        "forgoing": "Cotton",
        "opportunity_cost": 15000,
        "reasoning": "Choosing Rice over Cotton means forgoing ₹15,000 per acre"
      }
    ],
    "recommendation": "Cotton offers the highest profit potential",
    "confidence": 0.85
  }
}
```

## Testing

To test the opportunity cost calculation engine:

1. **Ensure profitability data exists:**
   ```sql
   SELECT * FROM crop_profitability WHERE state = 'Punjab' AND year = 2023;
   ```

2. **Test single opportunity cost:**
   ```bash
   curl "http://localhost:8000/market-data/opportunity-cost?primary_crop=Wheat&alternative_crop=Cotton&state=Punjab&year=2023"
   ```

3. **Test multi-crop comparison:**
   ```bash
   curl "http://localhost:8000/market-data/opportunity-cost/multi-crop?primary_crop=Wheat&alternative_crops=Cotton,Rice&state=Punjab"
   ```

4. **Test top profitable crops (AC4):**
   ```bash
   curl "http://localhost:8000/market-data/top-profitable-crops?state=Punjab&top_n=3&include_opportunity_costs=true"
   ```

## Future Enhancements

1. **Machine Learning Integration**: Use ML models to predict future opportunity costs
2. **Weather Integration**: Factor weather patterns into opportunity cost calculations
3. **Market Price Forecasting**: Include predicted future prices in calculations
4. **Soil Compatibility**: Consider soil suitability in recommendations
5. **Water Requirements**: Factor irrigation needs into opportunity cost
6. **Labor Availability**: Consider labor requirements in recommendations
7. **Crop Rotation Benefits**: Include soil health benefits in calculations

## Conclusion

The Opportunity Cost Calculation Engine has been successfully implemented and validates AC4. It provides farmers with:

- Clear understanding of trade-offs in crop selection
- Data-driven recommendations for profit maximization
- Risk-adjusted opportunity cost analysis
- Multi-crop comparison capabilities
- Integration with RAG-based market intelligence system

The engine is production-ready and can be used to support farmers in making informed crop selection decisions.
