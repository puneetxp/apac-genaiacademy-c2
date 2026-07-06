#!/usr/bin/env python3
"""
Quick test to verify AI quota import fix
Run this after activating venv: source venv/bin/activate
"""

print("Testing AI Quota imports...")

try:
    from app.orm.ai_usage_quota import AiUsageQuota
    print("✓ Successfully imported AiUsageQuota from app.orm.ai_usage_quota")
    print(f"  Class name: {AiUsageQuota.__name__}")
    print(f"  Table: {AiUsageQuota.table}")
except ImportError as e:
    print(f"✗ Failed to import AiUsageQuota: {e}")
    exit(1)

try:
    from app.services.ai_quota_service import AIQuotaService
    print("✓ Successfully imported AIQuotaService from app.services.ai_quota_service")
    service = AIQuotaService()
    print(f"  Service model: {service.model.__name__}")
    assert service.model == AiUsageQuota, "Service should use AiUsageQuota model"
    print("✓ Service correctly uses AiUsageQuota model")
except ImportError as e:
    print(f"✗ Failed to import AIQuotaService: {e}")
    exit(1)
except AssertionError as e:
    print(f"✗ Service model mismatch: {e}")
    exit(1)

print("\n✅ All imports working correctly!")
print("\nNext steps:")
print("1. Restart backend: pkill -f 'uvicorn app.main:app' && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
print("2. Test endpoint: curl http://localhost:8000/api/v1/ai-quota/status/1")
