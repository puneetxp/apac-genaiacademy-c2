"""
Manual test script for fertilizer tracking functionality

This script demonstrates the fertilizer tracking system:
1. Recording fertilizer applications
2. Updating soil response data
3. Analyzing effectiveness
4. Generating usage reports

Run with: python tests/manual_test_fertilizer_tracking.py
"""

import asyncio
from datetime import datetime, timedelta
from decimal import Decimal


# Mock database session for demonstration
class MockDB:
    def __init__(self):
        self.data = []
        self.id_counter = 1

    def add(self, obj):
        obj.id = self.id_counter
        self.id_counter += 1
        obj.created_at = datetime.now()
        obj.updated_at = datetime.now()
        self.data.append(obj)

    async def commit(self):
        pass

    async def refresh(self, obj):
        pass

    async def execute(self, stmt):
        # Mock execute - return mock result
        class MockResult:
            def scalar_one_or_none(self):
                return self.data[0] if self.data else None

            def scalars(self):
                class MockScalars:
                    def __init__(self, data):
                        self.data = data

                    def all(self):
                        return self.data

                return MockScalars(self.data)

        result = MockResult()
        result.data = self.data
        return result


class MockFertilizerApplication:
    """Mock fertilizer application for demonstration"""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.id = None
        self.created_at = None
        self.updated_at = None


