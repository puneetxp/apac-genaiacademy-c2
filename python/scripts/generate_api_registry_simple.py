#!/usr/bin/env python3
"""
Generate API Registry JSON - Simple version without importing FastAPI app
This script manually defines all API endpoints based on the codebase structure.
"""

import json
from pathlib import Path
from datetime import datetime


def generate_api_registry() -> dict:
    """Generate API registry with all known endpoints"""
    
    registry = {
        "$schema": "./api-registry-schema.json",
        "version": "1.0.0",
        "generatedAt": datetime.utcnow().isoformat() + 'Z',
        "baseUrl": "http://localhost:8000",
        "apiVersion": "v1",
        "endpoints": {
            "auth": {
                "login": "/api/v1/auth/signin",
                "signup": "/api/v1/auth/signup",
                "logout": "/api/v1/auth/logout",
                "refresh": "/api/v1/auth/refresh",
                "verifyEmail": "/api/v1/auth/verify-email",
                "resendVerification": "/api/v1/auth/resend-verification",
                "forgotPassword": "/api/v1/auth/forgot-password",
                "resetPassword": "/api/v1/auth/reset-password",
                "me": "/api/v1/auth/user"
            },
            "users": {
                "getProfile": "/api/v1/users/profile",
                "updateProfile": "/api/v1/users/profile",
                "changePassword": "/api/v1/users/change-password"
            },
            "farms": {
                "list": "/api/v1/farms",
                "create": "/api/v1/farms",
                "get": "/api/v1/farms/{id}",
                "update": "/api/v1/farms/{id}",
                "delete": "/api/v1/farms/{id}",
                "plots": "/api/v1/farms/{id}/plots"
            },
            "crops": {
                "annualStrategy": "/api/v1/annual-strategy",
                "recommendations": "/api/v1/crop-recommendations",
                "yieldPrediction": "/api/v1/yield-predictions",
                "saveStrategy": "/api/v1/annual-strategy/save",
                "getStrategy": "/api/v1/annual-strategy/{id}",
                "listStrategies": "/api/v1/annual-strategy/list",
                "myStrategies": "/api/v1/annual-strategy/list",
                "updateStatus": "/api/v1/annual-strategy/{id}/status",
                "addFeedback": "/api/v1/annual-strategy/{id}/feedback",
                "updateYield": "/api/v1/yield-predictions/{id}",
                "checkHarvest": "/api/v1/crops/harvest-readiness/{crop_id}",
                "harvestAlert": "/api/v1/crops/harvest-alert/{crop_id}"
            },
            "cropMilestones": {
                "list": "/api/v1/crop-milestones",
                "create": "/api/v1/crop-milestones",
                "get": "/api/v1/crop-milestones/{id}",
                "update": "/api/v1/crop-milestones/{id}",
                "complete": "/api/v1/crop-milestones/{id}/complete"
            },
            "marketplace": {
                "listings": "/api/v1/marketplace/listings",
                "createListing": "/api/v1/marketplace/listings",
                "getListing": "/api/v1/marketplace/listings/{id}",
                "updateListing": "/api/v1/marketplace/listings/{id}",
                "deleteListing": "/api/v1/marketplace/listings/{id}",
                "search": "/api/v1/marketplace/search",
                "myListings": "/api/v1/marketplace/my-listings"
            },
            "advanceBooking": {
                "create": "/api/v1/marketplace/advance-bookings",
                "list": "/api/v1/marketplace/advance-bookings",
                "get": "/api/v1/marketplace/advance-bookings/{id}",
                "update": "/api/v1/marketplace/advance-bookings/{id}",
                "cancel": "/api/v1/marketplace/advance-bookings/{id}/cancel",
                "confirm": "/api/v1/marketplace/advance-bookings/{id}/confirm",
                "complete": "/api/v1/marketplace/advance-bookings/{id}/complete",
                "qualityVerify": "/api/v1/marketplace/advance-bookings/{id}/quality-verify"
            },
            "marketData": {
                "prices": "/api/v1/market-data/prices",
                "trends": "/api/v1/market-data/trends",
                "forecast": "/api/v1/market-data/forecast"
            },
            "marketIntelligence": {
                "priceTracking": "/api/v1/market-intelligence/price-tracking",
                "priceHistory": "/api/v1/market-intelligence/price-history",
                "trends": "/api/v1/market-intelligence/trends/{item_type}/{item_name}",
                "qualityPremiums": "/api/v1/market-intelligence/quality-premiums/{item_type}/{item_name}",
                "demandForecast": "/api/v1/market-intelligence/demand-forecast/{item_type}/{item_name}",
                "summary": "/api/v1/market-intelligence/summary",
                "dashboard": "/api/v1/market-intelligence/dashboard"
            },
            "predictiveAnalytics": {
                "predictPrice": "/api/v1/predictive-analytics/predict-price",
                "predictDemand": "/api/v1/predictive-analytics/predict-demand",
                "supplyDemandGaps": "/api/v1/predictive-analytics/supply-demand-gaps",
                "opportunityScore": "/api/v1/predictive-analytics/opportunity-score",
                "buyerSupplyPlanning": "/api/v1/predictive-analytics/buyer-supply-planning"
            },
            "notifications": {
                "subscribe": "/api/v1/notifications/subscribe",
                "unsubscribe": "/api/v1/notifications/unsubscribe",
                "send": "/api/v1/notifications/send"
            },
            "weather": {
                "current": "/api/v1/weather/current",
                "forecast": "/api/v1/weather/forecast",
                "alerts": "/api/v1/weather/alerts",
                "severe": "/api/v1/severe-weather/alerts",
                "recommendations": "/api/v1/weather-recommendations"
            },
            "soil": {
                "tests": "/api/v1/soil-testing/tests",
                "createTest": "/api/v1/soil-testing/tests",
                "getTest": "/api/v1/soil-testing/tests/{id}",
                "maps": "/api/v1/soil-maps",
                "health": "/api/v1/soil-health/{plot_id}",
                "recommendations": "/api/v1/soil/recommendations"
            },
            "fertilizer": {
                "recommendations": "/api/v1/fertilizer-recommendations",
                "tracking": "/api/v1/fertilizer-tracking",
                "applications": "/api/v1/fertilizer-tracking/applications",
                "history": "/api/v1/fertilizer-tracking/history/{plot_id}"
            },
            "pestDisease": {
                "alerts": "/api/v1/pest-disease/alerts",
                "identify": "/api/v1/pest-disease/identify",
                "treatments": "/api/v1/pest-disease/treatments",
                "history": "/api/v1/pest-disease/history/{crop_id}"
            },
            "livestock": {
                "list": "/api/v1/livestock",
                "create": "/api/v1/livestock",
                "get": "/api/v1/livestock/{id}",
                "update": "/api/v1/livestock/{id}",
                "delete": "/api/v1/livestock/{id}",
                "health": "/api/v1/livestock-health/{id}",
                "nutrition": "/api/v1/livestock-nutrition/{id}",
                "breeding": "/api/v1/livestock-breeding",
                "vaccinations": "/api/v1/vaccination-reminders",
                "veterinary": "/api/v1/veterinary/appointments"
            },
            "livestockTransactions": {
                "create": "/api/v1/livestock-transactions",
                "list": "/api/v1/livestock-transactions",
                "get": "/api/v1/livestock-transactions/{id}",
                "update": "/api/v1/livestock-transactions/{id}",
                "cancel": "/api/v1/livestock-transactions/{id}/cancel"
            },
            "transport": {
                "providers": "/api/v1/transport/providers",
                "bookings": "/api/v1/transport/bookings",
                "createBooking": "/api/v1/transport/bookings",
                "tracking": "/api/v1/transport/tracking/{booking_id}"
            },
            "plotAnalysis": {
                "analyze": "/api/v1/plot-analysis/analyze",
                "profitability": "/api/v1/plot-analysis/profitability",
                "history": "/api/v1/plot-analysis/history/{plot_id}",
                "publish": "/api/v1/plot-publishing/publish",
                "listings": "/api/v1/plot-publishing/listings"
            },
            "aiQuota": {
                "getStatus": "/api/v1/ai-quota/status/{user_id}",
                "check": "/api/v1/ai-quota/check",
                "increment": "/api/v1/ai-quota/increment",
                "reset": "/api/v1/ai-quota/reset",
                "updateLimit": "/api/v1/ai-quota/limit/{user_id}",
                "statistics": "/api/v1/ai-quota/statistics"
            },
            "address": {
                "lookupPincode": "/api/v1/address/pincode/{pincode}",
                "validate": "/api/v1/address/validate"
            },
            "analytics": {
                "dashboard": "/api/v1/analytics/dashboard",
                "farmPerformance": "/api/v1/analytics/farm-performance",
                "cropPerformance": "/api/v1/analytics/crop-performance",
                "marketTrends": "/api/v1/analytics/market-trends"
            },
            "upload": {
                "image": "/api/v1/upload/image",
                "document": "/api/v1/upload/document"
            },
            "health": {
                "check": "/health",
                "ready": "/health/ready",
                "live": "/health/live"
            }
        }
    }
    
    return registry


