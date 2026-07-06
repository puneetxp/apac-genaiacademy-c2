"""
Unit tests for livestock breeding optimization
Tests breeding recommendations, cycle tracking, offspring management, and program reports
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock

from app.services.livestock_breeding_service import LivestockBreedingService


@pytest.fixture
def breeding_service():
    """Create breeding service instance"""
    return LivestockBreedingService()


@pytest.fixture
def mock_livestock():
    """Mock livestock data"""
    return {
        'id': 1,
        'farmer_id': 1,
        'farm_id': 1,
        'species': 'cattle',
        'breed': 'Holstein',
        'quantity': 1,
        'purchase_price': Decimal('50000'),
        'purchase_date': date(2023, 1, 1),
        'purpose': 'dairy',
        'status': 'active'
    }


@pytest.fixture
def mock_breeding_record():
    """Mock breeding record data"""
    return {
        'id': 1,
        'livestock_id': 1,
        'farmer_id': 1,
        'breeding_type': 'artificial_insemination',
        'breeding_date': date(2024, 1, 15),
        'mate_breed': 'Jersey',
        'expected_delivery_date': date(2024, 10, 25),
        'pregnancy_status': 'confirmed',
        'breeding_cost': Decimal('2000'),
        'veterinarian_name': 'Dr. Kumar',
        'notes': 'First breeding attempt'
    }


@pytest.fixture
def mock_offspring():
    """Mock offspring data"""
    return {
        'id': 1,
        'breeding_record_id': 1,
        'livestock_id': None,
        'farmer_id': 1,
        'birth_date': date(2024, 10, 20),
        'gender': 'female',
        'birth_weight': Decimal('35.5'),
        'health_status': 'healthy',
        'current_weight': Decimal('45.0'),
        'growth_rate': Decimal('0.5'),
        'notes': 'Healthy calf'
    }


# ============================================================================
# Breeding Record Management Tests
# ============================================================================

def test_create_breeding_record_success(breeding_service, mock_livestock):
    """Test successful breeding record creation"""
    with patch.object(breeding_service.livestock_model, 'find', return_value=mock_livestock):
        with patch.object(breeding_service.breeding_record_model, 'create') as mock_create:
            mock_create.return_value = {
                'id': 1,
                'livestock_id': 1,
                'farmer_id': 1,
                'breeding_type': 'natural',
                'breeding_date': date(2024, 1, 15),
                'expected_delivery_date': date(2024, 10, 25),
                'pregnancy_status': 'pending'
            }
            
            record_data = {
                'livestock_id': 1,
                'farmer_id': 1,
                'breeding_type': 'natural',
                'breeding_date': date(2024, 1, 15),
                'pregnancy_status': 'pending'
            }
            
            result = breeding_service.create_breeding_record(record_data)
            
            assert result['id'] == 1
            assert result['livestock_id'] == 1
            assert result['breeding_type'] == 'natural'
            assert result['expected_delivery_date'] == date(2024, 10, 25)
            mock_create.assert_called_once()


def test_create_breeding_record_calculates_expected_delivery(breeding_service, mock_livestock):
    """Test that expected delivery date is calculated automatically"""
    with patch.object(breeding_service.livestock_model, 'find', return_value=mock_livestock):
        with patch.object(breeding_service.breeding_record_model, 'create') as mock_create:
            mock_create.return_value = {'id': 1}
            
            breeding_date = date(2024, 1, 15)
            record_data = {
                'livestock_id': 1,
                'farmer_id': 1,
                'breeding_type': 'natural',
                'breeding_date': breeding_date,
                'pregnancy_status': 'pending'
            }
            
            breeding_service.create_breeding_record(record_data)
            
            # Verify expected delivery date was calculated (283 days for cattle)
            call_args = mock_create.call_args[0][0]
            expected_delivery = breeding_date + timedelta(days=283)
            assert call_args['expected_delivery_date'] == expected_delivery


def test_create_breeding_record_livestock_not_found(breeding_service):
    """Test breeding record creation fails when livestock not found"""
    with patch.object(breeding_service.livestock_model, 'find', return_value=None):
        record_data = {
            'livestock_id': 999,
            'farmer_id': 1,
            'breeding_type': 'natural',
            'breeding_date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="Livestock with ID 999 not found"):
            breeding_service.create_breeding_record(record_data)


def test_get_breeding_record_success(breeding_service, mock_breeding_record):
    """Test successful breeding record retrieval"""
    with patch.object(breeding_service.breeding_record_model, 'find', return_value=mock_breeding_record):
        result = breeding_service.get_breeding_record(1)
        
        assert result['id'] == 1
        assert result['livestock_id'] == 1
        assert result['breeding_type'] == 'artificial_insemination'


def test_update_breeding_record_success(breeding_service, mock_breeding_record):
    """Test successful breeding record update"""
    with patch.object(breeding_service.breeding_record_model, 'find', return_value=mock_breeding_record):
        with patch.object(breeding_service.breeding_record_model, 'update') as mock_update:
            updated_record = mock_breeding_record.copy()
            updated_record['pregnancy_status'] = 'delivered'
            updated_record['actual_delivery_date'] = date(2024, 10, 20)
            
            with patch.object(breeding_service.breeding_record_model, 'find', return_value=updated_record):
                update_data = {
                    'pregnancy_status': 'delivered',
                    'actual_delivery_date': date(2024, 10, 20)
                }
                
                result = breeding_service.update_breeding_record(1, update_data)
                
                assert result['pregnancy_status'] == 'delivered'
                assert result['actual_delivery_date'] == date(2024, 10, 20)
                mock_update.assert_called_once()


def test_list_breeding_records_with_filters(breeding_service):
    """Test listing breeding records with filters"""
    mock_records = [
        {'id': 1, 'livestock_id': 1, 'farmer_id': 1, 'pregnancy_status': 'confirmed', 'breeding_date': date(2024, 1, 15)},
        {'id': 2, 'livestock_id': 1, 'farmer_id': 1, 'pregnancy_status': 'delivered', 'breeding_date': date(2023, 6, 10)},
    ]
    
    mock_result = Mock()
    mock_result.to_dict.return_value = mock_records
    
    with patch.object(breeding_service.breeding_record_model, 'where') as mock_where:
        mock_where.return_value.get.return_value = mock_result
        
        results = breeding_service.list_breeding_records(livestock_id=1)
        
        assert len(results) == 2
        assert results[0]['breeding_date'] == date(2024, 1, 15)  # Most recent first


# ============================================================================
# Offspring Management Tests
# ============================================================================

def test_create_offspring_success(breeding_service, mock_breeding_record):
    """Test successful offspring creation"""
    with patch.object(breeding_service.breeding_record_model, 'find', return_value=mock_breeding_record):
        with patch.object(breeding_service.offspring_model, 'create') as mock_create:
            with patch.object(breeding_service.breeding_record_model, 'update') as mock_update:
                mock_create.return_value = {
                    'id': 1,
                    'breeding_record_id': 1,
                    'farmer_id': 1,
                    'birth_date': date(2024, 10, 20),
                    'gender': 'female',
                    'birth_weight': Decimal('35.5'),
                    'health_status': 'healthy'
                }
                
                offspring_data = {
                    'breeding_record_id': 1,
                    'farmer_id': 1,
                    'birth_date': date(2024, 10, 20),
                    'gender': 'female',
                    'birth_weight': Decimal('35.5'),
                    'health_status': 'healthy'
                }
                
                result = breeding_service.create_offspring(offspring_data)
                
                assert result['id'] == 1
                assert result['gender'] == 'female'
                assert result['birth_weight'] == Decimal('35.5')
                mock_create.assert_called_once()
                mock_update.assert_called_once()  # Updates offspring count


def test_create_offspring_breeding_record_not_found(breeding_service):
    """Test offspring creation fails when breeding record not found"""
    with patch.object(breeding_service.breeding_record_model, 'find', return_value=None):
        offspring_data = {
            'breeding_record_id': 999,
            'farmer_id': 1,
            'birth_date': date(2024, 10, 20)
        }
        
        with pytest.raises(ValueError, match="Breeding record with ID 999 not found"):
            breeding_service.create_offspring(offspring_data)


def test_update_offspring_calculates_growth_rate(breeding_service, mock_offspring):
    """Test that growth rate is calculated when weight is updated"""
    with patch.object(breeding_service.offspring_model, 'find', return_value=mock_offspring):
        with patch.object(breeding_service.offspring_model, 'update') as mock_update:
            updated_offspring = mock_offspring.copy()
            updated_offspring['current_weight'] = Decimal('50.0')
            updated_offspring['growth_rate'] = Decimal('0.483')
            
            with patch.object(breeding_service.offspring_model, 'find', return_value=updated_offspring):
                update_data = {'current_weight': Decimal('50.0')}
                
                result = breeding_service.update_offspring(1, update_data)
                
                # Verify growth rate was calculated
                call_args = mock_update.call_args[0][1]
                assert 'growth_rate' in call_args
                assert call_args['growth_rate'] > 0


def test_list_offspring_with_filters(breeding_service):
    """Test listing offspring with filters"""
    mock_offspring_list = [
        {'id': 1, 'breeding_record_id': 1, 'farmer_id': 1, 'health_status': 'healthy', 'birth_date': date(2024, 10, 20)},
        {'id': 2, 'breeding_record_id': 1, 'farmer_id': 1, 'health_status': 'healthy', 'birth_date': date(2024, 10, 21)},
    ]
    
    mock_result = Mock()
    mock_result.to_dict.return_value = mock_offspring_list
    
    with patch.object(breeding_service.offspring_model, 'where') as mock_where:
        mock_where.return_value.get.return_value = mock_result
        
        results = breeding_service.list_offspring(breeding_record_id=1)
        
        assert len(results) == 2
        assert results[0]['birth_date'] == date(2024, 10, 21)  # Most recent first


# ============================================================================
# Breeding Recommendations Tests
# ============================================================================

def test_get_breeding_recommendations_success(breeding_service, mock_livestock):
    """Test successful breeding recommendations generation"""
    with patch.object(breeding_service.livestock_model, 'find', return_value=mock_livestock):
        with patch.object(breeding_service, 'list_breeding_records', return_value=[]):
            with patch.object(breeding_service, 'list_offspring', return_value=[]):
                with patch.object(breeding_service.bedrock_service, '_invoke_claude') as mock_bedrock:
                    mock_bedrock.return_value = '''
                    {
                        "recommendations": [
                            {
                                "mate_breed": "Jersey",
                                "compatibility_score": 0.85,
                                "expected_offspring_traits": {
                                    "milk_yield": "high",
                                    "growth_rate": "medium",
                                    "disease_resistance": "high"
                                },
                                "reasoning": "Jersey cross produces high milk yield"
                            }
                        ],
                        "optimal_breeding_season": "October to February",
                        "breeding_tips": ["Ensure good health", "Consult veterinarian"]
                    }
                    '''
                    
                    result = breeding_service.get_breeding_recommendations(1)
                    
                    assert result['livestock_breed'] == 'Holstein'
                    assert result['livestock_species'] == 'cattle'
                    assert len(result['recommendations']) > 0
                    assert result['recommendations'][0]['mate_breed'] == 'Jersey'
                    assert result['recommendations'][0]['compatibility_score'] == 0.85
                    assert result['estimated_gestation_days'] == 283


def test_get_breeding_recommendations_livestock_not_found(breeding_service):
    """Test breeding recommendations fail when livestock not found"""
    with patch.object(breeding_service.livestock_model, 'find', return_value=None):
        with pytest.raises(ValueError, match="Livestock with ID 999 not found"):
            breeding_service.get_breeding_recommendations(999)


def test_get_breeding_recommendations_with_history(breeding_service, mock_livestock):
    """Test breeding recommendations consider breeding history"""
    breeding_history = [
        {'id': 1, 'pregnancy_status': 'delivered', 'breeding_date': date(2023, 1, 15)},
        {'id': 2, 'pregnancy_status': 'delivered', 'breeding_date': date(2023, 7, 10)},
    ]
    
    offspring_performance = [
        {'birth_weight': Decimal('35.0'), 'growth_rate': Decimal('0.5'), 'health_status': 'healthy'},
        {'birth_weight': Decimal('36.0'), 'growth_rate': Decimal('0.6'), 'health_status': 'healthy'},
    ]
    
    with patch.object(breeding_service.livestock_model, 'find', return_value=mock_livestock):
        with patch.object(breeding_service, 'list_breeding_records', return_value=breeding_history):
            with patch.object(breeding_service, 'list_offspring', return_value=offspring_performance):
                with patch.object(breeding_service.bedrock_service, '_invoke_claude') as mock_bedrock:
                    mock_bedrock.return_value = '{"recommendations": [], "optimal_breeding_season": "October to February", "breeding_tips": []}'
                    
                    result = breeding_service.get_breeding_recommendations(1)
                    
                    # Verify Bedrock was called with breeding history
                    call_args = mock_bedrock.call_args[1]
                    assert 'prompt' in call_args
                    assert 'Total breedings: 2' in call_args['prompt']


def test_get_breeding_recommendations_fallback_on_parse_error(breeding_service, mock_livestock):
    """Test breeding recommendations use defaults when parsing fails"""
    with patch.object(breeding_service.livestock_model, 'find', return_value=mock_livestock):
        with patch.object(breeding_service, 'list_breeding_records', return_value=[]):
            with patch.object(breeding_service, 'list_offspring', return_value=[]):
                with patch.object(breeding_service.bedrock_service, '_invoke_claude') as mock_bedrock:
                    mock_bedrock.return_value = 'Invalid JSON response'
                    
                    result = breeding_service.get_breeding_recommendations(1)
                    
                    # Should return default recommendations
                    assert result['livestock_breed'] == 'Holstein'
                    assert len(result['recommendations']) > 0
                    assert result['estimated_gestation_days'] == 283


# ============================================================================
# Breeding Program Report Tests
# ============================================================================

def test_generate_breeding_program_report_success(breeding_service):
    """Test successful breeding program report generation"""
    # Use recent dates within last 12 months
    today = date.today()
    recent_date1 = today - timedelta(days=90)  # 3 months ago
    recent_date2 = today - timedelta(days=60)  # 2 months ago
    
    breeding_records = [
        {
            'id': 1,
            'livestock_id': 1,
            'farmer_id': 1,
            'pregnancy_status': 'delivered',
            'breeding_date': recent_date1,
            'number_of_offspring': 1,
            'breeding_cost': Decimal('2000')
        },
        {
            'id': 2,
            'livestock_id': 2,
            'farmer_id': 1,
            'pregnancy_status': 'delivered',
            'breeding_date': recent_date2,
            'number_of_offspring': 1,
            'breeding_cost': Decimal('2000')
        }
    ]
    
    offspring_list = [
        {'id': 1, 'breeding_record_id': 1, 'birth_weight': Decimal('35.0'), 'health_status': 'healthy', 'sale_price': Decimal('15000'), 'birth_date': recent_date1 + timedelta(days=283)},
        {'id': 2, 'breeding_record_id': 2, 'birth_weight': Decimal('36.0'), 'health_status': 'healthy', 'sale_price': Decimal('16000'), 'birth_date': recent_date2 + timedelta(days=283)},
    ]
    
    # Mock all database calls
    with patch.object(breeding_service, 'list_breeding_records') as mock_list_breeding:
        with patch.object(breeding_service, 'list_offspring') as mock_list_offspring:
            # First call returns all records, subsequent calls return offspring
            mock_list_breeding.return_value = breeding_records
            mock_list_offspring.return_value = offspring_list
            
            result = breeding_service.generate_breeding_program_report(farmer_id=1)
            
            assert result['farmer_id'] == 1
            assert 'metrics' in result
            assert result['metrics']['total_breedings'] == 2
            assert result['metrics']['successful_breedings'] == 2
            assert result['metrics']['success_rate'] == Decimal('100.00')
            assert result['metrics']['total_offspring'] == 2
            assert result['metrics']['total_breeding_cost'] == Decimal('4000.00')
            assert result['metrics']['total_offspring_revenue'] == Decimal('31000.00')
            assert result['metrics']['breeding_roi'] > 0


def test_generate_breeding_program_report_with_date_range(breeding_service):
    """Test breeding program report with custom date range"""
    start_date = date(2024, 1, 1)
    end_date = date(2024, 6, 30)
    
    all_records = [
        {'id': 1, 'breeding_date': date(2024, 2, 15), 'pregnancy_status': 'delivered', 'number_of_offspring': 1, 'breeding_cost': Decimal('2000')},
        {'id': 2, 'breeding_date': date(2024, 8, 10), 'pregnancy_status': 'delivered', 'number_of_offspring': 1, 'breeding_cost': Decimal('2000')},  # Outside range
    ]
    
    with patch.object(breeding_service, 'list_breeding_records', return_value=all_records):
        with patch.object(breeding_service, 'list_offspring', return_value=[]):
            result = breeding_service.generate_breeding_program_report(
                farmer_id=1,
                start_date=start_date,
                end_date=end_date
            )
            
            # Should only include records within date range
            assert len(result['breeding_records']) == 1
            assert result['breeding_records'][0]['id'] == 1


def test_calculate_breeding_metrics_zero_breedings(breeding_service):
    """Test breeding metrics calculation with no breedings"""
    with patch.object(breeding_service, 'list_offspring', return_value=[]):
        metrics = breeding_service._calculate_breeding_metrics([], farmer_id=1)
        
        assert metrics['total_breedings'] == 0
        assert metrics['successful_breedings'] == 0
        assert metrics['success_rate'] == Decimal('0')
        assert metrics['total_offspring'] == 0


def test_calculate_offspring_summary_no_offspring(breeding_service):
    """Test offspring summary with no offspring"""
    summary = breeding_service._calculate_offspring_summary([])
    
    assert summary['total_offspring'] == 0
    assert summary['average_birth_weight'] == 0
    assert summary['average_growth_rate'] == 0


def test_calculate_genetic_trends_insufficient_data(breeding_service):
    """Test genetic trends with insufficient data"""
    with patch.object(breeding_service, 'list_offspring', return_value=[]):
        trends = breeding_service._calculate_genetic_trends([], farmer_id=1)
        
        assert trends['trend'] == 'insufficient_data'
        assert trends['improvement_percentage'] == 0


def test_calculate_genetic_trends_improving(breeding_service):
    """Test genetic trends showing improvement"""
    offspring_list = [
        {'birth_weight': Decimal('30.0'), 'growth_rate': Decimal('0.4'), 'birth_date': date(2023, 1, 15)},
        {'birth_weight': Decimal('32.0'), 'growth_rate': Decimal('0.45'), 'birth_date': date(2023, 6, 10)},
        {'birth_weight': Decimal('35.0'), 'growth_rate': Decimal('0.5'), 'birth_date': date(2024, 1, 15)},
        {'birth_weight': Decimal('36.0'), 'growth_rate': Decimal('0.55'), 'birth_date': date(2024, 6, 10)},
    ]
    
    with patch.object(breeding_service, 'list_offspring', return_value=offspring_list):
        trends = breeding_service._calculate_genetic_trends([], farmer_id=1)
        
        assert trends['trend'] == 'improving'
        assert trends['improvement_percentage'] > 5


def test_generate_breeding_program_recommendations_low_success_rate(breeding_service):
    """Test recommendations for low success rate"""
    metrics = {
        'success_rate': Decimal('50.0'),
        'breeding_roi': Decimal('20.0')
    }
    offspring_summary = {'total_offspring': 5, 'healthy_offspring': 4}
    genetic_trends = {'trend': 'stable', 'improvement_percentage': Decimal('2.0')}
    
    recommendations = breeding_service._generate_breeding_program_recommendations(
        metrics, offspring_summary, genetic_trends
    )
    
    assert len(recommendations) > 0
    assert any('success rate is below 60%' in rec for rec in recommendations)


def test_generate_breeding_program_recommendations_negative_roi(breeding_service):
    """Test recommendations for negative ROI"""
    metrics = {
        'success_rate': Decimal('80.0'),
        'breeding_roi': Decimal('-10.0')
    }
    offspring_summary = {'total_offspring': 5, 'healthy_offspring': 4}
    genetic_trends = {'trend': 'stable', 'improvement_percentage': Decimal('2.0')}
    
    recommendations = breeding_service._generate_breeding_program_recommendations(
        metrics, offspring_summary, genetic_trends
    )
    
    assert any('negative ROI' in rec for rec in recommendations)


def test_generate_breeding_program_recommendations_declining_genetics(breeding_service):
    """Test recommendations for declining genetic quality"""
    metrics = {
        'success_rate': Decimal('80.0'),
        'breeding_roi': Decimal('30.0')
    }
    offspring_summary = {'total_offspring': 5, 'healthy_offspring': 4}
    genetic_trends = {'trend': 'declining', 'improvement_percentage': Decimal('-8.0')}
    
    recommendations = breeding_service._generate_breeding_program_recommendations(
        metrics, offspring_summary, genetic_trends
    )
    
    assert any('Genetic quality declining' in rec for rec in recommendations)


# ============================================================================
# Helper Method Tests
# ============================================================================

def test_calculate_average_with_values(breeding_service):
    """Test average calculation with valid values"""
    values = [Decimal('10.0'), Decimal('20.0'), Decimal('30.0')]
    avg = breeding_service._calculate_average(values)
    
    assert avg == 20.0


def test_calculate_average_with_none_values(breeding_service):
    """Test average calculation filters out None values"""
    values = [Decimal('10.0'), None, Decimal('30.0'), None]
    avg = breeding_service._calculate_average(values)
    
    assert avg == 20.0


def test_calculate_average_empty_list(breeding_service):
    """Test average calculation with empty list"""
    avg = breeding_service._calculate_average([])
    
    assert avg == 0.0


def test_gestation_periods_defined(breeding_service):
    """Test that gestation periods are defined for all species"""
    assert 'cattle' in breeding_service.GESTATION_PERIODS
    assert 'buffalo' in breeding_service.GESTATION_PERIODS
    assert 'goat' in breeding_service.GESTATION_PERIODS
    assert 'poultry' in breeding_service.GESTATION_PERIODS
    
    assert breeding_service.GESTATION_PERIODS['cattle'] == 283
    assert breeding_service.GESTATION_PERIODS['buffalo'] == 310
    assert breeding_service.GESTATION_PERIODS['goat'] == 150
    assert breeding_service.GESTATION_PERIODS['poultry'] == 21


def test_breeding_seasons_defined(breeding_service):
    """Test that breeding seasons are defined for all species"""
    assert 'cattle' in breeding_service.BREEDING_SEASONS
    assert 'buffalo' in breeding_service.BREEDING_SEASONS
    assert 'goat' in breeding_service.BREEDING_SEASONS
    assert 'poultry' in breeding_service.BREEDING_SEASONS