def demonstrate_fertilizer_tracking():
    """Demonstrate fertilizer tracking functionality"""

    print("=" * 80)
    print("FERTILIZER TRACKING SYSTEM DEMONSTRATION")
    print("=" * 80)
    print()

    # 1. Recording a fertilizer application
    print("1. RECORDING FERTILIZER APPLICATION")
    print("-" * 80)

    application_data = {
        "farm_id": 1,
        "application_date": datetime.now(),
        "fertilizer_type": "urea",
        "category": "chemical",
        "quantity_kg": 50.0,
        "cost_total": 1500.0,
        "plot_id": 1,
        "crop_id": 1,
        "area_applied_hectares": 1.0,
        "nitrogen_kg": 23.0,  # Urea is 46% N
        "application_method": "broadcast",
        "growth_stage": "vegetative",
        "days_after_planting": 30,
        "weather_conditions": "Sunny, dry",
        "temperature_celsius": 28.5,
        "rainfall_mm_24h": 0.0,
        "recommended_by": "system",
    }

    print(f"Farm ID: {application_data['farm_id']}")
    print(f"Date: {application_data['application_date'].strftime('%Y-%m-%d')}")
    print(f"Fertilizer: {application_data['fertilizer_type']} ({application_data['category']})")
    print(f"Quantity: {application_data['quantity_kg']} kg")
    print(f"Cost: ₹{application_data['cost_total']}")
    print(f"Nitrogen provided: {application_data['nitrogen_kg']} kg")
    print(f"Application method: {application_data['application_method']}")
    print(f"Growth stage: {application_data['growth_stage']}")
    print(
        f"Weather: {application_data['weather_conditions']}, {application_data['temperature_celsius']}°C"
    )
    print()

    # Calculated metrics
    cost_per_kg = application_data["cost_total"] / application_data["quantity_kg"]
    quantity_per_hectare = (
        application_data["quantity_kg"] / application_data["area_applied_hectares"]
    )

    print("Calculated Metrics:")
    print(f"  Cost per kg: ₹{cost_per_kg:.2f}")
    print(f"  Quantity per hectare: {quantity_per_hectare:.2f} kg/ha")
    print()

    # 2. Soil response monitoring
    print("2. SOIL RESPONSE MONITORING")
    print("-" * 80)

    soil_before = {
        "nitrogen_kg_per_ha": 150.0,
        "phosphorus_kg_per_ha": 20.0,
        "potassium_kg_per_ha": 180.0,
        "soil_health_score": 65.0,
    }

    soil_after = {
        "nitrogen_kg_per_ha": 200.0,  # +50 kg/ha
        "phosphorus_kg_per_ha": 35.0,  # +15 kg/ha
        "potassium_kg_per_ha": 220.0,  # +40 kg/ha
        "soil_health_score": 72.0,  # +7 points
    }

    print("Soil Test Before Application:")
    print(f"  Nitrogen: {soil_before['nitrogen_kg_per_ha']} kg/ha")
    print(f"  Phosphorus: {soil_before['phosphorus_kg_per_ha']} kg/ha")
    print(f"  Potassium: {soil_before['potassium_kg_per_ha']} kg/ha")
    print(f"  Health Score: {soil_before['soil_health_score']}/100")
    print()

    print("Soil Test After Application (30 days later):")
    print(
        f"  Nitrogen: {soil_after['nitrogen_kg_per_ha']} kg/ha (+{soil_after['nitrogen_kg_per_ha'] - soil_before['nitrogen_kg_per_ha']})"
    )
    print(
        f"  Phosphorus: {soil_after['phosphorus_kg_per_ha']} kg/ha (+{soil_after['phosphorus_kg_per_ha'] - soil_before['phosphorus_kg_per_ha']})"
    )
    print(
        f"  Potassium: {soil_after['potassium_kg_per_ha']} kg/ha (+{soil_after['potassium_kg_per_ha'] - soil_before['potassium_kg_per_ha']})"
    )
    print(
        f"  Health Score: {soil_after['soil_health_score']}/100 (+{soil_after['soil_health_score'] - soil_before['soil_health_score']})"
    )
    print()

    # Calculate effectiveness score
    n_improvement = soil_after["nitrogen_kg_per_ha"] - soil_before["nitrogen_kg_per_ha"]
    n_applied = application_data["nitrogen_kg"]
    n_retention = (n_improvement / n_applied) * 100 if n_applied > 0 else 0

    print("Effectiveness Analysis:")
    print(f"  Nitrogen retention rate: {n_retention:.1f}%")
    print(
        f"  Soil health improvement: {soil_after['soil_health_score'] - soil_before['soil_health_score']:.1f} points"
    )

    # Simplified effectiveness score
    effectiveness_score = 0
    if 70 <= n_retention <= 80:
        effectiveness_score += 30
    elif 50 <= n_retention < 70:
        effectiveness_score += 20

    health_improvement = soil_after["soil_health_score"] - soil_before["soil_health_score"]
    if health_improvement >= 5:
        effectiveness_score += 10
    elif health_improvement >= 3:
        effectiveness_score += 7

    print(f"  Overall Effectiveness Score: {effectiveness_score}/100")
    print()

    # 3. Effectiveness analysis
    print("3. FERTILIZER EFFECTIVENESS ANALYSIS")
    print("-" * 80)

    # Mock multiple applications
    applications = [
        {"type": "urea", "category": "chemical", "cost": 1500, "quantity": 50, "effectiveness": 75},
        {"type": "dap", "category": "chemical", "cost": 3000, "quantity": 100, "effectiveness": 80},
        {
            "type": "vermicompost",
            "category": "organic",
            "cost": 2000,
            "quantity": 200,
            "effectiveness": 70,
        },
        {"type": "urea", "category": "chemical", "cost": 1500, "quantity": 50, "effectiveness": 72},
    ]

    total_cost = sum(app["cost"] for app in applications)
    total_quantity = sum(app["quantity"] for app in applications)
    avg_effectiveness = sum(app["effectiveness"] for app in applications) / len(applications)

    print(f"Total Applications: {len(applications)}")
    print(f"Total Cost: ₹{total_cost:,.2f}")
    print(f"Total Quantity: {total_quantity} kg")
    print(f"Average Effectiveness: {avg_effectiveness:.1f}%")
    print()

    # By fertilizer type
    print("Analysis by Fertilizer Type:")
    type_analysis = {}
    for app in applications:
        ftype = app["type"]
        if ftype not in type_analysis:
            type_analysis[ftype] = {"count": 0, "cost": 0, "quantity": 0, "effectiveness": []}
        type_analysis[ftype]["count"] += 1
        type_analysis[ftype]["cost"] += app["cost"]
        type_analysis[ftype]["quantity"] += app["quantity"]
        type_analysis[ftype]["effectiveness"].append(app["effectiveness"])

    for ftype, data in type_analysis.items():
        avg_eff = sum(data["effectiveness"]) / len(data["effectiveness"])
        avg_cost_per_kg = data["cost"] / data["quantity"]
        roi_score = avg_eff / avg_cost_per_kg if avg_cost_per_kg > 0 else 0

        print(f"  {ftype}:")
        print(f"    Applications: {data['count']}")
        print(f"    Total Cost: ₹{data['cost']:,.2f}")
        print(f"    Avg Cost/kg: ₹{avg_cost_per_kg:.2f}")
        print(f"    Avg Effectiveness: {avg_eff:.1f}%")
        print(f"    ROI Score: {roi_score:.2f}")
    print()

    # By category
    print("Analysis by Category:")
    category_analysis = {}
    for app in applications:
        cat = app["category"]
        if cat not in category_analysis:
            category_analysis[cat] = {"count": 0, "cost": 0, "effectiveness": []}
        category_analysis[cat]["count"] += 1
        category_analysis[cat]["cost"] += app["cost"]
        category_analysis[cat]["effectiveness"].append(app["effectiveness"])

    for cat, data in category_analysis.items():
        avg_eff = sum(data["effectiveness"]) / len(data["effectiveness"])
        print(f"  {cat}:")
        print(f"    Applications: {data['count']}")
        print(f"    Total Cost: ₹{data['cost']:,.2f}")
        print(f"    Avg Effectiveness: {avg_eff:.1f}%")
    print()

    # 4. Usage report
    print("4. FERTILIZER USAGE REPORT")
    print("-" * 80)

    print("Report Period: Last 6 months")
    print()

    print("Summary:")
    print(f"  Total Applications: {len(applications)}")
    print(f"  Total Cost: ₹{total_cost:,.2f}")
    print(f"  Total Quantity: {total_quantity} kg")
    print(f"  Avg Cost per Application: ₹{total_cost / len(applications):,.2f}")
    print()

    print("Nutrients Applied:")
    total_n = sum(
        23 if app["type"] == "urea" else 18 if app["type"] == "dap" else 10 for app in applications
    )
    total_p = sum(46 if app["type"] == "dap" else 5 for app in applications)
    total_k = sum(5 for app in applications)
    print(f"  Nitrogen: {total_n} kg")
    print(f"  Phosphorus: {total_p} kg")
    print(f"  Potassium: {total_k} kg")
    print()

    print("Recommendations:")
    print("  ✓ Excellent effectiveness (≥70%). Continue current practices.")
    print("  ✓ Good balance between organic and chemical fertilizers.")
    print("  ✓ Consider soil testing before each application for optimal results.")
    print()

    print("Cost Optimization Tips:")
    print("  • Urea shows best ROI. Consider using more for nitrogen needs.")
    print("  • Continue monitoring and conducting soil tests to maintain optimal rates.")
    print("  • Consider split applications to improve nutrient retention.")
    print()

    print("=" * 80)
    print("DEMONSTRATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    demonstrate_fertilizer_tracking()
