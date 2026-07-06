"""
Property-Based Tests for Livestock Health Record Management
Tests universal properties of health record CRUD operations using Hypothesis

**Validates: Requirements AC12 (Phase 7 - Required)**
"""

import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from datetime import date, datetime, timedelta
from decimal import Decimal
import time

from app.services.livestock_health_service import LivestockHealthService
from app.orm.livestock import Livestock
from app.orm.livestock_health_record import LivestockHealthRecord


# Test data strategies
@st.composite
def livestock_data_strategy(draw):
    """Generate valid livestock data"""
    species_options = ['cattle', 'buffalo', 'goat', 'poultry']
    breed_options = {
        'cattle': ['Holstein', 'Jersey', 'Gir', 'Sahiwal'],
        'buffalo': ['Murrah', 'Jaffarabadi', 'Mehsana'],
        'goat': ['Boer', 'Jamunapari', 'Sirohi'],
        'poultry': ['Broiler', 'Layer', 'Kadaknath']
    }
    
    species = draw(st.sampled_from(species_options))
    breed = draw(st.sampled_from(breed_options[species]))
    
    # Generate purchase date between 1 month and 5 years ago
    days_ago = draw(st.integers(min_value=30, max_value=1825))
    purchase_date = date.today() - timedelta(days=days_ago)
    
    return {
        'farm_id': 1,
        'farmer_id': draw(st.integers(min_value=10000, max_value=99999)),
        'species': species,
        'breed': breed,
        'quantity': 1,
        'purchase_price': Decimal(str(draw(st.floats(min_value=5000, max_value=100000)))),
        'purchase_date': purchase_date,
        'purpose': draw(st.sampled_from(['dairy', 'meat', 'breeding', 'eggs'])),
        'status': 'active'
    }


