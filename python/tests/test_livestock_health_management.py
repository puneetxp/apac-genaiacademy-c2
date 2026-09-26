"""
Tests for Livestock Health Record Management
Tests health record CRUD, vaccination schedules, and health reports
"""

from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest

from app.orm.livestock import Livestock
from app.orm.livestock_health_record import LivestockHealthRecord
from app.services.livestock_health_service import LivestockHealthService


@pytest.fixture
def health_service():
    """Create health service instance"""
    return LivestockHealthService()


@pytest.fixture
def test_livestock():
    """Create test livestock"""
    livestock_model = Livestock()

    # Clean up any existing test data
    existing_query = livestock_model.where({"farmer_id": 9999})
    existing_result = existing_query.get()
    if existing_result:
        existing = existing_result.to_dict()
        for item in existing:
            livestock_model.delete({"id": item["id"]})

    # Create test livestock
    livestock_data = {
        "farm_id": 1,
        "farmer_id": 9999,
        "species": "cattle",
        "breed": "Holstein",
        "quantity": 1,
        "purchase_price": Decimal("50000.00"),
        "purchase_date": date.today() - timedelta(days=90),  # 3 months old
        "purpose": "dairy",
        "status": "active",
    }

    created = livestock_model.create(livestock_data)
    result = created.get_inserted().to_dict()

    yield result

    # Cleanup
    livestock_model.delete({"id": result["id"]})


@pytest.fixture
def cleanup_health_records():
    """Cleanup health records after tests"""
    yield

    # Cleanup all test health records
    health_record_model = LivestockHealthRecord()
    all_query = health_record_model.where({"livestock_id": 9999})
    all_result = all_query.get()
    if all_result:
        all_records = all_result.to_dict()
        for record in all_records:
            if record.get("livestock_id") and record["livestock_id"] >= 9999:
                health_record_model.delete({"id": record["id"]})


