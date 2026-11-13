"""
Privacy Classifier - Phase 9 Implementation with Cactus AI
Hybrid approach: Pattern matching + Cactus Needle for contextual analysis
"""
from __future__ import annotations

import re
from typing import Dict, List, Optional
from dataclasses import dataclass

# Optional Cactus integration
try:
    import cactus
    CACTUS_AVAILABLE = True
except ImportError:
    CACTUS_AVAILABLE = False
    cactus = None

@dataclass
class PrivacyClassification:
    """Result of privacy classification"""
    has_sensitive: bool
    redacted_text: str
    sensitive_items: List[Dict[str, str]]
    risk_level: str  # low, medium, high, critical
    used_ai: bool = False  # Whether Cactus AI was used


class PrivacyClassifier:
    """
    Detects sensitive information using hybrid approach:
    1. Pattern matching (fast, deterministic)
    2. Cactus Needle AI (optional, contextual understanding)
    
    Categories detected:
    - API keys and tokens
    - Email addresses
    - Phone numbers
    - Credit card numbers
    - Social Security Numbers
    - IP addresses
    - Passwords
    - Contextual PII (via Cactus)
    """
    
    # Pattern definitions
    PATTERNS = {
        'api_key': [
            r'[A-Za-z0-9_-]{32,}',  # Generic API key
            r'sk-[A-Za-z0-9]{48}',  # OpenAI style
            r'AIza[A-Za-z0-9_-]{35}',  # Google API
            r'ghp_[A-Za-z0-9]{36}',  # GitHub Personal Access Token
        ],
        'email': [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        ],
        'phone': [
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',  # US phone
            r'\(\d{3}\)\s*\d{3}[-.\s]?\d{4}',
        ],
        'credit_card': [
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
        ],
        'ssn': [
            r'\b\d{3}-\d{2}-\d{4}\b',
        ],
        'ip_address': [
            r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
        ],
        'password_field': [
            r'password["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            r'pwd["\']?\s*[:=]\s*["\']([^"\']+)["\']',
        ],
    }
    
    def __init__(self, redact_mode: str = "partial", use_cactus: bool = True):
        """
        Initialize privacy classifier.
        
        Args:
            redact_mode: "full" = replace entirely, "partial" = keep partial info
            use_cactus: Use Cactus Needle for deep analysis (requires cactus-compute)
        """
        self.redact_mode = redact_mode
        self.use_cactus = use_cactus and CACTUS_AVAILABLE
        self._compile_patterns()
        self._cactus_agent = None
        
        if self.use_cactus:
            self._init_cactus_agent()
    
    def _compile_patterns(self):
        """Compile regex patterns for efficiency"""
        self.compiled_patterns = {}
        for category, patterns in self.PATTERNS.items():
            self.compiled_patterns[category] = [
                re.compile(pattern, re.IGNORECASE)
                for pattern in patterns
            ]
    
    def _init_cactus_agent(self):
        """Initialize Cactus Needle agent for contextual analysis"""
        if not CACTUS_AVAILABLE:
            return
        
        try:
            @cactus.tool
            def analyze_privacy(text: str) -> dict:
                """
                Analyze text for privacy-sensitive content beyond pattern matching.
                Returns: {"has_pii": bool, "categories": list, "reason": str}
                """
                # Tool signature tells Needle what we expect
                pass
            
            self._cactus_agent = cactus.Cactus(tools=[analyze_privacy])
            print("[Privacy] Cactus Needle agent initialized")
        except Exception as e:
            print(f"[Privacy] Cactus initialization failed: {e}")
            self.use_cactus = False
    
    def _analyze_with_cactus(self, text: str) -> Optional[Dict]:
        """Use Cactus Needle for contextual privacy analysis"""
        if not self.use_cactus or not self._cactus_agent:
            return None
        
        try:
            prompt = f"""Analyze if this text contains privacy-sensitive information:
"{text}"

Consider:
- Personal identifiable information (names, addresses, DOB)
- Financial info (accounts, transactions)
- Health info (medical conditions, prescriptions)
- Auth data (passwords, security answers)
- Confidential business data

Return: {{"has_pii": bool, "categories": [str], "reason": str}}"""
            
            result = self._cactus_agent.run(prompt)
            
            # Parse result
            if result and "results" in result:
                return result["results"]
        except Exception as e:
            print(f"[Privacy] Cactus analysis error: {e}")
        
        return None
    
    def classify(self, text: str, deep_analysis: bool = False) -> PrivacyClassification:
        """
        Classify text for privacy sensitivity.
        
        Args:
            text: Text to analyze
            deep_analysis: Use Cactus for deeper contextual analysis (slower but accurate)
        
        Returns:
            PrivacyClassification with detected sensitive items
        """
        sensitive_items = []
        redacted_text = text
        
        # Pattern-based detection (fast)
        for category, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                matches = pattern.findall(text)
                if matches:
                    for match in matches:
                        match_str = match if isinstance(match, str) else match[0]
                        
                        # Record finding
                        sensitive_items.append({
                            "category": category,
                            "value": match_str[:10] + "..." if len(match_str) > 10 else match_str,
                            "confidence": 0.95,  # High confidence for patterns
                            "method": "pattern"
                        })
                        
                        # Redact
                        replacement = self._partial_redact(match_str, category)
                        redacted_text = redacted_text.replace(match_str, replacement)
        
        # Contextual analysis with Cactus (optional)
        cactus_result = None
        if deep_analysis and self.use_cactus:
            cactus_result = self._analyze_with_cactus(text)
            
            if cactus_result and isinstance(cactus_result, dict):
                has_pii = cactus_result.get("has_pii", False)
                categories = cactus_result.get("categories", [])
                reason = cactus_result.get("reason", "")
                
                if has_pii:
                    # Add Cactus findings
                    for cat in categories:
                        sensitive_items.append({
                            "category": f"contextual_{cat}",
                            "value": "[detected by AI]",
                            "confidence": 0.75,  # Lower for AI
                            "method": "cactus",
                            "reason": reason
                        })
        
        # Calculate risk level
        risk_level = self._calculate_risk_level(sensitive_items)
        has_sensitive = len(sensitive_items) > 0
        
        return PrivacyClassification(
            has_sensitive=has_sensitive,
            redacted_text=redacted_text,
            sensitive_items=sensitive_items,
            risk_level=risk_level if has_sensitive else "low",
            used_ai=cactus_result is not None
        )
    
    def _partial_redact(self, value: str, category: str) -> str:
        """Partially redact a value (show first/last few chars)"""
        if len(value) <= 8:
            return "[REDACTED]"
        
        if category in ['api_key', 'password_field', 'credit_card', 'ssn']:
            # High sensitivity - show less
            return f"{value[:2]}...{value[-2:]}"
        elif category == 'email':
            # Keep domain visible
            if '@' in value:
                local, domain = value.split('@', 1)
                return f"{local[0]}***@{domain}"
            return value[:3] + "***"
        else:
            # Show more
            return f"{value[:4]}...{value[-4:]}"
    
    def _calculate_risk_level(self, items: List[Dict]) -> str:
        """Calculate overall risk level from detected items"""
        if not items:
            return "low"
        
        # Check for critical categories
        critical_cats = {'api_key', 'password_field', 'credit_card', 'ssn'}
        for item in items:
            cat = item['category'].replace('contextual_', '')
            if cat in critical_cats:
                return "critical"
        
        # Check for high-risk categories
        high_cats = {'email', 'phone'}  # Multiple PII types together
        high_count = sum(1 for item in items if item['category'].replace('contextual_', '') in high_cats)
        
        # Multiple items or any high-risk categories
        if len(items) >= 2 or high_count > 0:
            return "high"
        
        # Single medium-sensitivity category
        medium_cats = {'ip_address'}
        for item in items:
            cat = item['category'].replace('contextual_', '')
            if cat in medium_cats:
                return "medium"
        
        return "medium"  # Default for any detected item
    
    def should_route_locally(self, classification: PrivacyClassification) -> bool:
        """
        Determine if content should be processed locally vs cloud LLM.
        
        Args:
            classification: Privacy classification result
            
        Returns:
            True if should use local processing
        """
        if classification.risk_level in ['critical', 'high']:
            return True
        
        # Check for critical categories
        critical_categories = {'api_key', 'password_field', 'credit_card', 'ssn'}
        for item in classification.sensitive_items:
            cat = item['category'].replace('contextual_', '')
            if cat in critical_categories:
                return True
        
        return False


# Singleton instance
_classifier = None

def get_classifier(use_cactus: bool = True) -> PrivacyClassifier:
    """Get singleton privacy classifier instance"""
    global _classifier
    if _classifier is None:
        _classifier = PrivacyClassifier(redact_mode="partial", use_cactus=use_cactus)
    return _classifier


def classify_text(text: str, deep_analysis: bool = False) -> PrivacyClassification:
    """Convenience function to classify text"""
    return get_classifier().classify(text, deep_analysis=deep_analysis)
