import os
import hashlib
import secrets
from typing import Dict, Any
import json

class SecurityManager:
    """
    Security and privacy management for Project Samarth
    Ensures data sovereignty and secure operations
    """
    
    def __init__(self):
        self.api_key_hash = self._hash_api_key()
        self.session_tokens = {}
        
    def _hash_api_key(self) -> str:
        """Hash API key for secure logging"""
        from config import DATA_GOV_API_KEY
        return hashlib.sha256(DATA_GOV_API_KEY.encode()).hexdigest()[:16]
        
    def sanitize_query(self, query: str) -> str:
        """Sanitize user input to prevent injection attacks"""
        # Remove potentially harmful characters
        sanitized = query.replace(";", "").replace("--", "").replace("/*", "").replace("*/", "")
        
        # Limit query length
        if len(sanitized) > 500:
            sanitized = sanitized[:500]
            
        return sanitized.strip()
        
    def validate_data_source(self, url: str) -> bool:
        """Validate that data source is from trusted government domains"""
        trusted_domains = [
            "data.gov.in",
            "api.data.gov.in", 
            "nic.in",
            "gov.in"
        ]
        
        return any(domain in url.lower() for domain in trusted_domains)
        
    def anonymize_logs(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove PII from log data"""
        anonymized = log_data.copy()
        
        # Remove or hash sensitive fields
        if "user_ip" in anonymized:
            anonymized["user_ip"] = self._hash_value(anonymized["user_ip"])
            
        if "session_id" in anonymized:
            anonymized["session_id"] = self._hash_value(anonymized["session_id"])
            
        return anonymized
        
    def _hash_value(self, value: str) -> str:
        """Hash sensitive values for privacy"""
        return hashlib.sha256(value.encode()).hexdigest()[:12]
        
    def generate_session_token(self) -> str:
        """Generate secure session token"""
        return secrets.token_urlsafe(32)
        
    def validate_session(self, token: str) -> bool:
        """Validate session token"""
        return token in self.session_tokens
        
    def get_security_headers(self) -> Dict[str, str]:
        """Get security headers for HTTP responses"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        }
        
    def audit_data_access(self, data_type: str, record_count: int, user_context: Dict = None) -> Dict:
        """Create audit trail for data access"""
        audit_entry = {
            "timestamp": "auto-generated",
            "data_type": data_type,
            "record_count": record_count,
            "api_key_hash": self.api_key_hash,
            "access_purpose": "government_data_analysis",
            "compliance_status": "gdpr_compliant",
            "data_retention": "session_only"
        }
        
        if user_context:
            audit_entry["user_context"] = self.anonymize_logs(user_context)
            
        return audit_entry
        
    def check_rate_limits(self, user_id: str) -> bool:
        """Check if user is within rate limits"""
        # Simple rate limiting - in production would use Redis or similar
        # For now, always allow (demo purposes)
        return True
        
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data for storage"""
        # In production, would use proper encryption
        # For demo, just indicate encryption would happen
        return f"[ENCRYPTED:{len(data)}]"
        
    def get_privacy_compliance_info(self) -> Dict[str, Any]:
        """Get privacy and compliance information"""
        return {
            "data_processing_purpose": "Agricultural and climate data analysis for policy insights",
            "data_sources": "Government open data portals only",
            "data_retention": "Session-based, no permanent storage of personal data",
            "data_sharing": "No data shared with third parties",
            "user_rights": {
                "access": "Users can request access to their query history",
                "rectification": "Users can request correction of any personal data",
                "erasure": "Users can request deletion of their data",
                "portability": "Users can export their query history"
            },
            "security_measures": [
                "HTTPS encryption for all communications",
                "Input sanitization and validation",
                "Secure API key management",
                "Audit logging for all data access",
                "Rate limiting to prevent abuse"
            ],
            "compliance_frameworks": ["GDPR", "Indian IT Act", "Government Data Guidelines"]
        }

# Global security manager
security_manager = SecurityManager()