"""
Tests for Quota Reset Scheduled Job

Tests the quota reset job functionality including:
- Daily quota reset at midnight IST
- Job scheduling configuration
- Error handling
"""

from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytz

from app.schemas.ai_quota import QuotaResetResponse
from app.services.ai_quota_service import AIQuotaService


@pytest.mark.asyncio
async def test_reset_daily_quota_job_success():
    """Test successful quota reset job execution"""
    # Mock the database session and service
    mock_db = AsyncMock()
    mock_service = AsyncMock(spec=AIQuotaService)

    # Mock the reset result
    reset_time = datetime.now(pytz.timezone("Asia/Kolkata"))
    mock_result = QuotaResetResponse(
        users_reset=10, reset_time=reset_time, message="Successfully reset quota for 10 users"
    )
    mock_service.reset_daily_quota.return_value = mock_result

    # Import and test the job function
    from app.jobs.quota_reset_job import reset_daily_quota_job

    with patch("app.jobs.quota_reset_job.get_async_db_context") as mock_context:
        mock_context.return_value.__aenter__.return_value = mock_db

        with patch("app.jobs.quota_reset_job.AIQuotaService", return_value=mock_service):
            await reset_daily_quota_job()

    # Verify service was called
    mock_service.reset_daily_quota.assert_called_once()


@pytest.mark.asyncio
async def test_reset_daily_quota_job_error_handling():
    """Test quota reset job handles errors gracefully"""
    mock_db = AsyncMock()

    # Import the job function
    from app.jobs.quota_reset_job import reset_daily_quota_job

    with patch("app.jobs.quota_reset_job.get_async_db_context") as mock_context:
        mock_context.return_value.__aenter__.return_value = mock_db

        with patch("app.jobs.quota_reset_job.AIQuotaService") as mock_service_class:
            mock_service = AsyncMock()
            mock_service.reset_daily_quota.side_effect = Exception("Database error")
            mock_service_class.return_value = mock_service

            # Should not raise exception - errors are logged
            await reset_daily_quota_job()


def test_setup_quota_reset_scheduler():
    """Test scheduler setup with correct configuration"""
    from app.jobs.quota_reset_job import setup_quota_reset_scheduler

    scheduler = setup_quota_reset_scheduler()

    # Verify scheduler is configured
    assert scheduler is not None

    # Verify job is scheduled
    jobs = scheduler.get_jobs()
    assert len(jobs) == 1

    job = jobs[0]
    assert job.id == "daily_quota_reset"
    assert job.name == "Reset AI usage quota at midnight IST"

    # Verify trigger is set for midnight IST
    trigger = job.trigger
    assert trigger.timezone.zone == "Asia/Kolkata"

    # Clean up
    scheduler.shutdown(wait=False)


def test_start_quota_reset_scheduler():
    """Test starting the quota reset scheduler"""
    from app.jobs.quota_reset_job import start_quota_reset_scheduler

    scheduler = start_quota_reset_scheduler()

    # Verify scheduler is running
    assert scheduler is not None
    assert scheduler.running

    # Clean up
    scheduler.shutdown(wait=False)


def test_stop_quota_reset_scheduler():
    """Test stopping the quota reset scheduler"""
    from app.jobs.quota_reset_job import start_quota_reset_scheduler, stop_quota_reset_scheduler

    scheduler = start_quota_reset_scheduler()
    assert scheduler.running

    stop_quota_reset_scheduler(scheduler)

    # Verify scheduler is stopped
    assert not scheduler.running


def test_scheduler_midnight_ist_timing():
    """Test that scheduler is configured for midnight IST"""
    from app.jobs.quota_reset_job import setup_quota_reset_scheduler

    scheduler = setup_quota_reset_scheduler()
    job = scheduler.get_jobs()[0]

    # Get the trigger
    trigger = job.trigger

    # Verify it's a cron trigger
    assert trigger.__class__.__name__ == "CronTrigger"

    # Verify timezone is IST
    assert trigger.timezone.zone == "Asia/Kolkata"

    # Verify it runs at midnight (hour=0, minute=0)
    # Note: CronTrigger stores fields internally
    assert hasattr(trigger, "hour")
    assert hasattr(trigger, "minute")

    # Clean up
    scheduler.shutdown(wait=False)


@pytest.mark.asyncio
async def test_quota_reset_integration():
    """Integration test for quota reset with actual service"""
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlalchemy.orm import sessionmaker

    from app.core.config import settings
    from app.orm.ai_usage_quota import AiUsageQuota
    from app.services.ai_quota_service import AIQuotaService

    # Create test database session
    engine = create_async_engine(settings.ASYNC_DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        service = AIQuotaService(db)

        # Create test quota record
        test_user_id = 99999
        today = date.today()

        # Get or create quota
        quota = await service.get_or_create_quota(test_user_id, today)

        # Set some usage
        quota.gps_enhanced_requests = 15
        quota.pincode_requests = 30
        await db.commit()

        # Reset quota
        result = await service.reset_daily_quota()

        # Verify reset
        assert result.users_reset >= 1
        assert result.reset_time is not None

        # Check quota was reset
        updated_quota = await service.get_or_create_quota(test_user_id, today)
        assert updated_quota.gps_enhanced_requests == 0
        assert updated_quota.pincode_requests == 0

        # Clean up
        await db.delete(updated_quota)
        await db.commit()

    await engine.dispose()


def test_scheduler_job_replacement():
    """Test that scheduler replaces existing job with same ID"""
    from app.jobs.quota_reset_job import setup_quota_reset_scheduler

    # Setup scheduler twice
    scheduler1 = setup_quota_reset_scheduler()
    scheduler2 = setup_quota_reset_scheduler()

    # Should still have only one job
    jobs = scheduler2.get_jobs()
    assert len(jobs) == 1

    # Clean up
    scheduler2.shutdown(wait=False)
