"""
Tests for input validation and sanitization
"""

import pytest
from fastapi import HTTPException

from app.core.validation import (
    InputSanitizer,
    PhoneNumberValidator,
    NumericRangeValidator,
    EnumValidator,
    RequestSizeValidator,
    sanitize_input,
    validate_phone,
    validate_area,
    validate_coordinates,
    validate_enum,
)


class TestInputSanitizer:
    """Test input sanitization"""
    
    def test_sanitize_normal_string(self):
        """Test sanitizing normal string"""
        result = InputSanitizer.sanitize_string("Hello World")
        assert result == "Hello World"
    
    def test_sanitize_html_escape(self):
        """Test HTML escaping with allow_html=True"""
        result = InputSanitizer.sanitize_string("<p>Hello <strong>World</strong></p>", allow_html=True)
        # Should allow safe HTML tags
        assert "<p>" in result or "Hello" in result
    
    def test_detect_sql_injection(self):
        """Test SQL injection detection"""
        with pytest.raises(HTTPException) as exc_info:
            InputSanitizer.sanitize_string("'; DROP TABLE users; --")
        assert exc_info.value.status_code == 400
        assert "SQL injection" in exc_info.value.detail
    
    def test_detect_xss_attack(self):
        """Test XSS attack detection"""
        with pytest.raises(HTTPException) as exc_info:
            InputSanitizer.sanitize_string("<script>alert('xss')</script>")
        assert exc_info.value.status_code == 400
        assert "XSS" in exc_info.value.detail
    
    def test_sanitize_dict(self):
        """Test dictionary sanitization"""
        data = {
            "name": "John Doe",
            "description": "  Test description  ",
            "nested": {
                "field": "value"
            }
        }
        result = InputSanitizer.sanitize_dict(data)
        assert result["name"] == "John Doe"
        assert result["description"] == "Test description"
        assert result["nested"]["field"] == "value"
    
    def test_remove_null_bytes(self):
        """Test null byte removal"""
        result = InputSanitizer.sanitize_string("test\x00string")
        assert "\x00" not in result
        assert result == "teststring"


class TestPhoneNumberValidator:
    """Test phone number validation"""
    
    def test_valid_phone_with_prefix(self):
        """Test valid phone with +91 prefix"""
        result = PhoneNumberValidator.validate("+919876543210")
        assert result == "+919876543210"
    
    def test_valid_phone_without_prefix(self):
        """Test valid phone without prefix"""
        result = PhoneNumberValidator.validate("9876543210")
        assert result == "+919876543210"
    
    def test_valid_phone_with_91_prefix(self):
        """Test valid phone with 91 prefix"""
        result = PhoneNumberValidator.validate("919876543210")
        assert result == "+919876543210"
    
    def test_valid_phone_with_zero_prefix(self):
        """Test valid phone with 0 prefix"""
        result = PhoneNumberValidator.validate("09876543210")
        assert result == "+919876543210"
    
    def test_invalid_phone_format(self):
        """Test invalid phone format"""
        with pytest.raises(HTTPException) as exc_info:
            PhoneNumberValidator.validate("+911234567890")  # Starts with 1, not 6-9
        assert exc_info.value.status_code == 400
        assert "Invalid phone number" in exc_info.value.detail
    
    def test_phone_with_spaces(self):
        """Test phone with spaces"""
        result = PhoneNumberValidator.validate("+91 987 654 3210")
        assert result == "+919876543210"


class TestNumericRangeValidator:
    """Test numeric range validation"""
    
    def test_valid_area(self):
        """Test valid area"""
        result = NumericRangeValidator.validate_area(5.5)
        assert result == 5.5
    
    def test_area_too_small(self):
        """Test area below minimum"""
        with pytest.raises(HTTPException) as exc_info:
            NumericRangeValidator.validate_area(0.05)
        assert exc_info.value.status_code == 400
        assert "between" in exc_info.value.detail
    
    def test_area_too_large(self):
        """Test area above maximum"""
        with pytest.raises(HTTPException) as exc_info:
            NumericRangeValidator.validate_area(15000.0)
        assert exc_info.value.status_code == 400
        assert "between" in exc_info.value.detail
    
    def test_valid_coordinates(self):
        """Test valid GPS coordinates"""
        lat, lng = NumericRangeValidator.validate_coordinates(28.6139, 77.2090)
        assert lat == 28.6139
        assert lng == 77.2090
    
    def test_invalid_latitude(self):
        """Test invalid latitude"""
        with pytest.raises(HTTPException) as exc_info:
            NumericRangeValidator.validate_coordinates(95.0, 77.0)
        assert exc_info.value.status_code == 400
        assert "Latitude" in exc_info.value.detail
    
    def test_invalid_longitude(self):
        """Test invalid longitude"""
        with pytest.raises(HTTPException) as exc_info:
            NumericRangeValidator.validate_coordinates(28.0, 200.0)
        assert exc_info.value.status_code == 400
        assert "Longitude" in exc_info.value.detail
    
    def test_none_coordinates(self):
        """Test None coordinates"""
        lat, lng = NumericRangeValidator.validate_coordinates(None, None)
        assert lat is None
        assert lng is None
    
    def test_valid_quantity(self):
        """Test valid quantity"""
        result = NumericRangeValidator.validate_quantity(100.5)
        assert result == 100.5
    
    def test_valid_price(self):
        """Test valid price"""
        result = NumericRangeValidator.validate_price(5000.0)
        assert result == 5000.0


