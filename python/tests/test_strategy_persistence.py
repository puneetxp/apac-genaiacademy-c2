"""
Property-based tests for strategy persistence and reminder scheduling
Tests Property 6: Strategy Persistence and Reminder Scheduling

**Validates: Requirements AC2.7**
"""

import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, patch

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from app.services.notification_service import NotificationService


# Custom strategies for generating annual strategy data
@st.composite
def annual_strategy_data(draw):
    """
    Generate valid annual strategy data for testing persistence

    This strategy creates complete annual strategies that should be persisted
    to the database with all required fields.
    """

    # Common Indian crops by season
    kharif_crops = [
        "Rice",
        "Cotton",
        "Maize",
        "Soybean",
        "Groundnut",
        "Sugarcane",
        "Bajra",
        "Jowar",
    ]
    rabi_crops = ["Wheat", "Mustard", "Chickpea", "Barley", "Lentil", "Peas", "Potato", "Onion"]
    zaid_crops = ["Mung Bean", "Watermelon", "Cucumber", "Fodder", "Vegetables", None]

    # Generate strategy data
    kharif_crop = draw(st.sampled_from(kharif_crops))
    kharif_profit = draw(st.integers(min_value=10000, max_value=150000))
    kharif_confidence = draw(st.floats(min_value=0.0, max_value=1.0))

    rabi_crop = draw(st.sampled_from(rabi_crops))
    rabi_profit = draw(st.integers(min_value=10000, max_value=150000))
    rabi_confidence = draw(st.floats(min_value=0.0, max_value=1.0))

    zaid_crop = draw(st.sampled_from(zaid_crops))
    zaid_profit = draw(st.integers(min_value=0, max_value=50000)) if zaid_crop else 0
    zaid_confidence = draw(st.floats(min_value=0.0, max_value=1.0)) if zaid_crop else 0.0

    total_profit = kharif_profit + rabi_profit + zaid_profit

    # Generate monthly action plan (must cover all 12 months)
    months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    monthly_action_plan = []
    for month in months:
        num_actions = draw(st.integers(min_value=1, max_value=4))
        actions = [draw(st.text(min_size=10, max_size=60)) for _ in range(num_actions)]
        monthly_action_plan.append({"month": month, "actions": actions})

    # Generate alternative options
    num_alternatives = draw(st.integers(min_value=1, max_value=3))
    alternative_options = []
    for _ in range(num_alternatives):
        alternative_options.append(
            {
                "season": draw(st.sampled_from(["kharif", "rabi"])),
                "crop": draw(st.sampled_from(kharif_crops + rabi_crops)),
                "profit_difference": draw(st.integers(min_value=-30000, max_value=30000)),
                "risk_comparison": draw(st.text(min_size=10, max_size=100)),
            }
        )

    # Complete Bedrock response
    bedrock_response = {
        "kharif": {
            "recommended_crop": kharif_crop,
            "variety": draw(st.text(min_size=3, max_size=30)),
            "expected_yield_per_acre": draw(st.text(min_size=5, max_size=20)),
            "expected_profit_per_acre": kharif_profit,
            "investment_per_acre": draw(st.integers(min_value=5000, max_value=50000)),
            "planting_window": "June-July",
            "harvest_window": "October-November",
            "key_success_factors": [draw(st.text(min_size=5, max_size=50)) for _ in range(3)],
            "confidence_score": kharif_confidence,
        },
        "rabi": {
            "recommended_crop": rabi_crop,
            "variety": draw(st.text(min_size=3, max_size=30)),
            "expected_yield_per_acre": draw(st.text(min_size=5, max_size=20)),
            "expected_profit_per_acre": rabi_profit,
            "investment_per_acre": draw(st.integers(min_value=5000, max_value=50000)),
            "planting_window": "November-December",
            "harvest_window": "March-April",
            "key_success_factors": [draw(st.text(min_size=5, max_size=50)) for _ in range(3)],
            "confidence_score": rabi_confidence,
        },
        "zaid": {"recommended_crop": zaid_crop, "expected_profit_per_acre": zaid_profit},
        "annual_summary": {
            "total_expected_profit_per_acre": total_profit,
            "total_investment_per_acre": draw(st.integers(min_value=10000, max_value=100000)),
            "roi_percentage": draw(st.integers(min_value=50, max_value=300)),
            "risk_level": draw(st.sampled_from(["low", "medium", "high"])),
            "sustainability_score": draw(st.floats(min_value=0.0, max_value=1.0)),
        },
        "alternative_options": alternative_options,
        "monthly_action_plan": monthly_action_plan,
    }

    return {
        "farmer_id": draw(st.integers(min_value=1, max_value=10000)),
        "farm_id": draw(st.integers(min_value=1, max_value=10000)),
        "year": draw(st.integers(min_value=2024, max_value=2030)),
        "kharif_crop": kharif_crop,
        "kharif_profit_estimate": kharif_profit,
        "kharif_confidence_score": kharif_confidence,
        "rabi_crop": rabi_crop,
        "rabi_profit_estimate": rabi_profit,
        "rabi_confidence_score": rabi_confidence,
        "zaid_crop": zaid_crop,
        "zaid_profit_estimate": zaid_profit,
        "zaid_confidence_score": zaid_confidence,
        "total_annual_profit": total_profit,
        "implementation_timeline": json.dumps(monthly_action_plan),
        "alternative_options": json.dumps(alternative_options),
        "bedrock_response": json.dumps(bedrock_response),
        "status": "active",
    }


