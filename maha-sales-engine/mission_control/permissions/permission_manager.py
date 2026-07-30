#!/usr/bin/env python3
"""
MAHA Sales Engine V1 - Mission Control Permissions

Role-based access control and authorization for the Mission Control system.
"""

import sys
import time
import secrets
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.auth import AuthManager, UserRole, Permission
from shared.logging_utils import get_logger

logger = get_logger("maha-sales-engine.mission-control.permissions")


class MissionPermissionLevel(Enum):
    """Mission Control permission levels"""
    CEO = "ceo"
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


@dataclass
class PermissionRule:
    """Permission rule definition"""
    resource: str
    action: str
    required_level: str
    description: str


class PermissionManager:
    """
    Manages role-based access control for Mission Control.
    
    Provides permission checking, role management,
    and access control enforcement for all mission control operations.
    """
    
    def __init__(self, auth_manager: AuthManager):
        """
        Initialize permission manager.
        
        Args:
            auth_manager: Authentication manager instance
        """
        self.auth = auth_manager
        self.logger = get_logger("maha-sales-engine.mission-control.permissions")
        self._role_hierarchy = self._build_role_hierarchy()
        self._permission_rules = self._load_permission_rules()
    
    def _build_role_hierarchy(self) -> Dict[str, int]:
        """Build role hierarchy for permission inheritance"""
        return {
            MissionPermissionLevel.CEO.value: 100,
            MissionPermissionLevel.ADMIN.value: 80,
            MissionPermissionLevel.OPERATOR.value: 60,
            MissionPermissionLevel.VIEWER.value: 40
        }
    
    def _load_permission_rules(self) -> List[PermissionRule]:
        """Load permission rules"""
        return [
            PermissionRule("mission", "create", MissionPermissionLevel.ADMIN.value, "Create new missions"),
            PermissionRule("mission", "read", MissionPermissionLevel.VIEWER.value, "View missions"),
            PermissionRule("mission", "update", MissionPermissionLevel.OPERATOR.value, "Update missions"),
            PermissionRule("mission", "delete", MissionPermissionLevel.ADMIN.value, "Delete missions"),
            PermissionRule("metric", "read", MissionPermissionLevel.VIEWER.value, "View metrics"),
            PermissionRule("metric", "write", MissionPermissionLevel.OPERATOR.value, "Write metrics"),
            PermissionRule("alert", "read", MissionPermissionLevel.VIEWER.value, "View alerts"),
            PermissionRule("alert", "write", MissionPermissionLevel.OPERATOR.value, "Create alerts"),
            PermissionRule("alert", "delete", MissionPermissionLevel.ADMIN.value, "Delete alerts"),
            PermissionRule("audit", "read", MissionPermissionLevel.OPERATOR.value, "View audit logs"),
            PermissionRule("system", "admin", MissionPermissionLevel.CEO.value, "System administration"),
        ]
    
    def check_permission(self, user_role: str, resource: str, action: str) -> bool:
        """
        Check if user has permission for resource action.
        
        Args:
            user_role: User's role
            resource: Resource being accessed
            action: Action being performed
            
        Returns:
            True if authorized, False otherwise
        """
        try:
            user_level = self._role_hierarchy.get(user_role, 0)
            
            # Find matching rule
            for rule in self._permission_rules:
                if rule.resource == resource and rule.action == action:
                    required_level = self._role_hierarchy.get(rule.required_level, 100)
                    if user_level >= required_level:
                        self.logger.debug(f"Permission granted: {user_role} can {action} {resource}")
                        return True
                    else:
                        self.logger.warning(f"Permission denied: {user_role} cannot {action} {resource}")
                        return False
            
            # No specific rule found, deny by default
            self.logger.warning(f"No permission rule found for {resource}:{action}")
            return False
        except Exception as e:
            self.logger.error(f"Permission check failed: {e}")
            return False
    
    def has_permission(self, user_role: str, resource: str, action: str) -> bool:
        """
        Alias for check_permission.
        
        Args:
            user_role: User's role
            resource: Resource being accessed
            action: Action being performed
            
        Returns:
            True if authorized, False otherwise
        """
        return self.check_permission(user_role, resource, action)
    
    def get_user_permissions(self, user_role: str) -> List[str]:
        """
        Get all permissions for a user role.
        
        Args:
            user_role: User's role
            
        Returns:
            List of permission strings
        """
        try:
            user_level = self._role_hierarchy.get(user_role, 0)
            permissions = []
            
            for rule in self._permission_rules:
                required_level = self._role_hierarchy.get(rule.required_level, 100)
                if user_level >= required_level:
                    permissions.append(f"{rule.resource}:{rule.action}")
            
            return permissions
        except Exception as e:
            self.logger.error(f"Failed to get permissions for role {user_role}: {e}")
            return []
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate authentication token.
        
        Args:
            token: Authentication token
            
        Returns:
            User information if valid, None otherwise
        """
        try:
            # Delegate to auth manager
            return self.auth.validate_api_key(token)
        except Exception as e:
            self.logger.error(f"Token validation failed: {e}")
            return None
    
    def create_access_token(self, user_id: str, role: str) -> str:
        """
        Create access token for user.
        
        Args:
            user_id: User identifier
            role: User role
            
        Returns:
            Access token
        """
        try:
            # Delegate to auth manager
            return self.auth.create_api_key(user_id, role, [])
        except Exception as e:
            self.logger.error(f"Failed to create access token: {e}")
            raise
    
    def refresh_permission_rules(self) -> None:
        """Refresh permission rules from configuration"""
        try:
            self._permission_rules = self._load_permission_rules()
            self.logger.info("Permission rules refreshed")
        except Exception as e:
            self.logger.error(f"Failed to refresh permission rules: {e}")