def generate_typescript_helper():
    """Generate TypeScript helper for using the API registry"""
    
    ts_content = """// Auto-generated TypeScript helper for API Registry
// Generated by scripts/generate_api_registry_simple.py

import apiRegistry from './api-registry.json';

export type ApiEndpoints = typeof apiRegistry.endpoints;

// Helper function to build URL with parameters
export function buildApiUrl(
  endpoint: string,
  params?: Record<string, string | number>
): string {
  let url = endpoint;
  
  if (params) {
    for (const [key, value] of Object.entries(params)) {
      url = url.replace(`{${key}}`, String(value));
    }
  }
  
  // Return just the path - api-client will prepend baseURL
  return url;
}

// Helper to get endpoint by category and name
export function getEndpoint(
  category: keyof ApiEndpoints,
  name: string
): string {
  const endpoints = apiRegistry.endpoints[category] as Record<string, string>;
  if (!endpoints || !endpoints[name]) {
    throw new Error(`Endpoint not found: ${category}.${name}`);
  }
  return endpoints[name];
}

// Helper to build full URL by category and name
export function buildUrl(
  category: keyof ApiEndpoints,
  name: string,
  params?: Record<string, string | number>
): string {
  const endpoint = getEndpoint(category, name);
  return buildApiUrl(endpoint, params);
}

// Export the registry
export { apiRegistry };
export default apiRegistry;
"""
    
    return ts_content


def main():
    """Main function to generate and save API registry"""
    print("Generating API registry...")
    
    registry = generate_api_registry()
    
    # Determine output path
    script_dir = Path(__file__).parent
    output_dir = script_dir.parent.parent / 'solidjs' / 'src' / 'config'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Write JSON file
    output_file = output_dir / 'api-registry.json'
    with open(output_file, 'w') as f:
        json.dump(registry, f, indent=2)
    
    print(f"✓ API registry generated: {output_file}")
    
    # Count endpoints
    total_endpoints = sum(len(v) for v in registry['endpoints'].values())
    print(f"✓ Total endpoints: {total_endpoints}")
    print(f"✓ Categories: {len(registry['endpoints'])}")
    
    # Generate TypeScript helper
    ts_content = generate_typescript_helper()
    ts_file = output_dir / 'api-registry.ts'
    with open(ts_file, 'w') as f:
        f.write(ts_content)
    
    print(f"✓ TypeScript helper generated: {ts_file}")
    print("\nDone! Frontend can now import and use the API registry.")


if __name__ == '__main__':
    main()
