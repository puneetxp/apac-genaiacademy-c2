"""
Marketplace Service for automatic listing creation and management
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
import uuid

from app.orm.marketplace_listing import MarketplaceListing
from app.orm.buyer_interest import BuyerInterest
from app.orm.crop import Crop
from app.orm.farm import Farm
from app.orm.farm_plot import FarmPlot
from app.orm.user import User
from app.services.bedrock_service import bedrock_service

logger = logging.getLogger(__name__)


class MarketplaceService:
    """
    Service for managing marketplace listings and buyer-farmer connections
    
    Validates: AC4.1, AC4.2, AC4.3, AC4.4, AC4.5
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.bedrock = bedrock_service
    
    def create_automatic_listing(
        self,
        crop_id: uuid.UUID,
        farmer_id: uuid.UUID,
        yield_prediction: Optional[Dict[str, Any]] = None
    ) -> MarketplaceListing:
        """
        Automatically create marketplace listing when farmer plants a crop
        
        Args:
            crop_id: Crop UUID
            farmer_id: Farmer UUID
            yield_prediction: Optional yield prediction data
            
        Returns:
            Created Listing instance
            
        Validates: AC4.1 - Automatic listing when farmer confirms crop selection
        Validates: AC4.2 - Include all required fields
        """
        try:
            # Get crop details
            crop = self.db.query(Crop).filter(Crop.id == crop_id).first()
            if not crop:
                raise ValueError(f"Crop {crop_id} not found")
            
            # Get plot and farm details
            plot = self.db.query(FarmPlot).filter(FarmPlot.id == crop.plot_id).first()
            if not plot:
                raise ValueError(f"Plot {crop.plot_id} not found")
            
            farm = self.db.query(Farm).filter(Farm.id == plot.farm_id).first()
            if not farm:
                raise ValueError(f"Farm {plot.farm_id} not found")
            
            # Get farmer details
            farmer = self.db.query(User).filter(User.id == farmer_id).first()
            if not farmer:
                raise ValueError(f"Farmer {farmer_id} not found")
            
            # Check if listing already exists
            existing_listing = self.db.query(MarketplaceListing).filter(
                MarketplaceListing.crop_id == crop_id
            ).first()
            
            if existing_listing:
                logger.info(f"Listing already exists for crop {crop_id}")
                return existing_listing
            
            # Get crop variety details
            crop_variety = crop.crop_variety
            crop_type = crop_variety.crop_type if crop_variety else "Unknown"
            variety_name = crop_variety.variety_name if crop_variety else "Standard"
            
            # Use yield prediction or generate one
            if not yield_prediction:
                yield_prediction = self._generate_yield_prediction(crop, plot, farm)
            
            # Extract prediction details
            expected_yield = yield_prediction.get('total_expected_yield', crop.area_planted * 20)
            harvest_date = yield_prediction.get('harvest_date', 
                                               (crop.expected_harvest_date or 
                                                crop.planting_date + timedelta(days=120)).isoformat())
            quality_grade = yield_prediction.get('quality_grade', 'B')
            confidence_score = yield_prediction.get('confidence_score', 0.85)
            
            # Parse harvest date
            if isinstance(harvest_date, str):
                harvest_date = datetime.fromisoformat(harvest_date).date()
            
            # Calculate harvest window
            harvest_window_start = harvest_date - timedelta(days=7)
            harvest_window_end = harvest_date + timedelta(days=7)
            
            # Get market intelligence
            market_data = self._get_market_intelligence(crop_type, farm.location_state, farm.location_district)
            
            # Create listing title and description
            title = f"{crop_type} ({variety_name}) - {farm.location_district}, {farm.location_state}"
            description = self._generate_listing_description(
                crop_type=crop_type,
                variety=variety_name,
                area=float(crop.area_planted),
                expected_yield=float(expected_yield),
                quality_grade=quality_grade,
                harvest_date=harvest_date,
                farm_name=farm.name
            )
            
            # Create listing
            listing = MarketplaceListing(
                id=uuid.uuid4(),
                crop_id=crop_id,
                farmer_id=farmer_id,
                
                # Listing details
                title=title,
                description=description,
                
                # Crop information
                crop_type=crop_type,
                crop_variety=variety_name,
                
                # Quantity and quality
                estimated_quantity=expected_yield,
                quantity_unit='quintals',
                min_quantity=expected_yield * 0.1,  # 10% minimum
                max_quantity=expected_yield,
                quality_grade=quality_grade,
                quality_confidence=confidence_score,
                quality_description=f"Expected {quality_grade} grade based on AI prediction",
                
                # Harvest information
                expected_harvest_date=harvest_date,
                harvest_date_confidence=confidence_score,
                harvest_window_start=harvest_window_start,
                harvest_window_end=harvest_window_end,
                
                # Pricing
                asking_price_per_unit=market_data.get('price_per_quintal', 2000),
                price_negotiable=True,
                
                # Location
                location_state=farm.location_state,
                location_district=farm.location_district,
                location_block=farm.location_block,
                exact_location_shared=False,
                
                # Farmer contact (MVP - Direct Contact)
                contact_enabled=True,
                farmer_phone=farmer.phone,
                farmer_email=farmer.email,
                preferred_contact_method='phone',
                
                # Market intelligence
                market_demand_score=market_data.get('demand_score', 0.75),
                price_trend=market_data.get('price_trend', 'stable'),
                yoy_price_growth=market_data.get('yoy_growth', 0),
                
                # Status
                status='active',
                visibility='public',
                
                # Booking
                advance_booking_allowed=True,
                advance_payment_required=False,
                
                # Expiry (30 days after harvest window end)
                expires_at=datetime.combine(harvest_window_end + timedelta(days=30), datetime.min.time())
            )
            
            self.db.add(listing)
            self.db.commit()
            self.db.refresh(listing)
            
            logger.info(f"Created automatic listing {listing.id} for crop {crop_id}")
            
            return listing
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating automatic listing: {e}")
            raise
    
    def _generate_yield_prediction(
        self,
        crop: Crop,
        plot: FarmPlot,
        farm: Farm
    ) -> Dict[str, Any]:
        """Generate yield prediction using Bedrock"""
        try:
            crop_variety = crop.crop_variety
            crop_type = crop_variety.crop_type if crop_variety else "Unknown"
            variety_name = crop_variety.variety_name if crop_variety else "Standard"
            
            prediction = self.bedrock.predict_yield_and_harvest(
                crop_name=crop_type,
                variety=variety_name,
                state=farm.location_state,
                district=farm.location_district,
                planting_date=crop.planting_date.isoformat(),
                area_acres=float(crop.area_planted),
                soil_type=plot.soil_type,
                irrigation_type=plot.irrigation_type
            )
            
            return prediction if prediction else self._get_fallback_prediction(crop)
            
        except Exception as e:
            logger.warning(f"Error generating yield prediction: {e}")
            return self._get_fallback_prediction(crop)
    
    def _get_fallback_prediction(self, crop: Crop) -> Dict[str, Any]:
        """Fallback prediction if Bedrock fails"""
        harvest_date = crop.expected_harvest_date or (crop.planting_date + timedelta(days=120))
        expected_yield = float(crop.area_planted) * 20  # Conservative 20 quintals/acre
        
        return {
            'harvest_date': harvest_date.isoformat(),
            'total_expected_yield': expected_yield,
            'quality_grade': 'B',
            'confidence_score': 0.75
        }
    
    def _get_market_intelligence(
        self,
        crop_type: str,
        state: str,
        district: str
    ) -> Dict[str, Any]:
        """Get market intelligence for pricing"""
        # Simplified market data for MVP
        # In production, this would query the market_intelligence tables
        
        base_prices = {
            'rice': 2000,
            'wheat': 2100,
            'maize': 1800,
            'cotton': 5500,
            'soybean': 4000,
            'groundnut': 5000,
            'chickpea': 5500,
            'pigeon pea': 6000
        }
        
        crop_lower = crop_type.lower()
        price = base_prices.get(crop_lower, 2500)
        
        return {
            'price_per_quintal': price,
            'demand_score': 0.75,
            'price_trend': 'stable',
            'yoy_growth': 5.0
        }
    
    def _generate_listing_description(
        self,
        crop_type: str,
        variety: str,
        area: float,
        expected_yield: float,
        quality_grade: str,
        harvest_date: date,
        farm_name: str
    ) -> str:
        """Generate listing description"""
        return f"""High-quality {crop_type} ({variety}) available for advance booking.

Farm: {farm_name}
Cultivated Area: {area:.2f} acres
Expected Yield: {expected_yield:.2f} quintals
Quality Grade: {quality_grade}
Expected Harvest: {harvest_date.strftime('%B %Y')}

This crop is being grown using modern agricultural practices with AI-powered crop management. 
Advance booking available with flexible payment terms.

Contact farmer directly for inquiries and negotiations."""
    
    def register_buyer_interest(
        self,
        listing_id: uuid.UUID,
        buyer_id: uuid.UUID,
        interest_data: Dict[str, Any]
    ) -> BuyerInterest:
        """
        Register buyer interest in a listing
        
        Validates: AC4.3 - Buyers can express interest in advance booking
        """
        try:
            # Check if interest already exists
            existing_interest = self.db.query(BuyerInterest).filter(
                BuyerInterest.listing_id == listing_id,
                BuyerInterest.buyer_id == buyer_id
            ).first()
            
            if existing_interest:
                logger.info(f"Buyer interest already exists for listing {listing_id}")
                return existing_interest
            
            # Create buyer interest
            interest = BuyerInterest(
                id=uuid.uuid4(),
                listing_id=listing_id,
                buyer_id=buyer_id,
                interest_type=interest_data.get('interest_type', 'inquiry'),
                quantity_interested=interest_data.get('quantity_interested'),
                preferred_price=interest_data.get('preferred_price'),
                buyer_phone=interest_data.get('buyer_phone'),
                buyer_email=interest_data.get('buyer_email'),
                buyer_company=interest_data.get('buyer_company'),
                quality_requirements=interest_data.get('quality_requirements'),
                delivery_requirements=interest_data.get('delivery_requirements'),
                payment_terms=interest_data.get('payment_terms'),
                message_to_farmer=interest_data.get('message'),
                contact_requested=True,
                contact_request_date=datetime.now(),
                status='pending'
            )
            
            self.db.add(interest)
            
            # Update listing interest count
            listing = self.db.query(MarketplaceListing).filter(MarketplaceListing.id == listing_id).first()
            if listing:
                listing.interest_count += 1
            
            self.db.commit()
            self.db.refresh(interest)
            
            logger.info(f"Registered buyer interest {interest.id} for listing {listing_id}")
            
            return interest
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error registering buyer interest: {e}")
            raise
    
    def get_listings(
        self,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: str = 'harvest_date',
        sort_order: str = 'asc',
        limit: int = 20,
        offset: int = 0
    ) -> tuple[List[Dict], int]:
        """
        Get marketplace listings with filters, sorting, and pagination
        
        Args:
            filters: Dictionary of filter criteria
            sort_by: Field to sort by (harvest_date, quantity, quality_grade)
            sort_order: Sort order (asc, desc)
            limit: Maximum number of results (default 20)
            offset: Number of results to skip (default 0)
            
        Returns:
            Tuple of (listings, total_count)
            
        Validates: AC4 - Marketplace search with filters, pagination, and sorting
        """
        try:
            # Base query - only active listings using custom ORM
            query = MarketplaceListing.where({'status': ['active']})
            
            # Build count query with same filters
            count_query = MarketplaceListing.where({'status': ['active']})
            
            # Apply filters
            if filters:
                # Crop type filter - use ILIKE for case-insensitive partial match
                if filters.get('crop_type'):
                    crop_type = filters['crop_type'].strip()
                    query = query.and_where_custom([['crop_type', 'ILIKE', f'%{crop_type}%']])
                    count_query = count_query.and_where_custom([['crop_type', 'ILIKE', f'%{crop_type}%']])
                
                # State filter - exact match
                if filters.get('state'):
                    query = query.and_where({'location_state': [filters['state']]})
                    count_query = count_query.and_where({'location_state': [filters['state']]})
                
                # District filter - exact match
                if filters.get('district'):
                    query = query.and_where({'location_district': [filters['district']]})
                    count_query = count_query.and_where({'location_district': [filters['district']]})
                
                # Quantity filters - range comparisons
                if filters.get('min_quantity'):
                    query = query.and_where_custom([['estimated_quantity', '>=', filters['min_quantity']]])
                    count_query = count_query.and_where_custom([['estimated_quantity', '>=', filters['min_quantity']]])
                
                if filters.get('max_quantity'):
                    query = query.and_where_custom([['estimated_quantity', '<=', filters['max_quantity']]])
                    count_query = count_query.and_where_custom([['estimated_quantity', '<=', filters['max_quantity']]])
                
                # Harvest date range filters
                if filters.get('harvest_from'):
                    query = query.and_where_custom([['expected_harvest_date', '>=', filters['harvest_from']]])
                    count_query = count_query.and_where_custom([['expected_harvest_date', '>=', filters['harvest_from']]])
                
                if filters.get('harvest_to'):
                    query = query.and_where_custom([['expected_harvest_date', '<=', filters['harvest_to']]])
                    count_query = count_query.and_where_custom([['expected_harvest_date', '<=', filters['harvest_to']]])
                
                # Quality grade filter - exact match
                if filters.get('quality_grade'):
                    query = query.and_where({'quality_grade': [filters['quality_grade']]})
                    count_query = count_query.and_where({'quality_grade': [filters['quality_grade']]})
                
                # Price range filters
                if filters.get('min_price'):
                    query = query.and_where_custom([['asking_price_per_unit', '>=', filters['min_price']]])
                    count_query = count_query.and_where_custom([['asking_price_per_unit', '>=', filters['min_price']]])
                
                if filters.get('max_price'):
                    query = query.and_where_custom([['asking_price_per_unit', '<=', filters['max_price']]])
                    count_query = count_query.and_where_custom([['asking_price_per_unit', '<=', filters['max_price']]])
            
            # Get total count before pagination
            count_result = count_query.count()
            total_count = count_result[0]['count'] if count_result else 0
            
            # Apply sorting using raw SQL ORDER BY
            sort_column_name = 'expected_harvest_date'  # default
            
            if sort_by == 'quantity':
                sort_column_name = 'estimated_quantity'
            elif sort_by == 'quality_grade':
                sort_column_name = 'quality_grade'
            elif sort_by == 'price':
                sort_column_name = 'asking_price_per_unit'
            elif sort_by == 'harvest_date':
                sort_column_name = 'expected_harvest_date'
            
            # Use raw SQL for ORDER BY clause
            query.db.rawsql(f' ORDER BY "{sort_column_name}" {sort_order.upper()} ')
            
            # Apply pagination
            query.db.limit_q(limit).offset_q(offset)
            
            # Execute query and get results
            query.get()
            listings = query.items
            
            logger.info(f"Retrieved {len(listings)} listings (total: {total_count})")
            
            return listings, total_count
            
        except Exception as e:
            logger.error(f"Error getting listings: {e}")
            raise
    
    def get_listing_detail(self, listing_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """
        Get detailed listing information with production predictions and market intelligence
        
        Args:
            listing_id: Listing UUID
            
        Returns:
            Dictionary with full listing details, production predictions, and market intelligence
            
        Validates: AC4 - Listing detail view with comprehensive information
        """
        try:
            from app.orm.crop_market_data import CropMarketData
            from app.orm.crop import Crop
            
            # Get listing
            listing = self.db.query(MarketplaceListing).filter(MarketplaceListing.id == listing_id).first()
            
            if not listing:
                return None
            
            # Increment view count
            listing.view_count += 1
            self.db.commit()
            
            # Get crop details for production predictions
            crop = self.db.query(Crop).filter(Crop.id == listing.crop_id).first()
            
            # Get market intelligence data
            market_data = self._get_market_intelligence_detail(
                listing.crop_type,
                listing.location_state,
                listing.location_district
            )
            
            # Build production predictions
            production_predictions = {
                'estimated_yield': {
                    'quantity': float(listing.estimated_quantity),
                    'unit': listing.quantity_unit,
                    'confidence': float(listing.harvest_date_confidence) if listing.harvest_date_confidence else 0.85
                },
                'quality_prediction': {
                    'grade': listing.quality_grade,
                    'confidence': float(listing.quality_confidence) if listing.quality_confidence else 0.85,
                    'description': listing.quality_description
                },
                'harvest_timing': {
                    'expected_date': listing.expected_harvest_date.isoformat(),
                    'window_start': listing.harvest_window_start.isoformat() if listing.harvest_window_start else None,
                    'window_end': listing.harvest_window_end.isoformat() if listing.harvest_window_end else None,
                    'confidence': float(listing.harvest_date_confidence) if listing.harvest_date_confidence else 0.85
                }
            }
            
            # Add crop-specific details if available
            if crop:
                production_predictions['crop_details'] = {
                    'planting_date': crop.planting_date.isoformat() if crop.planting_date else None,
                    'area_planted': float(crop.area_planted) if crop.area_planted else None,
                    'growth_stage': crop.growth_stage if hasattr(crop, 'growth_stage') else None
                }
            
            # Build comprehensive response
            listing_detail = {
                'id': str(listing.id),
                'title': listing.title,
                'description': listing.description,
                
                # Crop information
                'crop_type': listing.crop_type,
                'crop_variety': listing.crop_variety,
                
                # Production predictions
                'production_predictions': production_predictions,
                
                # Quantity and quality
                'estimated_quantity': float(listing.estimated_quantity),
                'quantity_unit': listing.quantity_unit,
                'min_quantity': float(listing.min_quantity) if listing.min_quantity else None,
                'max_quantity': float(listing.max_quantity) if listing.max_quantity else None,
                'quality_grade': listing.quality_grade,
                'quality_confidence': float(listing.quality_confidence) if listing.quality_confidence else None,
                
                # Harvest information
                'expected_harvest_date': listing.expected_harvest_date.isoformat(),
                'harvest_window': {
                    'start': listing.harvest_window_start.isoformat() if listing.harvest_window_start else None,
                    'end': listing.harvest_window_end.isoformat() if listing.harvest_window_end else None
                },
                
                # Pricing
                'pricing': {
                    'asking_price_per_unit': float(listing.asking_price_per_unit) if listing.asking_price_per_unit else None,
                    'price_negotiable': listing.price_negotiable,
                    'currency': listing.currency
                },
                
                # Location
                'location': {
                    'state': listing.location_state,
                    'district': listing.location_district,
                    'block': listing.location_block
                },
                
                # Farmer contact options
                'contact': {
                    'enabled': listing.contact_enabled,
                    'phone': listing.farmer_phone if listing.contact_enabled else None,
                    'email': listing.farmer_email if listing.contact_enabled else None,
                    'preferred_method': listing.preferred_contact_method
                },
                
                # Market intelligence context
                'market_intelligence': market_data,
                
                # Interest registration
                'interest_registration': {
                    'allowed': listing.advance_booking_allowed,
                    'endpoint': f'/marketplace/buyer-interest',
                    'listing_id': str(listing.id)
                },
                
                # Status and analytics
                'status': listing.status,
                'advance_booking_allowed': listing.advance_booking_allowed,
                'view_count': listing.view_count,
                'interest_count': listing.interest_count,
                'listed_at': listing.listed_at.isoformat(),
                
                # Media
                'images': listing.images if listing.images else [],
                'videos': listing.videos if listing.videos else []
            }
            
            return listing_detail
            
        except Exception as e:
            logger.error(f"Error getting listing detail: {e}")
            raise
    
    def _get_market_intelligence_detail(
        self,
        crop_type: str,
        state: str,
        district: str
    ) -> Dict[str, Any]:
        """
        Get detailed market intelligence for a crop in a specific location
        
        Args:
            crop_type: Crop type
            state: State name
            district: District name
            
        Returns:
            Dictionary with market intelligence data including YoY growth and demand trends
        """
        try:
            from app.orm.crop_market_data import CropMarketData
            from datetime import datetime
            from sqlalchemy import func, desc
            
            current_year = datetime.now().year
            current_month = datetime.now().month
            
            # Get recent market data (last 12 months)
            recent_data = self.db.query(CropMarketData).filter(
                CropMarketData.crop_type.ilike(f'%{crop_type}%'),
                CropMarketData.state == state,
                CropMarketData.year >= current_year - 1
            ).order_by(desc(CropMarketData.year), desc(CropMarketData.month)).limit(12).all()
            
            # Get district-specific data if available
            district_data = self.db.query(CropMarketData).filter(
                CropMarketData.crop_type.ilike(f'%{crop_type}%'),
                CropMarketData.state == state,
                CropMarketData.district == district,
                CropMarketData.year >= current_year - 1
            ).order_by(desc(CropMarketData.year), desc(CropMarketData.month)).first()
            
            # Calculate YoY growth
            yoy_growth = None
            if len(recent_data) >= 2:
                # Compare current year with previous year
                current_year_data = [d for d in recent_data if d.year == current_year]
                previous_year_data = [d for d in recent_data if d.year == current_year - 1]
                
                if current_year_data and previous_year_data:
                    current_avg = sum(float(d.avg_price_per_quintal) for d in current_year_data) / len(current_year_data)
                    previous_avg = sum(float(d.avg_price_per_quintal) for d in previous_year_data) / len(previous_year_data)
                    
                    if previous_avg > 0:
                        yoy_growth = ((current_avg - previous_avg) / previous_avg) * 100
            
            # Determine demand trend
            demand_trend = 'stable'
            demand_score = 0.75
            
            if recent_data:
                latest = recent_data[0]
                demand_score = float(latest.market_demand_score) if latest.market_demand_score else 0.75
                
                # Analyze price trend over last 6 months
                if len(recent_data) >= 6:
                    recent_6_months = recent_data[:6]
                    prices = [float(d.avg_price_per_quintal) for d in recent_6_months]
                    
                    # Simple trend analysis
                    if prices[0] > prices[-1] * 1.1:
                        demand_trend = 'increasing'
                    elif prices[0] < prices[-1] * 0.9:
                        demand_trend = 'decreasing'
                    else:
                        demand_trend = 'stable'
            
            # Get price range
            price_range = {
                'min': None,
                'max': None,
                'average': None
            }
            
            if recent_data:
                prices = [float(d.avg_price_per_quintal) for d in recent_data]
                price_range = {
                    'min': min(prices),
                    'max': max(prices),
                    'average': sum(prices) / len(prices)
                }
            
            # Build market intelligence response
            market_intelligence = {
                'demand_score': demand_score,
                'demand_trend': demand_trend,
                'price_trend': recent_data[0].price_trend if recent_data else 'stable',
                'yoy_growth': round(yoy_growth, 2) if yoy_growth is not None else None,
                'yoy_growth_description': self._get_yoy_growth_description(yoy_growth),
                'price_range': price_range,
                'market_context': {
                    'state': state,
                    'district': district,
                    'data_points': len(recent_data),
                    'last_updated': recent_data[0].updated_at.isoformat() if recent_data else None
                },
                'seasonal_insights': self._get_seasonal_insights(crop_type, state, recent_data)
            }
            
            return market_intelligence
            
        except Exception as e:
            logger.warning(f"Error getting market intelligence detail: {e}")
            # Return fallback data
            return {
                'demand_score': 0.75,
                'demand_trend': 'stable',
                'price_trend': 'stable',
                'yoy_growth': None,
                'yoy_growth_description': 'Data not available',
                'price_range': {'min': None, 'max': None, 'average': None},
                'market_context': {
                    'state': state,
                    'district': district,
                    'data_points': 0,
                    'last_updated': None
                },
                'seasonal_insights': None
            }
    
    def _get_yoy_growth_description(self, yoy_growth: Optional[float]) -> str:
        """Get human-readable description of YoY growth"""
        if yoy_growth is None:
            return "Historical data not available"
        
        if yoy_growth > 15:
            return "Strong price growth - High demand"
        elif yoy_growth > 5:
            return "Moderate price growth - Increasing demand"
        elif yoy_growth > -5:
            return "Stable prices - Steady demand"
        elif yoy_growth > -15:
            return "Moderate price decline - Decreasing demand"
        else:
            return "Significant price decline - Low demand"
    
    def _get_seasonal_insights(
        self,
        crop_type: str,
        state: str,
        recent_data: List
    ) -> Optional[Dict[str, Any]]:
        """Get seasonal insights for the crop"""
        if not recent_data:
            return None
        
        try:
            # Group by season
            seasonal_prices = {}
            for data in recent_data:
                if data.season:
                    season = data.season.lower()
                    if season not in seasonal_prices:
                        seasonal_prices[season] = []
                    seasonal_prices[season].append(float(data.avg_price_per_quintal))
            
            # Calculate average by season
            seasonal_averages = {}
            for season, prices in seasonal_prices.items():
                seasonal_averages[season] = sum(prices) / len(prices)
            
            # Find best season
            best_season = None
            if seasonal_averages:
                best_season = max(seasonal_averages, key=seasonal_averages.get)
            
            return {
                'seasonal_prices': seasonal_averages,
                'best_season': best_season,
                'best_season_price': seasonal_averages.get(best_season) if best_season else None
            }
            
        except Exception as e:
            logger.warning(f"Error getting seasonal insights: {e}")
            return None