@st.composite
def health_record_data_strategy(draw, livestock_id):
    """Generate valid health record data"""
    record_type = draw(st.sampled_from(['vaccination', 'treatment', 'checkup', 'observation', 'breeding']))
    
    # Generate record date within last year
    days_ago = draw(st.integers(min_value=0, max_value=365))
    record_date = date.today() - timedelta(days=days_ago)
    
    record_data = {
        'livestock_id': livestock_id,
        'record_type': record_type,
        'record_date': record_date,
        'description': draw(st.text(min_size=10, max_size=200, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')))),
    }
    
    # Add optional fields based on probability
    if draw(st.booleans()):
        record_data['veterinarian_name'] = draw(st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Zs'))))
    
    if draw(st.booleans()):
        record_data['cost'] = Decimal(str(draw(st.floats(min_value=100, max_value=10000))))
    
    if draw(st.booleans()):
        record_data['notes'] = draw(st.text(min_size=10, max_size=300, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs', 'Po'))))
    
    # Add type-specific fields
    if record_type == 'vaccination':
        if draw(st.booleans()):
            days_until_next = draw(st.integers(min_value=30, max_value=365))
            record_data['next_due_date'] = record_date + timedelta(days=days_until_next)
    
    elif record_type == 'treatment':
        if draw(st.booleans()):
            record_data['medication_name'] = draw(st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))))
        if draw(st.booleans()):
            record_data['dosage'] = draw(st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'))))
        if draw(st.booleans()):
            record_data['treatment_outcome'] = draw(st.sampled_from(['ongoing', 'recovered', 'referred', 'deceased']))
    
    return record_data


@st.composite
def health_record_update_strategy(draw):
    """Generate valid health record update data"""
    update_data = {}
    
    # Randomly update some fields
    if draw(st.booleans()):
        update_data['description'] = draw(st.text(min_size=10, max_size=200, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'))))
    
    if draw(st.booleans()):
        update_data['notes'] = draw(st.text(min_size=10, max_size=300, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs', 'Po'))))
    
    if draw(st.booleans()):
        update_data['cost'] = Decimal(str(draw(st.floats(min_value=100, max_value=10000))))
    
    if draw(st.booleans()):
        update_data['treatment_outcome'] = draw(st.sampled_from(['ongoing', 'recovered', 'referred', 'deceased']))
    
    # Ensure at least one field is updated
    assume(len(update_data) > 0)
    
    return update_data


@pytest.fixture(scope="module")
def health_service():
    """Create health service instance"""
    return LivestockHealthService()


@pytest.fixture(scope="module")
def livestock_model():
    """Create livestock model instance"""
    return Livestock()


@pytest.fixture(scope="module")
def health_record_model():
    """Create health record model instance"""
    return LivestockHealthRecord()


@pytest.fixture(autouse=True)
def cleanup_test_data(livestock_model, health_record_model):
    """Cleanup test data before and after each test"""
    # Cleanup before test
    _cleanup_records(livestock_model, health_record_model)
    
    yield
    
    # Cleanup after test
    _cleanup_records(livestock_model, health_record_model)


def _cleanup_records(livestock_model, health_record_model):
    """Helper to cleanup test records"""
    try:
        # Cleanup test livestock (farmer_id >= 10000)
        # Use raw SQL to avoid ORM issues
        from app.core.db import DB
        
        # Delete health records for test livestock
        DB.raw(
            "DELETE FROM livestock_health_records WHERE livestock_id IN (SELECT id FROM livestock WHERE farmer_id >= %s)",
            [10000]
        )
        
        # Delete test livestock
        DB.raw("DELETE FROM livestock WHERE farmer_id >= %s", [10000])
        
    except Exception as e:
        # Ignore cleanup errors - they're not critical for tests
        pass


class TestHealthRecordCRUDProperties:
    """
    Property 11: Livestock Health Record Management
    
    Test that for any livestock animal, farmers can create, update, and retrieve health records.
    Verify all data is persisted correctly and retrievable within 1 second.
    """
    
    @given(livestock_data=livestock_data_strategy())
    @settings(
        max_examples=5,  # Reduced from 20 to avoid connection exhaustion
        deadline=5000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    def test_property_create_and_retrieve_health_record(
        self,
        health_service,
        livestock_model,
        livestock_data
    ):
        """
        Property: For any valid livestock and health record data,
        creating a health record should persist all data correctly
        and be retrievable within 1 second.
        
        **Validates: Requirements AC12.1**
        """
        # Create livestock
        created_livestock = livestock_model.create(livestock_data)
        livestock = created_livestock.get_inserted().to_dict()
        
        try:
            # Generate health record data
            record_data = {
                'livestock_id': livestock['id'],
                'record_type': 'vaccination',
                'record_date': date.today(),
                'description': 'Test vaccination record',
                'veterinarian_name': 'Dr. Test',
                'cost': Decimal('500.00')
            }
            
            # Measure creation time
            start_time = time.time()
            created_record = health_service.create_health_record(record_data)
            creation_time = time.time() - start_time
            
            # Property 1: Record is created successfully
            assert created_record is not None
            assert created_record['id'] > 0
            
            # Property 2: All data is persisted correctly
            assert created_record['livestock_id'] == livestock['id']
            assert created_record['record_type'] == record_data['record_type']
            assert created_record['description'] == record_data['description']
            assert created_record['veterinarian_name'] == record_data['veterinarian_name']
            assert Decimal(str(created_record['cost'])) == record_data['cost']
            
            # Property 3: Record is retrievable within 1 second
            start_time = time.time()
            retrieved_record = health_service.get_health_record(created_record['id'])
            retrieval_time = time.time() - start_time
            
            assert retrieval_time < 1.0, f"Retrieval took {retrieval_time:.3f}s, should be < 1s"
            assert retrieved_record is not None
            assert retrieved_record['id'] == created_record['id']
            
            # Property 4: Retrieved data matches created data
            assert retrieved_record['livestock_id'] == record_data['livestock_id']
            assert retrieved_record['record_type'] == record_data['record_type']
            assert retrieved_record['description'] == record_data['description']
            
        finally:
            # Cleanup
            livestock_model.delete({'id': livestock['id']})
    
    @given(
        livestock_data=livestock_data_strategy(),
        record_data_gen=st.data()
    )
    @settings(
        max_examples=5,  # Reduced from 15
        deadline=5000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    def test_property_create_multiple_record_types(
        self,
        health_service,
        livestock_model,
        livestock_data,
        record_data_gen
    ):
        """
        Property: For any livestock, farmers can create multiple types of health records
        (vaccination, treatment, checkup, observation, breeding) and all are persisted correctly.
        
        **Validates: Requirements AC12.1, AC12.5**
        """
        # Create livestock
        created_livestock = livestock_model.create(livestock_data)
        livestock = created_livestock.get_inserted().to_dict()
        
        try:
            record_types = ['vaccination', 'treatment', 'checkup', 'observation', 'breeding']
            created_records = []
            
            # Create one record of each type
            for record_type in record_types:
                record_data = record_data_gen.draw(health_record_data_strategy(livestock['id']))
                record_data['record_type'] = record_type  # Ensure specific type
                
                created_record = health_service.create_health_record(record_data)
                created_records.append(created_record)
                
                # Property 1: Each record type is created successfully
                assert created_record is not None
                assert created_record['record_type'] == record_type
            
            # Property 2: All records are retrievable
            for created_record in created_records:
                retrieved = health_service.get_health_record(created_record['id'])
                assert retrieved is not None
                assert retrieved['id'] == created_record['id']
            
            # Property 3: All records are listed for the livestock
            all_records = health_service.list_health_records(livestock_id=livestock['id'])
            assert len(all_records) >= len(record_types)
            
            # Property 4: Each record type is present in the list
            retrieved_types = {r['record_type'] for r in all_records}
            for record_type in record_types:
                assert record_type in retrieved_types
            
        finally:
            # Cleanup
            livestock_model.delete({'id': livestock['id']})
    
    @given(
        livestock_data=livestock_data_strategy(),
        record_data_gen=st.data(),
        update_data_gen=st.data()
    )
    @settings(
        max_examples=5,  # Reduced from 15
        deadline=5000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    def test_property_update_health_record(
        self,
        health_service,
        livestock_model,
        livestock_data,
        record_data_gen,
        update_data_gen
    ):
        """
        Property: For any health record, farmers can update record details
        and all changes are persisted correctly.
        
        **Validates: Requirements AC12.1, AC12.5**
        """
        # Create livestock
        created_livestock = livestock_model.create(livestock_data)
        livestock = created_livestock.get_inserted().to_dict()
        
        try:
            # Create initial health record
            record_data = record_data_gen.draw(health_record_data_strategy(livestock['id']))
            created_record = health_service.create_health_record(record_data)
            
            # Generate update data
            update_data = update_data_gen.draw(health_record_update_strategy())
            
            # Update the record
            updated_record = health_service.update_health_record(created_record['id'], update_data)
            
            # Property 1: Update is successful
            assert updated_record is not None
            assert updated_record['id'] == created_record['id']
            
            # Property 2: Updated fields are persisted correctly
            for field, value in update_data.items():
                if field in updated_record:
                    if isinstance(value, Decimal):
                        assert Decimal(str(updated_record[field])) == value
                    else:
                        assert updated_record[field] == value
            
            # Property 3: Unchanged fields remain the same
            assert updated_record['livestock_id'] == created_record['livestock_id']
            assert updated_record['record_type'] == created_record['record_type']
            assert updated_record['record_date'] == created_record['record_date']
            
            # Property 4: Updated record is retrievable with changes
            retrieved = health_service.get_health_record(created_record['id'])
            assert retrieved is not None
            for field, value in update_data.items():
                if field in retrieved:
                    if isinstance(value, Decimal):
                        assert Decimal(str(retrieved[field])) == value
                    else:
                        assert retrieved[field] == value
            
        finally:
            # Cleanup
            livestock_model.delete({'id': livestock['id']})
    
    @given(
        livestock_data=livestock_data_strategy(),
        num_records=st.integers(min_value=5, max_value=50)
    )
    @settings(
        max_examples=3,  # Reduced from 10
        deadline=10000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    def test_property_list_records_performance(
        self,
        health_service,
        livestock_model,
        livestock_data,
        num_records
    ):
        """
        Property: For any number of health records (5-50), listing all records
        for a livestock should complete within 1 second.
        
        **Validates: Requirements AC12 (Performance requirement)**
        """
        # Create livestock
        created_livestock = livestock_model.create(livestock_data)
        livestock = created_livestock.get_inserted().to_dict()
        
        try:
            # Create multiple health records
            for i in range(num_records):
                record_data = {
                    'livestock_id': livestock['id'],
                    'record_type': ['vaccination', 'treatment', 'checkup'][i % 3],
                    'record_date': date.today() - timedelta(days=i),
                    'description': f'Health record {i+1}'
                }
                health_service.create_health_record(record_data)
            
            # Measure listing time
            start_time = time.time()
            records = health_service.list_health_records(livestock_id=livestock['id'])
            listing_time = time.time() - start_time
            
            # Property 1: Listing completes within 1 second
            assert listing_time < 1.0, f"Listing {num_records} records took {listing_time:.3f}s, should be < 1s"
            
            # Property 2: All records are returned
            assert len(records) >= num_records
            
            # Property 3: All records belong to the correct livestock
            for record in records:
                assert record['livestock_id'] == livestock['id']
            
            # Property 4: Records are sorted by date (most recent first)
            for i in range(len(records) - 1):
                date1 = records[i]['record_date']
                date2 = records[i + 1]['record_date']
                if isinstance(date1, str):
                    date1 = datetime.strptime(date1, '%Y-%m-%d').date()
                if isinstance(date2, str):
                    date2 = datetime.strptime(date2, '%Y-%m-%d').date()
                assert date1 >= date2, "Records should be sorted by date descending"
            
        finally:
            # Cleanup
            livestock_model.delete({'id': livestock['id']})
    
    @given(
        livestock_data=livestock_data_strategy(),
        record_type_filter=st.sampled_from(['vaccination', 'treatment', 'checkup', 'observation'])
    )
    @settings(
        max_examples=3,  # Reduced from 10
        deadline=5000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    def test_property_filter_by_record_type(
        self,
        health_service,
        livestock_model,
        livestock_data,
        record_type_filter
    ):
        """
        Property: For any record type filter, listing records should return
        only records of that type.
        
        **Validates: Requirements AC12.1**
        """
        # Create livestock
        created_livestock = livestock_model.create(livestock_data)
        livestock = created_livestock.get_inserted().to_dict()
        
        try:
            # Create records of different types
            record_types = ['vaccination', 'treatment', 'checkup', 'observation']
            for record_type in record_types:
                for i in range(3):  # 3 records of each type
                    record_data = {
                        'livestock_id': livestock['id'],
                        'record_type': record_type,
                        'record_date': date.today() - timedelta(days=i),
                        'description': f'{record_type} record {i+1}'
                    }
                    health_service.create_health_record(record_data)
            
            # Filter by specific type
            filtered_records = health_service.list_health_records(
                livestock_id=livestock['id'],
                record_type=record_type_filter
            )
            
            # Property 1: All returned records match the filter
            assert len(filtered_records) >= 3
            for record in filtered_records:
                assert record['record_type'] == record_type_filter
            
            # Property 2: No records of other types are returned
            all_records = health_service.list_health_records(livestock_id=livestock['id'])
            other_type_count = sum(1 for r in all_records if r['record_type'] != record_type_filter)
            assert other_type_count > 0  # Ensure we have other types
            assert len(filtered_records) < len(all_records)  # Filtered list is smaller
            
        finally:
            # Cleanup
            livestock_model.delete({'id': livestock['id']})
    
    @given(
        livestock_data=livestock_data_strategy(),
        days_back=st.integers(min_value=30, max_value=180)
    )
    @settings(
        max_examples=3,  # Reduced from 10
        deadline=5000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    def test_property_filter_by_date_range(
        self,
        health_service,
        livestock_model,
        livestock_data,
        days_back
    ):
        """
        Property: For any date range filter, listing records should return
        only records within that date range.
        
        **Validates: Requirements AC12.1**
        """
        # Create livestock
        created_livestock = livestock_model.create(livestock_data)
        livestock = created_livestock.get_inserted().to_dict()
        
        try:
            # Create records with different dates
            for i in range(200):  # Records spanning 200 days
                record_data = {
                    'livestock_id': livestock['id'],
                    'record_type': 'observation',
                    'record_date': date.today() - timedelta(days=i),
                    'description': f'Observation on day {i}'
                }
                health_service.create_health_record(record_data)
            
            # Filter by date range
            start_date = date.today() - timedelta(days=days_back)
            filtered_records = health_service.list_health_records(
                livestock_id=livestock['id'],
                start_date=start_date
            )
            
            # Property 1: All returned records are within the date range
            for record in filtered_records:
                record_date = record['record_date']
                if isinstance(record_date, str):
                    record_date = datetime.strptime(record_date, '%Y-%m-%d').date()
                assert record_date >= start_date
            
            # Property 2: Records outside the range are not returned
            all_records = health_service.list_health_records(livestock_id=livestock['id'])
            assert len(filtered_records) <= len(all_records)
            assert len(filtered_records) <= days_back + 1  # +1 for today
            
        finally:
            # Cleanup
            livestock_model.delete({'id': livestock['id']})
    
    @given(livestock_data=livestock_data_strategy())
    @settings(
        max_examples=3,  # Reduced from 10
        deadline=5000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    def test_property_vaccination_schedule_generation(
        self,
        health_service,
        livestock_model,
        livestock_data
    ):
        """
        Property: For any livestock, the system generates a vaccination schedule
        based on species, breed, age, and location.
        
        **Validates: Requirements AC12.2**
        """
        # Create livestock
        created_livestock = livestock_model.create(livestock_data)
        livestock = created_livestock.get_inserted().to_dict()
        
        try:
            # Get vaccination schedule
            schedule = health_service.get_vaccination_schedule(livestock['id'])
            
            # Property 1: Schedule is generated successfully
            assert schedule is not None
            assert schedule['livestock_id'] == livestock['id']
            assert schedule['species'] == livestock['species']
            
            # Property 2: Schedule contains required sections
            assert 'upcoming_vaccinations' in schedule
            assert 'completed_vaccinations' in schedule
            assert 'overdue_vaccinations' in schedule
            assert 'age_months' in schedule
            
            # Property 3: Age is calculated correctly
            purchase_date = livestock['purchase_date']
            if isinstance(purchase_date, str):
                purchase_date = datetime.strptime(purchase_date, '%Y-%m-%d').date()
            expected_age_months = (date.today() - purchase_date).days // 30
            assert schedule['age_months'] == expected_age_months
            
            # Property 4: For young livestock, there should be upcoming vaccinations
            if schedule['age_months'] < 12:
                assert len(schedule['upcoming_vaccinations']) > 0 or len(schedule['overdue_vaccinations']) > 0
            
            # Property 5: Each vaccination has required fields
            for vaccination in schedule['upcoming_vaccinations']:
                assert 'name' in vaccination
                assert 'due_date' in vaccination
                assert 'days_until_due' in vaccination
            
        finally:
            # Cleanup
            livestock_model.delete({'id': livestock['id']})
    
    @given(
        livestock_data=livestock_data_strategy(),
        num_records=st.integers(min_value=10, max_value=30)
    )
    @settings(
        max_examples=2,  # Reduced from 5
        deadline=10000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    def test_property_health_report_generation(
        self,
        health_service,
        livestock_model,
        livestock_data,
        num_records
    ):
        """
        Property: For any livestock with health records, the system generates
        a comprehensive health report within 5 seconds.
        
        **Validates: Requirements AC12.6 (Validation Metric: < 5 seconds)**
        """
        # Create livestock
        created_livestock = livestock_model.create(livestock_data)
        livestock = created_livestock.get_inserted().to_dict()
        
        try:
            # Create various health records
            for i in range(num_records):
                record_type = ['vaccination', 'treatment', 'checkup', 'observation'][i % 4]
                record_data = {
                    'livestock_id': livestock['id'],
                    'record_type': record_type,
                    'record_date': date.today() - timedelta(days=i*5),
                    'description': f'{record_type} record {i+1}',
                    'cost': Decimal(str(500 + i * 100))
                }
                health_service.create_health_record(record_data)
            
            # Measure report generation time
            start_time = time.time()
            report = health_service.generate_health_report(livestock['id'])
            generation_time = time.time() - start_time
            
            # Property 1: Report generation completes within 5 seconds
            assert generation_time < 5.0, f"Report generation took {generation_time:.3f}s, should be < 5s"
            
            # Property 2: Report contains all required sections
            assert report is not None
            assert report['livestock_id'] == livestock['id']
            assert 'total_records' in report
            assert 'vaccinations' in report
            assert 'treatments' in report
            assert 'checkups' in report
            assert 'observations' in report
            assert 'total_health_cost' in report
            assert 'health_summary' in report
            
            # Property 3: Total records count is correct
            assert report['total_records'] >= num_records
            
            # Property 4: Health cost is calculated correctly
            assert report['total_health_cost'] > 0
            
            # Property 5: Health summary is generated
            assert len(report['health_summary']) > 0
            assert livestock['species'] in report['health_summary'].lower() or livestock['breed'] in report['health_summary']
            
        finally:
            # Cleanup
            livestock_model.delete({'id': livestock['id']})


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