class TestHealthRecordCRUD:
    """Test health record CRUD operations"""

    def test_create_vaccination_record(
        self, health_service, test_livestock, cleanup_health_records
    ):
        """Test creating a vaccination record"""
        record_data = {
            "livestock_id": test_livestock["id"],
            "record_type": "vaccination",
            "record_date": date.today(),
            "description": "FMD (Foot and Mouth Disease) vaccination",
            "veterinarian_name": "Dr. Sharma",
            "cost": Decimal("500.00"),
            "next_due_date": date.today() + timedelta(days=180),
            "notes": "First dose administered successfully",
        }

        result = health_service.create_health_record(record_data)

        assert result is not None
        assert result["id"] > 0
        assert result["livestock_id"] == test_livestock["id"]
        assert result["record_type"] == "vaccination"
        assert result["description"] == "FMD (Foot and Mouth Disease) vaccination"
        assert result["veterinarian_name"] == "Dr. Sharma"
        assert Decimal(str(result["cost"])) == Decimal("500.00")

    def test_create_treatment_record(self, health_service, test_livestock, cleanup_health_records):
        """Test creating a treatment record with medication details"""
        record_data = {
            "livestock_id": test_livestock["id"],
            "record_type": "treatment",
            "record_date": date.today() - timedelta(days=5),
            "description": "Treatment for fever and loss of appetite",
            "veterinarian_name": "Dr. Patel",
            "cost": Decimal("1200.00"),
            "notes": "Prescribed antibiotics for 7 days",
            "medication_name": "Amoxicillin",
            "dosage": "500mg twice daily",
            "treatment_outcome": "ongoing",
        }

        result = health_service.create_health_record(record_data)

        assert result is not None
        assert result["record_type"] == "treatment"
        assert result["description"] == "Treatment for fever and loss of appetite"
        assert Decimal(str(result["cost"])) == Decimal("1200.00")

    def test_create_checkup_record(self, health_service, test_livestock, cleanup_health_records):
        """Test creating a routine checkup record"""
        record_data = {
            "livestock_id": test_livestock["id"],
            "record_type": "checkup",
            "record_date": date.today() - timedelta(days=30),
            "description": "Routine health checkup - all parameters normal",
            "veterinarian_name": "Dr. Kumar",
            "cost": Decimal("300.00"),
            "next_due_date": date.today() + timedelta(days=150),
            "notes": "Weight: 250kg, Temperature: 38.5°C, Heart rate: 60 bpm",
        }

        result = health_service.create_health_record(record_data)

        assert result is not None
        assert result["record_type"] == "checkup"
        assert "all parameters normal" in result["description"]

    def test_create_observation_record(
        self, health_service, test_livestock, cleanup_health_records
    ):
        """Test creating an observation record"""
        record_data = {
            "livestock_id": test_livestock["id"],
            "record_type": "observation",
            "record_date": date.today(),
            "description": "Animal showing signs of reduced milk production",
            "notes": "Monitor for next 3 days, may need veterinary consultation",
        }

        result = health_service.create_health_record(record_data)

        assert result is not None
        assert result["record_type"] == "observation"
        assert "reduced milk production" in result["description"]

    def test_get_health_record(self, health_service, test_livestock, cleanup_health_records):
        """Test retrieving a health record by ID"""
        # Create a record
        record_data = {
            "livestock_id": test_livestock["id"],
            "record_type": "vaccination",
            "record_date": date.today(),
            "description": "Test vaccination",
            "cost": Decimal("500.00"),
        }

        created = health_service.create_health_record(record_data)

        # Retrieve it
        retrieved = health_service.get_health_record(created["id"])

        assert retrieved is not None
        assert retrieved["id"] == created["id"]
        assert retrieved["description"] == "Test vaccination"

    def test_update_health_record(self, health_service, test_livestock, cleanup_health_records):
        """Test updating a health record"""
        # Create a record
        record_data = {
            "livestock_id": test_livestock["id"],
            "record_type": "treatment",
            "record_date": date.today(),
            "description": "Initial treatment",
            "treatment_outcome": "ongoing",
        }

        created = health_service.create_health_record(record_data)

        # Update it
        update_data = {
            "description": "Treatment completed successfully",
            "treatment_outcome": "recovered",
            "notes": "Full recovery after 7 days",
        }

        updated = health_service.update_health_record(created["id"], update_data)

        assert updated is not None
        assert updated["description"] == "Treatment completed successfully"
        assert updated["notes"] == "Full recovery after 7 days"

    def test_delete_health_record(self, health_service, test_livestock, cleanup_health_records):
        """Test deleting a health record"""
        # Create a record
        record_data = {
            "livestock_id": test_livestock["id"],
            "record_type": "observation",
            "record_date": date.today(),
            "description": "Test observation",
        }

        created = health_service.create_health_record(record_data)

        # Delete it
        success = health_service.delete_health_record(created["id"])

        assert success is True

        # Verify it's deleted
        retrieved = health_service.get_health_record(created["id"])
        assert retrieved is None or retrieved.get("enable") == 0

    def test_create_record_invalid_livestock(self, health_service, cleanup_health_records):
        """Test creating record for non-existent livestock"""
        record_data = {
            "livestock_id": 999999,  # Non-existent
            "record_type": "vaccination",
            "record_date": date.today(),
            "description": "Test vaccination",
        }

        with pytest.raises(ValueError, match="not found"):
            health_service.create_health_record(record_data)


class TestHealthRecordListing:
    """Test health record listing and filtering"""

    def test_list_all_records_for_livestock(
        self, health_service, test_livestock, cleanup_health_records
    ):
        """Test listing all records for a specific livestock"""
        # Create multiple records
        for i in range(3):
            record_data = {
                "livestock_id": test_livestock["id"],
                "record_type": "vaccination",
                "record_date": date.today() - timedelta(days=i * 30),
                "description": f"Vaccination {i+1}",
            }
            health_service.create_health_record(record_data)

        # List records
        records = health_service.list_health_records(livestock_id=test_livestock["id"])

        assert len(records) >= 3
        assert all(r["livestock_id"] == test_livestock["id"] for r in records)

    def test_filter_by_record_type(self, health_service, test_livestock, cleanup_health_records):
        """Test filtering records by type"""
        # Create different types of records
        types = ["vaccination", "treatment", "checkup"]
        for record_type in types:
            record_data = {
                "livestock_id": test_livestock["id"],
                "record_type": record_type,
                "record_date": date.today(),
                "description": f"Test {record_type}",
            }
            health_service.create_health_record(record_data)

        # Filter by vaccination
        vaccinations = health_service.list_health_records(
            livestock_id=test_livestock["id"], record_type="vaccination"
        )

        assert len(vaccinations) >= 1
        assert all(r["record_type"] == "vaccination" for r in vaccinations)

    def test_filter_by_date_range(self, health_service, test_livestock, cleanup_health_records):
        """Test filtering records by date range"""
        # Create records with different dates
        dates = [date.today() - timedelta(days=60), date.today() - timedelta(days=30), date.today()]

        for record_date in dates:
            record_data = {
                "livestock_id": test_livestock["id"],
                "record_type": "checkup",
                "record_date": record_date,
                "description": f"Checkup on {record_date}",
            }
            health_service.create_health_record(record_data)

        # Filter last 45 days
        start_date = date.today() - timedelta(days=45)
        recent_records = health_service.list_health_records(
            livestock_id=test_livestock["id"], start_date=start_date
        )

        assert len(recent_records) >= 2
        for record in recent_records:
            record_date = record["record_date"]
            if isinstance(record_date, str):
                record_date = datetime.strptime(record_date, "%Y-%m-%d").date()
            assert record_date >= start_date

    def test_pagination(self, health_service, test_livestock, cleanup_health_records):
        """Test pagination of health records"""
        # Create 10 records
        for i in range(10):
            record_data = {
                "livestock_id": test_livestock["id"],
                "record_type": "observation",
                "record_date": date.today() - timedelta(days=i),
                "description": f"Observation {i+1}",
            }
            health_service.create_health_record(record_data)

        # Get first page
        page1 = health_service.list_health_records(
            livestock_id=test_livestock["id"], skip=0, limit=5
        )

        # Get second page
        page2 = health_service.list_health_records(
            livestock_id=test_livestock["id"], skip=5, limit=5
        )

        assert len(page1) == 5
        assert len(page2) >= 5
        assert page1[0]["id"] != page2[0]["id"]


