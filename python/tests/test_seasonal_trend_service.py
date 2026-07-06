"""
Tests for Seasonal Trend Analysis Service
"""

import pytest
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session

from app.services.seasonal_trend_service import SeasonalTrendService
from app.models.market_intelligence import CropMarketData, HistoricalYield


class TestSeasonalTrendService:
    """Test suite for SeasonalTrendService"""
    
    @pytest.fixture
    def service(self, db_session: Session):
        """Create service instance"""
        return SeasonalTrendService(db_session)
    
    @pytest.fixture
    def sample_market_data(self, db_session: Session):
        """Create sample market data for testing"""
        data_records = []
        
        # Create data for Wheat in Punjab for Rabi season (3 years)
        for year in [2021, 2022, 2023]:
            for month in [3, 4, 5]:  # Rabi harvest months
                record = CropMarketData(
                    crop_type="Wheat",
                    variety="HD-2967",
                    state="Punjab",
                    district="Ludhiana",
                    year=year,
                    month=month,
                    season="rabi",
                    avg_price_per_quintal=Decimal(str(2000 + (year - 2021) * 100 + month * 10)),
                    min_price=Decimal(str(1900 + (year - 2021) * 100)),
                    max_price=Decimal(str(2100 + (year - 2021) * 100)),
                    market_demand_score=Decimal("0.85"),
                    data_source="test"
                )
                db_session.add(record)
                data_records.append(record)
        
        db_session.commit()
        return data_records
    
    @pytest.fixture
    def sample_yield_data(self, db_session: Session):
        """Create sample yield data for testing"""
        data_records = []
        
        # Create yield data for Wheat in Punjab for Rabi season (3 years)
        for year in [2021, 2022, 2023]:
            record = HistoricalYield(
                crop_type="Wheat",
                variety="HD-2967",
                state="Punjab",
                district="Ludhiana",
                year=year,
                season="rabi",
                avg_yield_per_acre=Decimal(str(20 + (year - 2021) * 0.5)),
                min_yield=Decimal(str(18 + (year - 2021) * 0.5)),
                max_yield=Decimal(str(22 + (year - 2021) * 0.5)),
                success_rate=Decimal(str(85 + (year - 2021))),
                farmer_count=100,
                data_source="test"
            )
            db_session.add(record)
            data_records.append(record)
        
        db_session.commit()
        return data_records
    
    def test_analyze_season_trend_with_data(
        self,
        service: SeasonalTrendService,
        sample_market_data,
        sample_yield_data
    ):
        """Test analyzing season trend with available data"""
        result = service.analyze_season_trend(
            crop_type="Wheat",
            state="Punjab",
            district="Ludhiana",
            season="rabi",
            years=3
        )
        
        assert result['season'] == 'rabi'
        assert result['crop_type'] == 'Wheat'
        assert result['state'] == 'Punjab'
        assert result['data_available'] is True
        
        # Check price trends
        assert 'price_trends' in result
        assert result['price_trends']['data_available'] is True
        assert 'avg_yoy_growth' in result['price_trends']
        
        # Check yield trends
        assert 'yield_trends' in result
        assert result['yield_trends']['data_available'] is True
        assert 'avg_yoy_growth' in result['yield_trends']
        
        # Check seasonal patterns
        assert 'seasonal_patterns' in result
        assert 'overall_performance' in result['seasonal_patterns']
        
        # Check planting windows
        assert 'planting_windows' in result
        assert result['planting_windows']['optimal_planting_start'] is not None
    
    def test_analyze_season_trend_without_data(self, service: SeasonalTrendService):
        """Test analyzing season trend with no data"""
        result = service.analyze_season_trend(
            crop_type="NonExistentCrop",
            state="NonExistentState",
            season="kharif",
            years=5
        )
        
        assert result['data_available'] is False
        assert 'error' in result or result['price_trends']['data_available'] is False
    
    def test_analyze_seasonal_trends_all_seasons(
        self,
        service: SeasonalTrendService,
        sample_market_data,
        sample_yield_data
    ):
        """Test analyzing all seasonal trends"""
        result = service.analyze_seasonal_trends(
            crop_type="Wheat",
            state="Punjab",
            district="Ludhiana",
            years=3
        )
        
        assert 'seasonal_breakdown' in result
        assert 'kharif' in result['seasonal_breakdown']
        assert 'rabi' in result['seasonal_breakdown']
        assert 'zaid' in result['seasonal_breakdown']
        
        # Rabi should have data
        assert result['seasonal_breakdown']['rabi']['data_available'] is True
        
        # Check for best season recommendation
        if 'best_season' in result:
            assert 'season' in result['best_season']
            assert 'score' in result['best_season']
    
    def test_invalid_season(self, service: SeasonalTrendService):
        """Test with invalid season name"""
        result = service.analyze_season_trend(
            crop_type="Wheat",
            state="Punjab",
            season="invalid_season",
            years=3
        )
        
        assert 'error' in result
    
    def test_store_seasonal_trend(
        self,
        service: SeasonalTrendService,
        sample_market_data,
        sample_yield_data
    ):
        """Test storing seasonal trend analysis"""
        # First analyze
        analysis = service.analyze_season_trend(
            crop_type="Wheat",
            state="Punjab",
            district="Ludhiana",
            season="rabi",
            years=3
        )
        
        # Then store
        stored_trend = service.store_seasonal_trend(
            crop_type="Wheat",
            state="Punjab",
            district="Ludhiana",
            season="rabi",
            trend_data=analysis
        )
        
        assert stored_trend.id is not None
        assert stored_trend.crop_type == "Wheat"
        assert stored_trend.state == "Punjab"
        assert stored_trend.planting_season == "rabi"
        assert stored_trend.price_trend_yoy is not None
        assert stored_trend.yield_trend_yoy is not None
    
    def test_seasonal_price_trends(
        self,
        service: SeasonalTrendService,
        sample_market_data
    ):
        """Test price trend analysis"""
        price_trends = service._analyze_seasonal_price_trends(
            crop_type="Wheat",
            state="Punjab",
            district="Ludhiana",
            season="rabi",
            years=3
        )
        
        assert price_trends['data_available'] is True
        assert 'avg_yoy_growth' in price_trends
        assert 'trend' in price_trends
        assert price_trends['trend'] in ['increasing', 'stable', 'decreasing']
        assert 'current_avg_price' in price_trends
        assert 'price_volatility' in price_trends
    
    def test_seasonal_yield_trends(
        self,
        service: SeasonalTrendService,
        sample_yield_data
    ):
        """Test yield trend analysis"""
        yield_trends = service._analyze_seasonal_yield_trends(
            crop_type="Wheat",
            state="Punjab",
            district="Ludhiana",
            season="rabi",
            years=3
        )
        
        assert yield_trends['data_available'] is True
        assert 'avg_yoy_growth' in yield_trends
        assert 'trend' in yield_trends
        assert yield_trends['trend'] in ['improving', 'stable', 'declining']
        assert 'current_avg_yield' in yield_trends
    
    def test_planting_windows(self, service: SeasonalTrendService):
        """Test planting window determination"""
        planting_windows = service._determine_planting_windows(
            crop_type="Wheat",
            state="Punjab",
            season="rabi",
            price_trends={'data_available': True, 'trend': 'increasing'},
            yield_trends={'data_available': True, 'trend': 'improving'}
        )
        
        assert 'optimal_planting_start' in planting_windows
        assert 'optimal_planting_end' in planting_windows
        assert 'expected_harvest_start' in planting_windows
        assert 'expected_harvest_end' in planting_windows
        assert 'recommendation' in planting_windows
    
    def test_season_months_definition(self, service: SeasonalTrendService):
        """Test season month definitions"""
        assert 'kharif' in service.SEASON_MONTHS
        assert 'rabi' in service.SEASON_MONTHS
        assert 'zaid' in service.SEASON_MONTHS
        
        # Check kharif months
        assert 'planting' in service.SEASON_MONTHS['kharif']
        assert 'harvest' in service.SEASON_MONTHS['kharif']
        
        # Check rabi months
        assert 'planting' in service.SEASON_MONTHS['rabi']
        assert 'harvest' in service.SEASON_MONTHS['rabi']