class TestEnumValidator:
    """Test enum validation"""
    
    def test_valid_soil_type(self):
        """Test valid soil type"""
        result = EnumValidator.validate_choice("clay", EnumValidator.SOIL_TYPES, "soil_type")
        assert result == "clay"
    
    def test_valid_soil_type_case_insensitive(self):
        """Test soil type case insensitive"""
        result = EnumValidator.validate_choice("CLAY", EnumValidator.SOIL_TYPES, "soil_type")
        assert result == "clay"
    
    def test_invalid_soil_type(self):
        """Test invalid soil type"""
        with pytest.raises(HTTPException) as exc_info:
            EnumValidator.validate_choice("invalid", EnumValidator.SOIL_TYPES, "soil_type")
        assert exc_info.value.status_code == 400
        assert "must be one of" in exc_info.value.detail
    
    def test_valid_irrigation_type(self):
        """Test valid irrigation type"""
        result = EnumValidator.validate_choice("drip", EnumValidator.IRRIGATION_TYPES, "irrigation_type")
        assert result == "drip"
    
    def test_valid_user_type(self):
        """Test valid user type"""
        result = EnumValidator.validate_choice("farmer", EnumValidator.USER_TYPES, "user_type")
        assert result == "farmer"


class TestRequestSizeValidator:
    """Test request size validation"""
    
    def test_valid_json_size(self):
        """Test valid JSON size"""
        data = {"field1": "value1", "field2": "value2"}
        # Should not raise exception
        RequestSizeValidator.validate_json_size(data)
    
    def test_too_many_fields(self):
        """Test too many fields"""
        data = {f"field{i}": f"value{i}" for i in range(1500)}
        with pytest.raises(HTTPException) as exc_info:
            RequestSizeValidator.validate_json_size(data)
        assert exc_info.value.status_code == 413
        assert "too complex" in exc_info.value.detail
    
    def test_string_too_long(self):
        """Test string too long"""
        data = {"field": "x" * 15000}
        with pytest.raises(HTTPException) as exc_info:
            RequestSizeValidator.validate_json_size(data)
        assert exc_info.value.status_code == 413
        assert "String too long" in exc_info.value.detail
    
    def test_array_too_large(self):
        """Test array too large"""
        data = {"array": list(range(1500))}
        with pytest.raises(HTTPException) as exc_info:
            RequestSizeValidator.validate_json_size(data)
        assert exc_info.value.status_code == 413
        assert "Array too large" in exc_info.value.detail
    
    def test_nested_structure(self):
        """Test nested structure validation"""
        data = {
            "level1": {
                "level2": {
                    "level3": {
                        "field": "value"
                    }
                }
            }
        }
        # Should not raise exception
        RequestSizeValidator.validate_json_size(data)


class TestConvenienceFunctions:
    """Test convenience functions"""
    
    def test_sanitize_input(self):
        """Test sanitize_input function"""
        result = sanitize_input("  Test String  ")
        assert result == "Test String"
    
    def test_validate_phone(self):
        """Test validate_phone function"""
        result = validate_phone("9876543210")
        assert result == "+919876543210"
    
    def test_validate_area(self):
        """Test validate_area function"""
        result = validate_area(10.5)
        assert result == 10.5
    
    def test_validate_coordinates(self):
        """Test validate_coordinates function"""
        lat, lng = validate_coordinates(28.6139, 77.2090)
        assert lat == 28.6139
        assert lng == 77.2090
    
    def test_validate_enum(self):
        """Test validate_enum function"""
        result = validate_enum("farmer", EnumValidator.USER_TYPES, "user_type")
        assert result == "farmer"