class TestVaccinationSchedule:
    """Test vaccination schedule generation"""

    def test_get_vaccination_schedule_cattle(
        self, health_service, test_livestock, cleanup_health_records
    ):
        """Test vaccination schedule for cattle"""
        schedule = health_service.get_vaccination_schedule(test_livestock["id"])

        assert schedule is not None
        assert schedule["livestock_id"] == test_livestock["id"]
        assert schedule["species"] == "cattle"
        assert "upcoming_vaccinations" in schedule
        assert "completed_vaccinations" in schedule
        assert "overdue_vaccinations" in schedule

        # Should have upcoming vaccinations for a 3-month-old cattle
        assert len(schedule["upcoming_vaccinations"]) > 0

    def test_vaccination_schedule_with_completed(
        self, health_service, test_livestock, cleanup_health_records
    ):
        """Test vaccination schedule shows completed vaccinations"""
        # Create a completed vaccination
        record_data = {
            "livestock_id": test_livestock["id"],
            "record_type": "vaccination",
            "record_date": date.today() - timedelta(days=30),
            "description": "FMD (Foot and Mouth Disease) vaccination",
            "next_due_date": date.today() + timedelta(days=150),
        }
        health_service.create_health_record(record_data)

        schedule = health_service.get_vaccination_schedule(test_livestock["id"])

        assert len(schedule["completed_vaccinations"]) >= 1
        assert any("FMD" in v["name"] for v in schedule["completed_vaccinations"])

    def test_vaccination_schedule_overdue(self, health_service, cleanup_health_records):
        """Test vaccination schedule identifies overdue vaccinations"""
        # Create an older livestock (12 months old)
        livestock_model = Livestock()
        old_livestock_data = {
            "farm_id": 1,
            "farmer_id": 9999,
            "species": "cattle",
            "breed": "Jersey",
            "quantity": 1,
            "purchase_price": Decimal("40000.00"),
            "purchase_date": date.today() - timedelta(days=365),  # 12 months old
            "purpose": "dairy",
            "status": "active",
        }
        created = livestock_model.create(old_livestock_data)
        old_livestock = created.get_inserted().to_dict()

        try:
            schedule = health_service.get_vaccination_schedule(old_livestock["id"])

            # Should have overdue vaccinations for a 12-month-old cattle with no records
            assert len(schedule["overdue_vaccinations"]) > 0

        finally:
            livestock_model.delete({"id": old_livestock["id"]})