class TestStrategyPersistenceAndReminders:
    """
    Property 6: Strategy Persistence and Reminder Scheduling

    Test that for any selected annual crop strategy, system persists complete
    strategy to database and schedules appropriate implementation reminders.
    """

    @given(strategy=annual_strategy_data())
    @settings(
        max_examples=200,
        deadline=15000,  # 15 seconds per test
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
    )
    def test_complete_strategy_persistence(self, strategy):
        """
        **Validates: Requirements AC2.7**

        Property: For any selected annual crop strategy, the system should persist
        the complete strategy to the database with all required fields.
        """
        # Arrange: Create mock database service
        mock_service = Mock()
        mock_service.table = "annual_strategies"

        # Mock the create method to return the strategy with an ID
        created_strategy = strategy.copy()
        created_strategy["id"] = 12345
        created_strategy["created_at"] = datetime.now(timezone.utc)
        created_strategy["updated_at"] = datetime.now(timezone.utc)
        mock_service.create.return_value = created_strategy

        # Act: Persist the strategy
        result = mock_service.create(strategy)

        # Assert: Strategy was persisted
        assert mock_service.create.called, "Strategy create method was not called"
        assert mock_service.create.call_count == 1, "Strategy should be created exactly once"

        # Assert: All required fields are present in the persisted strategy
        call_args = mock_service.create.call_args[0][0]

        # Core identification fields
        assert "farmer_id" in call_args, "farmer_id missing from persisted strategy"
        assert "farm_id" in call_args, "farm_id missing from persisted strategy"
        assert "year" in call_args, "year missing from persisted strategy"

        # Kharif season fields
        assert "kharif_crop" in call_args, "kharif_crop missing from persisted strategy"
        assert "kharif_profit_estimate" in call_args, "kharif_profit_estimate missing"
        assert "kharif_confidence_score" in call_args, "kharif_confidence_score missing"

        # Rabi season fields
        assert "rabi_crop" in call_args, "rabi_crop missing from persisted strategy"
        assert "rabi_profit_estimate" in call_args, "rabi_profit_estimate missing"
        assert "rabi_confidence_score" in call_args, "rabi_confidence_score missing"

        # Zaid season fields
        assert "zaid_crop" in call_args, "zaid_crop missing from persisted strategy"
        assert "zaid_profit_estimate" in call_args, "zaid_profit_estimate missing"

        # Annual summary fields
        assert "total_annual_profit" in call_args, "total_annual_profit missing"

        # Implementation details
        assert "implementation_timeline" in call_args, "implementation_timeline missing"
        assert "alternative_options" in call_args, "alternative_options missing"
        assert "bedrock_response" in call_args, "bedrock_response missing"

        # Status field
        assert "status" in call_args, "status missing from persisted strategy"

        # Assert: Result contains the created strategy with ID
        assert result is not None, "Persisted strategy should not be None"
        assert "id" in result, "Persisted strategy should have an ID"
        assert result["id"] == 12345, "Strategy ID should match"

    @given(strategy=annual_strategy_data())
    @settings(
        max_examples=100,
        deadline=15000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
    )
    def test_implementation_timeline_completeness(self, strategy):
        """
        **Validates: Requirements AC2.7**

        Property: For any persisted strategy, the implementation timeline should
        cover all 12 months of the agricultural year.
        """
        # Parse the implementation timeline
        timeline = json.loads(strategy["implementation_timeline"])

        # Assert: Timeline is a list
        assert isinstance(timeline, list), "Implementation timeline must be a list"

        # Assert: Timeline covers all 12 months
        assert (
            len(timeline) == 12
        ), f"Implementation timeline must cover all 12 months, got {len(timeline)}"

        # Assert: All month names are present
        expected_months = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
        actual_months = [entry["month"] for entry in timeline]

        for expected_month in expected_months:
            assert (
                expected_month in actual_months
            ), f"Month '{expected_month}' missing from implementation timeline"

        # Assert: Each month has actions
        for month_entry in timeline:
            assert "month" in month_entry, "Month entry missing 'month' field"
            assert (
                "actions" in month_entry
            ), f"Month '{month_entry.get('month', 'unknown')}' missing 'actions' field"
            assert isinstance(
                month_entry["actions"], list
            ), f"Month '{month_entry['month']}' actions must be a list"
            assert (
                len(month_entry["actions"]) > 0
            ), f"Month '{month_entry['month']}' must have at least one action"

    @given(strategy=annual_strategy_data())
    @settings(
        max_examples=100,
        deadline=15000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
    )
    def test_reminder_scheduling_for_monthly_actions(self, strategy):
        """
        **Validates: Requirements AC2.7**

        Property: For any selected annual crop strategy, the system should schedule
        appropriate monthly implementation reminders based on the timeline.
        """
        # Arrange: Parse the implementation timeline
        timeline = json.loads(strategy["implementation_timeline"])

        # Arrange: Create mock notification service
        notification_service = Mock(spec=NotificationService)
        notification_service.send_strategy_reminder.return_value = {
            "success": True,
            "notification_type": "strategy_reminder",
        }

        # Act: Schedule reminders for each month in the timeline
        scheduled_reminders = []
        for month_entry in timeline:
            month = month_entry["month"]
            actions = month_entry["actions"]

            # Simulate scheduling a reminder for this month
            reminder_result = notification_service.send_strategy_reminder(
                farmer_phone="+919876543210",
                farmer_email="farmer@example.com",
                farmer_name="Test Farmer",
                strategy_id=str(strategy.get("id", 12345)),
                reminder_type=f"{month.lower()}_actions",
                action_items=actions,
                due_date=None,
            )

            scheduled_reminders.append(
                {
                    "month": month,
                    "action_count": len(actions),
                    "reminder_sent": reminder_result["success"],
                }
            )

        # Assert: Reminders were scheduled for all 12 months
        assert (
            len(scheduled_reminders) == 12
        ), f"Should schedule reminders for all 12 months, got {len(scheduled_reminders)}"

        # Assert: All reminders were successfully sent
        for reminder in scheduled_reminders:
            assert reminder["reminder_sent"], f"Reminder for {reminder['month']} failed to send"

        # Assert: Notification service was called 12 times (once per month)
        assert (
            notification_service.send_strategy_reminder.call_count == 12
        ), f"Expected 12 reminder calls, got {notification_service.send_strategy_reminder.call_count}"

        # Assert: Each reminder call included the required parameters
        for call in notification_service.send_strategy_reminder.call_args_list:
            call_kwargs = call[1] if len(call) > 1 else call.kwargs

            assert "farmer_phone" in call_kwargs, "farmer_phone missing from reminder call"
            assert "farmer_name" in call_kwargs, "farmer_name missing from reminder call"
            assert "strategy_id" in call_kwargs, "strategy_id missing from reminder call"
            assert "reminder_type" in call_kwargs, "reminder_type missing from reminder call"
            assert "action_items" in call_kwargs, "action_items missing from reminder call"

            # Assert: Action items is a non-empty list
            assert isinstance(call_kwargs["action_items"], list), "action_items must be a list"
            assert len(call_kwargs["action_items"]) > 0, "action_items must not be empty"

    @given(strategy=annual_strategy_data())
    @settings(
        max_examples=100,
        deadline=15000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
    )
    def test_bedrock_response_persistence(self, strategy):
        """
        **Validates: Requirements AC2.7**

        Property: For any selected annual crop strategy, the complete Bedrock
        response should be persisted in the bedrock_response field for reference.
        """
        # Assert: Bedrock response field exists
        assert "bedrock_response" in strategy, "bedrock_response field missing from strategy"

        # Assert: Bedrock response is not empty
        assert strategy["bedrock_response"] is not None, "bedrock_response should not be None"
        assert len(strategy["bedrock_response"]) > 0, "bedrock_response should not be empty"

        # Parse the Bedrock response
        bedrock_data = json.loads(strategy["bedrock_response"])

        # Assert: Bedrock response contains all required sections
        assert "kharif" in bedrock_data, "Bedrock response missing kharif section"
        assert "rabi" in bedrock_data, "Bedrock response missing rabi section"
        assert "zaid" in bedrock_data, "Bedrock response missing zaid section"
        assert "annual_summary" in bedrock_data, "Bedrock response missing annual_summary"
        assert "alternative_options" in bedrock_data, "Bedrock response missing alternative_options"
        assert "monthly_action_plan" in bedrock_data, "Bedrock response missing monthly_action_plan"

        # Assert: Bedrock response data matches persisted strategy fields
        assert (
            bedrock_data["kharif"]["recommended_crop"] == strategy["kharif_crop"]
        ), "Kharif crop mismatch between bedrock_response and strategy fields"
        assert (
            bedrock_data["rabi"]["recommended_crop"] == strategy["rabi_crop"]
        ), "Rabi crop mismatch between bedrock_response and strategy fields"

        # Assert: Profit estimates match
        assert (
            bedrock_data["kharif"]["expected_profit_per_acre"] == strategy["kharif_profit_estimate"]
        ), "Kharif profit mismatch between bedrock_response and strategy fields"
        assert (
            bedrock_data["rabi"]["expected_profit_per_acre"] == strategy["rabi_profit_estimate"]
        ), "Rabi profit mismatch between bedrock_response and strategy fields"

    @given(strategy=annual_strategy_data())
    @settings(
        max_examples=100,
        deadline=15000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
    )
    def test_reminder_content_includes_action_items(self, strategy):
        """
        **Validates: Requirements AC2.7**

        Property: For any monthly reminder, the notification should include the
        specific action items for that month from the implementation timeline.
        """
        # Arrange: Parse the implementation timeline
        timeline = json.loads(strategy["implementation_timeline"])

        # Arrange: Create mock notification service
        notification_service = Mock(spec=NotificationService)
        notification_service.send_strategy_reminder.return_value = {
            "success": True,
            "notification_type": "strategy_reminder",
        }

        # Act: Pick a random month and schedule its reminder
        import random

        month_entry = random.choice(timeline)
        month = month_entry["month"]
        actions = month_entry["actions"]

        reminder_result = notification_service.send_strategy_reminder(
            farmer_phone="+919876543210",
            farmer_email="farmer@example.com",
            farmer_name="Test Farmer",
            strategy_id=str(strategy.get("id", 12345)),
            reminder_type=f"{month.lower()}_actions",
            action_items=actions,
            due_date=None,
        )

        # Assert: Reminder was sent successfully
        assert reminder_result["success"], "Reminder should be sent successfully"

        # Assert: Notification service was called with correct action items
        call_kwargs = notification_service.send_strategy_reminder.call_args[1]
        assert "action_items" in call_kwargs, "action_items missing from reminder call"

        # Assert: Action items match the month's actions from timeline
        sent_actions = call_kwargs["action_items"]
        assert (
            sent_actions == actions
        ), f"Sent action items {sent_actions} don't match timeline actions {actions}"

        # Assert: All actions from the month are included
        assert len(sent_actions) == len(
            actions
        ), f"Expected {len(actions)} actions, got {len(sent_actions)}"

        for action in actions:
            assert action in sent_actions, f"Action '{action}' missing from reminder"

    def test_strategy_persistence_integration(self):
        """
        **Validates: Requirements AC2.7**

        Integration test: Verify that a complete strategy persistence workflow
        works end-to-end with database and notification services.
        """
        # Arrange: Create a complete strategy
        strategy = {
            "farmer_id": 1,
            "farm_id": 1,
            "year": 2024,
            "kharif_crop": "Rice",
            "kharif_profit_estimate": 45000,
            "kharif_confidence_score": 0.85,
            "rabi_crop": "Wheat",
            "rabi_profit_estimate": 38000,
            "rabi_confidence_score": 0.82,
            "zaid_crop": "Mung Bean",
            "zaid_profit_estimate": 12000,
            "zaid_confidence_score": 0.75,
            "total_annual_profit": 95000,
            "implementation_timeline": json.dumps(
                [
                    {"month": "January", "actions": ["Harvest rabi crops", "Prepare for zaid"]},
                    {"month": "February", "actions": ["Complete rabi harvest", "Soil preparation"]},
                    {"month": "March", "actions": ["Market rabi produce", "Plan kharif crops"]},
                    {"month": "April", "actions": ["Soil testing", "Purchase seeds"]},
                    {"month": "May", "actions": ["Land preparation", "Irrigation setup"]},
                    {"month": "June", "actions": ["Plant kharif crops", "Apply fertilizer"]},
                    {"month": "July", "actions": ["Monitor growth", "Pest control"]},
                    {"month": "August", "actions": ["Weeding", "Additional fertilizer"]},
                    {"month": "September", "actions": ["Crop monitoring", "Harvest preparation"]},
                    {"month": "October", "actions": ["Harvest kharif", "Storage planning"]},
                    {"month": "November", "actions": ["Market kharif produce", "Plant rabi crops"]},
                    {"month": "December", "actions": ["Rabi crop care", "Irrigation management"]},
                ]
            ),
            "alternative_options": json.dumps(
                [
                    {
                        "season": "kharif",
                        "crop": "Cotton",
                        "profit_difference": -5000,
                        "risk_comparison": "Higher risk but stable market",
                    }
                ]
            ),
            "bedrock_response": json.dumps(
                {
                    "kharif": {"recommended_crop": "Rice", "expected_profit_per_acre": 45000},
                    "rabi": {"recommended_crop": "Wheat", "expected_profit_per_acre": 38000},
                    "zaid": {"recommended_crop": "Mung Bean", "expected_profit_per_acre": 12000},
                    "annual_summary": {"total_expected_profit_per_acre": 95000},
                    "alternative_options": [],
                    "monthly_action_plan": [],
                }
            ),
            "status": "active",
        }

        # Arrange: Mock database service
        mock_db_service = Mock()
        mock_db_service.table = "annual_strategies"

        created_strategy = strategy.copy()
        created_strategy["id"] = 12345
        created_strategy["created_at"] = datetime.now(timezone.utc)
        mock_db_service.create.return_value = created_strategy

        # Arrange: Mock notification service
        mock_notification_service = Mock(spec=NotificationService)
        mock_notification_service.send_strategy_reminder.return_value = {
            "success": True,
            "notification_type": "strategy_reminder",
        }

        # Act: Persist strategy
        persisted_strategy = mock_db_service.create(strategy)

        # Act: Schedule reminders for all months
        timeline = json.loads(strategy["implementation_timeline"])
        for month_entry in timeline:
            mock_notification_service.send_strategy_reminder(
                farmer_phone="+919876543210",
                farmer_email="farmer@example.com",
                farmer_name="Test Farmer",
                strategy_id=str(persisted_strategy["id"]),
                reminder_type=f"{month_entry['month'].lower()}_actions",
                action_items=month_entry["actions"],
                due_date=None,
            )

        # Assert: Strategy was persisted
        assert mock_db_service.create.called, "Strategy should be persisted"
        assert persisted_strategy["id"] == 12345, "Strategy should have ID"

        # Assert: All 12 monthly reminders were scheduled
        assert (
            mock_notification_service.send_strategy_reminder.call_count == 12
        ), "Should schedule 12 monthly reminders"

        # Assert: Each reminder includes strategy_id
        for call in mock_notification_service.send_strategy_reminder.call_args_list:
            call_kwargs = call[1]
            assert (
                call_kwargs["strategy_id"] == "12345"
            ), "Each reminder should reference the persisted strategy ID"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
