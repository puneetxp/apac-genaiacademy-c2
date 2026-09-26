"""
Manual Test Script for Quota Reset Job

This script allows manual testing of the quota reset functionality:
1. Creates test quota records with usage
2. Triggers quota reset
3. Verifies reset was successful

Usage:
    python tests/manual_test_quota_reset.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import date, datetime

import pytz
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.orm.ai_usage_quota import AiUsageQuota
from app.services.ai_quota_service import AIQuotaService


async def create_test_quota_records(db: AsyncSession, num_users: int = 5):
    """Create test quota records with usage"""
    print(f"\n📝 Creating {num_users} test quota records...")

    service = AIQuotaService(db)
    today = date.today()

    test_user_ids = []
    for i in range(1, num_users + 1):
        user_id = 90000 + i  # Use high IDs to avoid conflicts
        test_user_ids.append(user_id)

        # Create quota with some usage
        quota = await service.get_or_create_quota(user_id, today)
        quota.gps_enhanced_requests = 10 + i
        quota.pincode_requests = 20 + i
        await db.commit()

        print(
            f"  ✓ User {user_id}: GPS={quota.gps_enhanced_requests}, Pincode={quota.pincode_requests}"
        )

    return test_user_ids


async def display_quota_status(db: AsyncSession, user_ids: list):
    """Display current quota status for users"""
    print("\n📊 Current Quota Status:")

    service = AIQuotaService(db)

    for user_id in user_ids:
        status = await service.get_quota_status(user_id)
        print(f"  User {user_id}:")
        print(f"    GPS Enhanced: {status.gps_enhanced_requests}/{status.quota_limit}")
        print(f"    Pincode: {status.pincode_requests}")
        print(f"    Remaining: {status.remaining_quota}")
        print(f"    Exceeded: {status.quota_exceeded}")


async def test_quota_reset(db: AsyncSession):
    """Test the quota reset functionality"""
    print("\n🔄 Testing Quota Reset...")

    service = AIQuotaService(db)
    result = await service.reset_daily_quota()

    print(f"  ✓ Reset completed!")
    print(f"    Users reset: {result.users_reset}")
    print(f"    Reset time: {result.reset_time}")
    print(f"    Message: {result.message}")

    return result


async def cleanup_test_records(db: AsyncSession, user_ids: list):
    """Clean up test quota records"""
    print("\n🧹 Cleaning up test records...")

    from sqlalchemy import delete

    stmt = delete(AiUsageQuota).where(AiUsageQuota.user_id.in_(user_ids))
    result = await db.execute(stmt)
    await db.commit()

    print(f"  ✓ Deleted {result.rowcount} test records")


async def test_scheduler_configuration():
    """Test the scheduler configuration"""
    print("\n⏰ Testing Scheduler Configuration...")

    try:
        from app.jobs.quota_reset_job import setup_quota_reset_scheduler

        scheduler = setup_quota_reset_scheduler()

        print("  ✓ Scheduler created successfully")

        jobs = scheduler.get_jobs()
        print(f"  ✓ Number of jobs: {len(jobs)}")

        if jobs:
            job = jobs[0]
            print(f"  ✓ Job ID: {job.id}")
            print(f"  ✓ Job Name: {job.name}")
            print(f"  ✓ Timezone: {job.trigger.timezone.zone}")
            print(f"  ✓ Next run: {job.next_run_time}")

        scheduler.shutdown(wait=False)
        print("  ✓ Scheduler shutdown successfully")

        return True
    except Exception as e:
        print(f"  ✗ Scheduler test failed: {e}")
        return False


async def test_manual_trigger():
    """Test manual trigger of quota reset via API endpoint"""
    print("\n🔧 Testing Manual Trigger Endpoint...")

    try:
        import httpx

        # Test the reset endpoint
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://localhost:8000{settings.API_V1_STR}/ai-quota/reset"
            )

            if response.status_code == 200:
                result = response.json()
                print(f"  ✓ Manual trigger successful!")
                print(f"    Users reset: {result['users_reset']}")
                print(f"    Reset time: {result['reset_time']}")
                return True
            else:
                print(f"  ✗ Manual trigger failed: {response.status_code}")
                print(f"    Response: {response.text}")
                return False
    except Exception as e:
        print(f"  ✗ Manual trigger test failed: {e}")
        print(f"    Note: Make sure the FastAPI server is running on localhost:8000")
        return False


async def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 Quota Reset Job Manual Test")
    print("=" * 60)

    # Create database session
    engine = create_async_engine(settings.ASYNC_DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with async_session() as db:
            # Step 1: Create test records
            test_user_ids = await create_test_quota_records(db, num_users=5)

            # Step 2: Display initial status
            await display_quota_status(db, test_user_ids)

            # Step 3: Test quota reset
            await test_quota_reset(db)

            # Step 4: Display status after reset
            await display_quota_status(db, test_user_ids)

            # Step 5: Clean up
            await cleanup_test_records(db, test_user_ids)

        # Step 6: Test scheduler configuration
        scheduler_ok = await test_scheduler_configuration()

        # Step 7: Test manual trigger endpoint (optional)
        print("\n" + "=" * 60)
        print("Would you like to test the manual trigger endpoint?")
        print("(Requires FastAPI server running on localhost:8000)")
        response = input("Test manual trigger? (y/n): ").strip().lower()

        if response == "y":
            await test_manual_trigger()

        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