class TestHealthReport:
    """Test comprehensive health report generation"""

    def test_generate_health_report(self, health_service, test_livestock, cleanup_health_records):
        """Test generating comprehensive health report"""
        # Create various health records
        records = [
            {
                "livestock_id": test_livestock["id"],
                "record_type": "vaccination",
                "record_date": date.today() - timedelta(days=60),
                "description": "FMD vaccination",
                "cost": Decimal("500.00"),
            },
            {
                "livestock_id": test_livestock["id"],
                "record_type": "treatment",
                "record_date": date.today() - timedelta(days=30),
                "description": "Treatment for fever",
                "cost": Decimal("1200.00"),
            },
            {
                "livestock_id": test_livestock["id"],
                "record_type": "checkup",
                "record_date": date.today() - timedelta(days=15),
                "description": "Routine checkup",
                "cost": Decimal("300.00"),
            },
        ]

        for record_data in records:
            health_service.create_health_record(record_data)

        # Generate report
        report = health_service.generate_health_report(test_livestock["id"])

        assert report is not None
        assert report["livestock_id"] == test_livestock["id"]
        assert report["species"] == "cattle"
        assert report["breed"] == "Holstein"
        assert report["total_records"] >= 3
        assert len(report["vaccinations"]) >= 1
        assert len(report["treatments"]) >= 1
        assert len(report["checkups"]) >= 1
        assert report["total_health_cost"] >= Decimal("2000.00")
        assert report["last_checkup_date"] is not None
        assert "health_summary" in report
        assert len(report["health_summary"]) > 0

    def test_health_report_cost_calculation(
        self, health_service, test_livestock, cleanup_health_records
    ):
        """Test health report calculates total costs correctly"""
        # Create records with known costs
        costs = [Decimal("500.00"), Decimal("1200.00"), Decimal("300.00")]

        for i, cost in enumerate(costs):
            record_data = {
                "livestock_id": test_livestock["id"],
                "record_type": "vaccination",
                "record_date": date.today() - timedelta(days=i * 10),
                "description": f"Record {i+1}",
                "cost": cost,
            }
            health_service.create_health_record(record_data)

        report = health_service.generate_health_report(test_livestock["id"])

        expected_total = sum(costs)
        assert report["total_health_cost"] == expected_total

    def test_health_report_summary_generation(
        self, health_service, test_livestock, cleanup_health_records
    ):
        """Test health report generates meaningful summary"""
        # Create a vaccination
        record_data = {
            "livestock_id": test_livestock["id"],
            "record_type": "vaccination",
            "record_date": date.today() - timedelta(days=30),
            "description": "FMD vaccination",
        }
        health_service.create_health_record(record_data)

        report = health_service.generate_health_report(test_livestock["id"])

        summary = report["health_summary"]
        assert "Holstein" in summary or "cattle" in summary.lower()
        assert "vaccination" in summary.lower()

    def test_health_report_empty_records(
        self, health_service, test_livestock, cleanup_health_records
    ):
        """Test health report with no health records"""
        report = health_service.generate_health_report(test_livestock["id"])

        assert report is not None
        assert report["total_records"] == 0
        assert len(report["vaccinations"]) == 0
        assert len(report["treatments"]) == 0
        assert report["total_health_cost"] == Decimal("0")
        assert report["last_checkup_date"] is None


class TestHealthRecordPerformance:
    """Test health record system performance"""

    def test_record_retrieval_performance(
        self, health_service, test_livestock, cleanup_health_records
    ):
        """Test that health records are retrieved within 1 second"""
        import time

        # Create 50 health records
        for i in range(50):
            record_data = {
                "livestock_id": test_livestock["id"],
                "record_type": "observation",
                "record_date": date.today() - timedelta(days=i),
                "description": f"Observation {i+1}",
            }
            health_service.create_health_record(record_data)

        # Measure retrieval time
        start_time = time.time()
        records = health_service.list_health_records(livestock_id=test_livestock["id"])
        end_time = time.time()

        retrieval_time = end_time - start_time

        assert retrieval_time < 1.0, f"Record retrieval took {retrieval_time:.2f}s, should be < 1s"
        assert len(records) >= 50

    def test_health_report_generation_performance(
        self, health_service, test_livestock, cleanup_health_records
    ):
        """Test that health report generation is performant"""
        import time

        # Create various records
        for i in range(20):
            record_data = {
                "livestock_id": test_livestock["id"],
                "record_type": ["vaccination", "treatment", "checkup"][i % 3],
                "record_date": date.today() - timedelta(days=i * 5),
                "description": f"Record {i+1}",
                "cost": Decimal("500.00"),
            }
            health_service.create_health_record(record_data)

        # Measure report generation time
        start_time = time.time()
        report = health_service.generate_health_report(test_livestock["id"])
        end_time = time.time()

        generation_time = end_time - start_time

        assert (
            generation_time < 2.0
        ), f"Report generation took {generation_time:.2f}s, should be < 2s"
        assert report["total_records"] >= 20


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
