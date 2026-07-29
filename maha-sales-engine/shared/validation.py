#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Shared Validation
Input validation for all API endpoints.
"""

import os
import sys
import re
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.shared.validation")


class ValidationError(Exception):
    """Validation error"""
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")


class FieldValidator:
    """Field validation utilities"""
    
    @staticmethod
    def required(value: Any, field_name: str) -> Any:
        """Validate required field"""
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValidationError(field_name, "Field is required")
        return value
    
    @staticmethod
    def string(value: Any, field_name: str, max_length: int = 1000, min_length: int = 1) -> str:
        """Validate string field"""
        if not isinstance(value, str):
            raise ValidationError(field_name, "Must be a string")
        
        if len(value) < min_length:
            raise ValidationError(field_name, f"Must be at least {min_length} characters")
        
        if len(value) > max_length:
            raise ValidationError(field_name, f"Must be at most {max_length} characters")
        
        return value.strip()
    
    @staticmethod
    def integer(value: Any, field_name: str, min_value: int = None, max_value: int = None) -> int:
        """Validate integer field"""
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValidationError(field_name, "Must be an integer")
        
        if min_value is not None and value < min_value:
            raise ValidationError(field_name, f"Must be at least {min_value}")
        
        if max_value is not None and value > max_value:
            raise ValidationError(field_name, f"Must be at most {max_value}")
        
        return value
    
    @staticmethod
    def float(value: Any, field_name: str, min_value: float = None, max_value: float = None) -> float:
        """Validate float field"""
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValidationError(field_name, "Must be a number")
        
        value = float(value)
        
        if min_value is not None and value < min_value:
            raise ValidationError(field_name, f"Must be at least {min_value}")
        
        if max_value is not None and value > max_value:
            raise ValidationError(field_name, f"Must be at most {max_value}")
        
        return value
    
    @staticmethod
    def email(value: str, field_name: str) -> str:
        """Validate email field"""
        value = FieldValidator.string(value, field_name, max_length=255)
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, value):
            raise ValidationError(field_name, "Invalid email format")
        
        return value.lower()
    
    @staticmethod
    def uuid(value: str, field_name: str) -> str:
        """Validate UUID field"""
        value = FieldValidator.string(value, field_name, max_length=36)
        
        pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        if not re.match(pattern, value, re.IGNORECASE):
            raise ValidationError(field_name, "Invalid UUID format")
        
        return value.lower()
    
    @staticmethod
    def url(value: str, field_name: str) -> str:
        """Validate URL field"""
        value = FieldValidator.string(value, field_name, max_length=2048)
        
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        if not re.match(pattern, value):
            raise ValidationError(field_name, "Invalid URL format")
        
        return value
    
    @staticmethod
    def enum_value(value: str, field_name: str, allowed_values: List[str]) -> str:
        """Validate enum field"""
        value = FieldValidator.string(value, field_name)
        
        if value not in allowed_values:
            raise ValidationError(field_name, f"Must be one of: {', '.join(allowed_values)}")
        
        return value
    
    @staticmethod
    def list(value: Any, field_name: str, max_items: int = 100) -> List:
        """Validate list field"""
        if not isinstance(value, list):
            raise ValidationError(field_name, "Must be a list")
        
        if len(value) > max_items:
            raise ValidationError(field_name, f"Must have at most {max_items} items")
        
        return value
    
    @staticmethod
    def dict(value: Any, field_name: str) -> Dict:
        """Validate dict field"""
        if not isinstance(value, dict):
            raise ValidationError(field_name, "Must be an object")
        
        return value


class RequestValidator:
    """Request validation"""
    
    def __init__(self):
        self.field_validator = FieldValidator()
    
    def validate(self, data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        """Validate request data against schema"""
        validated = {}
        errors = []
        
        for field_name, field_schema in schema.items():
            field_type = field_schema.get("type", "string")
            required = field_schema.get("required", False)
            
            # Check required
            if required and field_name not in data:
                errors.append(ValidationError(field_name, "Field is required"))
                continue
            
            # Skip if not present
            if field_name not in data:
                continue
            
            value = data[field_name]
            
            # Validate by type
            try:
                if field_type == "string":
                    validated[field_name] = self.field_validator.string(
                        value, field_name,
                        max_length=field_schema.get("max_length", 1000),
                        min_length=field_schema.get("min_length", 1)
                    )
                elif field_type == "integer":
                    validated[field_name] = self.field_validator.integer(
                        value, field_name,
                        min_value=field_schema.get("min_value"),
                        max_value=field_schema.get("max_value")
                    )
                elif field_type == "float":
                    validated[field_name] = self.field_validator.float(
                        value, field_name,
                        min_value=field_schema.get("min_value"),
                        max_value=field_schema.get("max_value")
                    )
                elif field_type == "email":
                    validated[field_name] = self.field_validator.email(value, field_name)
                elif field_type == "uuid":
                    validated[field_name] = self.field_validator.uuid(value, field_name)
                elif field_type == "url":
                    validated[field_name] = self.field_validator.url(value, field_name)
                elif field_type == "enum":
                    validated[field_name] = self.field_validator.enum_value(
                        value, field_name,
                        field_schema.get("values", [])
                    )
                elif field_type == "list":
                    validated[field_name] = self.field_validator.list(
                        value, field_name,
                        max_items=field_schema.get("max_items", 100)
                    )
                elif field_type == "dict":
                    validated[field_name] = self.field_validator.dict(value, field_name)
            except ValidationError as e:
                errors.append(e)
        
        if errors:
            error_messages = [f"{e.field}: {e.message}" for e in errors]
            raise ValidationError("validation", "; ".join(error_messages))
        
        return validated


def validate_request(schema: Dict[str, Any]):
    """Decorator to validate request data"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get("request")
            if not request:
                raise ValidationError("request", "Request object not found")
            
            validator = RequestValidator()
            try:
                validated_data = validator.validate(await request.json(), schema)
                kwargs["validated_data"] = validated_data
            except ValidationError as e:
                raise HTTPException(status_code=422, detail=str(e))
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def main():
    """Test validation"""
    validator = RequestValidator()
    
    schema = {
        "email": {"type": "email", "required": True},
        "name": {"type": "string", "required": True, "max_length": 100},
        "age": {"type": "integer", "min_value": 0, "max_value": 150}
    }
    
    data = {
        "email": "test@example.com",
        "name": "John Doe",
        "age": 30
    }
    
    validated = validator.validate(data, schema)
    print(f"Validated: {validated}")
    print("Validation tests passed")


if __name__ == "__main__":
    main()
