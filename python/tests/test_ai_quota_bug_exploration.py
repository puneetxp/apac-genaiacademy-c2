"""
Bug Condition Exploration Test for AI Quota Query Error

**Validates: Requirements 1.4, 1.5, 1.6**

This test encodes the EXPECTED BEHAVIOR and will FAIL on unfixed code.
The failure confirms the bug exists. When the fix is implemented, this test will pass.

Property 1: Fault Condition - AI Quota Query Success
- Test that get_or_create_quota() executes queries successfully without placeholder errors
- Test that reset_daily_quota() queries records without placeholder mismatch
- Test that status endpoint queries execute without database errors
"""

import pytest
from datetime import date, datetime
import pytz
from typing import Dict, Any

from app.services.ai_quota_service import AIQuotaService
from app.orm.ai_usage_quota import AiUsageQuota


class TestAIQuotaBugCondition:
    """
    Bug condition exploration tests.
    
    CRITICAL: These tests MUST FAIL on unfixed code - failure confirms the bug exists.
    DO NOT attempt to fix the test or the code when it fails.
    
    The bug manifests as: "the query has 0 placeholders but 2 parameters were passed"
    when using and_where_custom() with user_id and date parameters.
    """
    
    @pytest.fixture
    def quota_service(self) -> AIQuotaService:
        """Create AI quota service instance."""
        return AIQuotaService()
    
    @pytest.fixture
    def test_user_id(self) -> int:
        """Test user ID for quota operations."""
        return 99999  # Use high ID to avoid conflicts
    
    @pytest.fixture
    def today(self) -> date:
        """Get today's date in IST timezone."""
        return datetime.now(pytz.timezone('Asia/Kolkata')).date()
    
    def test_get_or_create_quota_query_succeeds(
        self, 
        quota_service: AIQuotaService, 
        test_user_id: int,
        today: date
    ):
        """
        Test that get_or_create_quota() executes database query successfully.
        
        Expected Behavior (Requirement 2.5):
        - Query using and_where_custom() with user_id and date MUST execute successfully
        - Query MUST NOT throw "the query has 0 placeholders but 2 parameters were passed"
        - Method MUST return quota record (either existing or newly created)
        
        EXPECTED OUTCOME: This test FAILS on unfixed code (confirms bug exists)
        
        Bug Condition:
        - The and_where_custom() method is called with [['user_id', '=', user_id], ['date', '=', date]]
        - The ORM builds a query with WHERE clause
        - The query execution fails with placeholder count mismatch
        """
        try:
            # This should work but will fail with placeholder mismatch on unfixed code
            quota = quota_service.get_or_create_quota(test_user_id, today)
            
            # If we get here, the query succeeded
            assert quota is not None, "Quota should not be None"
            assert isinstance(quota, dict), "Quota should be a dictionary"
            assert quota.get('user_id') == test_user_id, f"User ID should be {test_user_id}"
            assert str(quota.get('date')) == str(today), f"Date should be {today}"
            
            print(f"\n✓ Query succeeded for user {test_user_id} on {today}")
            print(f"  Quota record: {quota}")
            
        except Exception as e:
            error_msg = str(e)
            
            # Check if this is the expected bug
            if "placeholders" in error_msg.lower() and "parameters" in error_msg.lower():
                pytest.fail(
                    f"EXPECTED FAILURE: Database query failed with placeholder mismatch error.\n"
                    f"Error: {error_msg}\n"
                    f"This confirms the bug exists in and_where_custom() query execution.\n"
                    f"The query is trying to use user_id={test_user_id} and date={today} "
                    f"but the placeholder binding is incorrect."
                )
            else:
                # Unexpected error - re-raise it
                raise
    
    def test_get_or_create_quota_with_multiple_users(
        self,
        quota_service: AIQuotaService,
        today: date
    ):
        """
        Test that get_or_create_quota() works for multiple different users.
        
        Expected Behavior (Requirement 2.5):
        - Queries for different user_id values MUST all succeed
        - Each query MUST correctly bind the user_id parameter
        - No placeholder mismatch errors should occur
        
        EXPECTED OUTCOME: This test FAILS on unfixed code (confirms bug exists)
        """
        test_user_ids = [99991, 99992, 99993]
        results = []
        
        for user_id in test_user_ids:
            try:
                quota = quota_service.get_or_create_quota(user_id, today)
                results.append({
                    'user_id': user_id,
                    'success': True,
                    'quota': quota
                })
                print(f"\n✓ Query succeeded for user {user_id}")
                
            except Exception as e:
                error_msg = str(e)
                results.append({
                    'user_id': user_id,
                    'success': False,
                    'error': error_msg
                })
                
                if "placeholders" in error_msg.lower() and "parameters" in error_msg.lower():
                    print(f"\n✗ Query failed for user {user_id}: {error_msg}")
        
        # Check if any queries failed
        failed_queries = [r for r in results if not r['success']]
        
        if failed_queries:
            failure_details = "\n".join([
                f"  User {r['user_id']}: {r['error']}"
                for r in failed_queries
            ])
            pytest.fail(
                f"EXPECTED FAILURE: {len(failed_queries)}/{len(test_user_ids)} queries failed.\n"
                f"Failed queries:\n{failure_details}\n"
                f"This confirms the bug exists in and_where_custom() query execution."
            )
        
        # All queries succeeded
        assert len(results) == len(test_user_ids), "All queries should complete"
        assert all(r['success'] for r in results), "All queries should succeed"
    
    def test_quota_status_endpoint_query_succeeds(
        self,
        quota_service: AIQuotaService,
        test_user_id: int
    ):
        """
        Test that get_quota_status() executes database query successfully.
        
        Expected Behavior (Requirement 2.7):
        - GET /api/v1/ai-quota/status/{user_id} MUST execute successfully
        - Underlying get_or_create_quota() query MUST NOT throw placeholder errors
        - Endpoint MUST return quota status without 500 errors
        
        EXPECTED OUTCOME: This test FAILS on unfixed code (confirms bug exists)
        
        This simulates the actual API endpoint call that's failing in production.
        """
        import asyncio
        
        async def test_status():
            try:
                # This calls get_or_create_quota() internally
                status = await quota_service.get_quota_status(test_user_id)
                
                # If we get here, the query succeeded
                assert status is not None, "Status should not be None"
                assert status.user_id == test_user_id, f"User ID should be {test_user_id}"
                
                print(f"\n✓ Status query succeeded for user {test_user_id}")
                print(f"  GPS Enhanced: {status.gps_enhanced_requests}/{status.quota_limit}")
                print(f"  Pincode: {status.pincode_requests}")
                print(f"  Remaining: {status.remaining_quota}")
                
                return True
                
            except Exception as e:
                error_msg = str(e)
                
                if "placeholders" in error_msg.lower() and "parameters" in error_msg.lower():
                    pytest.fail(
                        f"EXPECTED FAILURE: Status endpoint query failed with placeholder error.\n"
                        f"Error: {error_msg}\n"
                        f"This confirms the bug exists - the /api/v1/ai-quota/status/{{user_id}} "
                        f"endpoint is failing with database query errors.\n"
                        f"This matches the production error: 'the query has 0 placeholders but 2 parameters were passed'"
                    )
                else:
                    raise
        
        # Run the async test
        asyncio.run(test_status())
    
    def test_reset_daily_quota_query_succeeds(
        self,
        quota_service: AIQuotaService,
        today: date
    ):
        """
        Test that reset_daily_quota() executes database queries successfully.
        
        Expected Behavior (Requirement 2.6):
        - Quota reset job MUST query records successfully
        - Query using where() with date parameter MUST execute without errors
        - Reset operation MUST complete without placeholder mismatch errors
        
        EXPECTED OUTCOME: This test FAILS on unfixed code (confirms bug exists)
        
        This simulates the midnight IST quota reset job that's failing.
        """
        import asyncio
        
        async def test_reset():
            try:
                # First create some test quota records
                test_user_ids = [99994, 99995]
                for user_id in test_user_ids:
                    quota_service.get_or_create_quota(user_id, today)
                
                print(f"\n✓ Created test quota records for {len(test_user_ids)} users")
                
                # Now try to reset - this queries records by date
                result = await quota_service.reset_daily_quota()
                
                # If we get here, the reset succeeded
                assert result is not None, "Reset result should not be None"
                assert result.users_reset >= 0, "Users reset count should be non-negative"
                
                print(f"\n✓ Reset query succeeded")
                print(f"  Users reset: {result.users_reset}")
                print(f"  Reset time: {result.reset_time}")
                
                return True
                
            except Exception as e:
                error_msg = str(e)
                
                if "placeholders" in error_msg.lower() and "parameters" in error_msg.lower():
                    pytest.fail(
                        f"EXPECTED FAILURE: Reset quota query failed with placeholder error.\n"
                        f"Error: {error_msg}\n"
                        f"This confirms the bug exists - the midnight IST quota reset job "
                        f"is failing when it tries to query quota records by date.\n"
                        f"This matches the production error from the scheduled job."
                    )
                else:
                    raise
        
        # Run the async test
        asyncio.run(test_reset())
    
    def test_orm_and_where_custom_with_two_conditions(self):
        """
        Test the ORM and_where_custom() method directly with two conditions.
        
        Expected Behavior (Requirement 2.5):
        - and_where_custom() with two conditions MUST build query correctly
        - Query MUST have correct number of placeholders for parameters
        - Query execution MUST succeed without placeholder mismatch
        
        EXPECTED OUTCOME: This test FAILS on unfixed code (confirms bug exists)
        
        This is a focused test on the exact ORM method that's causing the issue.
        """
        try:
            # Try to query with and_where_custom using two conditions
            result = AiUsageQuota().and_where_custom([
                ['user_id', '=', 99996],
                ['date', '=', '2024-01-01']
            ]).first()
            
            # If we get here, the query succeeded (or returned None if no records)
            print(f"\n✓ ORM and_where_custom() query succeeded")
            print(f"  Result: {result.items if result else 'No records found'}")
            
            # The query should execute without errors
            # Result can be None if no matching records exist, that's fine
            
        except Exception as e:
            error_msg = str(e)
            
            if "placeholders" in error_msg.lower() and "parameters" in error_msg.lower():
                pytest.fail(
                    f"EXPECTED FAILURE: ORM and_where_custom() failed with placeholder error.\n"
                    f"Error: {error_msg}\n"
                    f"This confirms the root cause - the and_where_custom() method is not "
                    f"correctly binding parameters when building queries with multiple conditions.\n"
                    f"The query builder is creating a mismatch between placeholder count and parameter count."
                )
            else:
                raise
    
    def test_usage_statistics_query_with_date_range(
        self,
        quota_service: AIQuotaService
    ):
        """
        Test that get_usage_statistics() executes queries successfully.
        
        Expected Behavior (Requirement 2.5):
        - Statistics query using and_where_custom() with date range MUST succeed
        - Query with >= and <= operators MUST bind parameters correctly
        - No placeholder mismatch errors should occur
        
        EXPECTED OUTCOME: This test FAILS on unfixed code (confirms bug exists)
        """
        import asyncio
        from datetime import timedelta
        
        async def test_statistics():
            try:
                today = date.today()
                start_date = today - timedelta(days=7)
                end_date = today
                
                # This uses and_where_custom() with date range conditions
                stats = await quota_service.get_usage_statistics(start_date, end_date)
                
                # If we get here, the query succeeded
                assert stats is not None, "Statistics should not be None"
                assert 'total_users' in stats, "Statistics should contain total_users"
                
                print(f"\n✓ Statistics query succeeded for date range {start_date} to {end_date}")
                print(f"  Total users: {stats['total_users']}")
                print(f"  Total GPS requests: {stats['total_gps_requests']}")
                
                return True
                
            except Exception as e:
                error_msg = str(e)
                
                if "placeholders" in error_msg.lower() and "parameters" in error_msg.lower():
                    pytest.fail(
                        f"EXPECTED FAILURE: Statistics query failed with placeholder error.\n"
                        f"Error: {error_msg}\n"
                        f"This confirms the bug also affects date range queries using >= and <= operators."
                    )
                else:
                    raise
        
        # Run the async test
        asyncio.run(test_statistics())


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
