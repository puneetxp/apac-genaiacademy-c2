# Crop Rotation Optimization Algorithm - Implementation Summary

## Overview

Implemented an enhanced crop rotation optimization algorithm that recommends optimal 2-crop sequences for consecutive seasons, considering soil health, nutrient balance, profit maximization, and crop compatibility.

## Implementation Date

January 2025

## Location

`crop-intelligence-platform/backend/app/services/crop_recommendation_service.py`

## Key Features

### 1. Multi-Factor Optimization

The algorithm considers multiple factors when recommending crop rotations:

- **Profit Maximization** (40% weight): Total annual profit from both crops
- **Crop Compatibility** (30% weight): Agricultural science-based compatibility scores
- **Soil Health Benefits** (20% weight): Nutrient balance and soil structure improvement
- **Risk Diversification** (10% weight): Different crop families for pest/disease management

### 2. Crop Compatibility Matrix

Defined compatibility scores (0.0-1.0) based on:
- Nutrient complementarity (nitrogen fixers + heavy feeders)
- Pest and disease cycle breaking
- Soil structure improvement
- Root depth complementarity

**Example Compatibilities:**
- Legumes (gram, peas, lentil) → Cereals (wheat, rice): 0.90-0.95 (excellent)
- Rice → Wheat: 0.95 (traditional and proven)
- Cotton → Wheat: 0.90 (high profit potential)
- Heavy feeder → Heavy feeder: 0.30 (poor - depletes soil)

### 3. Nutrient Profile System

Categorizes crops by nutrient usage:

**Nitrogen Fixers** (improve soil):
- Gram, peas, lentil, soybean, groundnut
- Add nitrogen to soil, reducing fertilizer needs for next crop

**Heavy Feeders** (deplete soil):
- Rice, cotton, sugarcane, maize
- Require significant nutrients

**Moderate Feeders**:
- Wheat, barley, mustard, sunflower
- Balanced nutrient usage

**Light Feeders**:
- Bajra, jowar
- Minimal nutrient depletion

### 4. Season Sequencing

Follows Indian agricultural seasons:
- **Kharif** (June-October) → **Rabi** (November-April) → **Zaid** (May-June)
- Recommends crops for appropriate seasons based on climate patterns

### 5. Soil Health Benefits Calculation

Evaluates rotation impact on soil:
- **Nitrogen balance**: Improved, restored, neutral, or depleted
- **Soil structure**: Maintained or improved
- **Pest/disease break**: Different crop families reduce pest pressure
- **Organic matter**: Increased, stable, or decreased
- **Overall rating**: Excellent, good, moderate, or poor

### 6. Rotation Scoring Algorithm

```python
final_score = (
    profit_score * 0.40 +
    compatibility_score * 0.30 +
    soil_health_score * 0.20 +
    risk_diversification_score * 0.10
)
```

## Algorithm Flow

1. **Input**: Top 3 profitable crops for the farmer's location
2. **Find Candidates**: Query database for crops suitable for next season(s)
3. **Filter by Compatibility**: Only include crops with compatibility ≥ 0.6
4. **Score Each Rotation**: Calculate multi-factor score for each combination
5. **Rank and Select**: Return top 3 rotations sorted by score
6. **Generate Benefits**: Create human-readable benefits and recommendations

## Example Output

```json
{
  "sequence": "Gram → Wheat",
  "season_1": {
    "crop": "Gram",
    "season": "kharif",
    "expected_profit": 45000
  },
  "season_2": {
    "crop": "Wheat",
    "season": "rabi",
    "expected_profit": 55000
  },
  "total_annual_profit": 100000,
  "rotation_score": 92.5,
  "soil_health_benefits": {
    "nitrogen_balance": "improved",
    "soil_structure": "maintained",
    "pest_disease_break": true,
    "organic_matter": "increased",
    "overall_rating": "excellent"
  },
  "benefits": [
    "Gram fixes nitrogen in soil, reducing fertilizer needs for Wheat",
    "Different crop families break pest and disease cycles",
    "Improved soil organic matter and structure",
    "Optimal land utilization throughout the year",
    "Risk diversification across different crop types",
    "Diversified income streams from different market segments"
  ],
  "recommendation": "Plant Gram in Kharif (monsoon) season, followed by Wheat in Rabi (winter) season. This rotation provides excellent soil health benefits with improved nitrogen balance. Expected annual profit: ₹100,000 per acre. The nitrogen-fixing properties of Gram will reduce fertilizer costs for Wheat."
}
```

## Integration

The algorithm is integrated into the main RAG-based crop recommendation service:

```python
# Called from get_rag_crop_recommendations()
rotation_recommendations = self._generate_crop_rotation_recommendations(
    primary_crops=enhanced_recommendations,
    state=state,
    district=district
)
```

## Benefits for Farmers

1. **Increased Annual Profit**: Optimizes crop selection across both seasons
2. **Reduced Fertilizer Costs**: Nitrogen-fixing crops reduce input costs
3. **Improved Soil Health**: Sustainable farming practices for long-term productivity
4. **Risk Mitigation**: Diversification across crop types and seasons
5. **Pest Management**: Natural pest/disease cycle breaking
6. **Data-Driven Decisions**: Based on historical market data and agricultural science

## Technical Improvements Over Basic Implementation

### Before (Basic Implementation):
- Simple season-based matching
- Limited to 2 rotations
- No soil health consideration
- Basic profit calculation only
- Generic benefits list

### After (Enhanced Implementation):
- Multi-factor optimization with weighted scoring
- Comprehensive crop compatibility matrix
- Detailed nutrient profile system
- Soil health impact assessment
- Risk diversification analysis
- Season-aware sequencing
- Personalized recommendations with context

## Database Dependencies

- `SeasonalTrend`: For finding crops by season and location
- `CropProfitability`: For profit data by crop, season, and location
- Historical market data for informed recommendations

## Future Enhancements

1. **Machine Learning Integration**: Train models on successful rotation outcomes
2. **Weather Pattern Integration**: Consider climate forecasts in rotation planning
3. **Soil Test Integration**: Use actual soil test data for personalized recommendations
4. **Multi-Year Rotations**: Extend to 3-4 crop sequences
5. **Intercropping Recommendations**: Suggest companion planting options
6. **Water Requirement Optimization**: Factor irrigation needs into scoring
7. **Labor Availability**: Consider labor requirements in recommendations

## Validation

The algorithm validates **AC4 requirement**: "RAG system suggests top 3 profitable crops with opportunity cost analysis and 2-crop rotation"

### Test Coverage:
- Unit test: `test_crop_rotation_recommendations` in `tests/test_crop_recommendations.py`
- Validates rotation structure, season sequencing, and profit calculations
- Ensures compatibility with existing RAG recommendation system

## Performance Considerations

- Efficient database queries with proper indexing
- Caching of compatibility matrix and nutrient profiles
- Fallback to common rotations if no data available
- Limits to top 3 rotations to avoid overwhelming farmers

## Code Quality

- Well-documented with inline comments
- Modular design with separate helper methods
- Error handling with fallback mechanisms
- Type hints for better code maintainability
- Follows existing codebase patterns

## Conclusion

The enhanced crop rotation optimization algorithm provides farmers with scientifically-backed, profit-optimized crop sequences that improve soil health and maximize annual returns. It successfully integrates agricultural science principles with data-driven market intelligence to deliver actionable recommendations.
