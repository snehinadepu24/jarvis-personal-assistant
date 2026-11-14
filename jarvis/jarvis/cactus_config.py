"""
Cactus AI Configuration and Integration
Central configuration for all Cactus components
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

try:
    import cactus
    CACTUS_AVAILABLE = True
    CACTUS_VERSION = getattr(cactus, '__version__', 'unknown')
except ImportError:
    CACTUS_AVAILABLE = False
    CACTUS_VERSION = None


@dataclass
class CactusConfig:
    """Configuration for Cactus AI integration"""
    
    # Global settings
    enabled: bool = True  # Master switch for all Cactus features
    fallback_to_cloud: bool = True  # Fallback to cloud APIs if Cactus fails
    
    # Privacy Classifier
    privacy_use_cactus: bool = True  # Use Needle for deep privacy analysis
    privacy_deep_analysis: bool = False  # Always use deep analysis (slower)
    
    # Speech-to-Text
    stt_use_cactus: bool = True  # Use Whistle for STT
    stt_sample_rate: int = 16000  # Audio sample rate
    
    # Planning
    planner_use_cactus: bool = False  # Use Gemini for planning
    planner_hybrid_mode: bool = True  # Use Needle for simple, Gemini for complex
    planner_complexity_threshold: str = "medium"  # Route to Needle if <= threshold
    
    # Vision
    vision_use_cactus: bool = True  # Use Mirage for vision
    vision_fallback_route: int = 3  # Fallback to OCR if Mirage fails
    
    # Performance
    model_cache_dir: Optional[str] = None  # Custom model cache location
    max_concurrent_requests: int = 1  # Limit concurrent Cactus operations
    
    # Telemetry
    telemetry_enabled: bool = False  # Cactus usage telemetry


# Global configuration instance
_config = None


def get_config() -> CactusConfig:
    """Get global Cactus configuration"""
    global _config
    if _config is None:
        _config = CactusConfig()
    return _config


def set_config(config: CactusConfig):
    """Set global Cactus configuration"""
    global _config
    _config = config


def is_available() -> bool:
    """Check if Cactus is available"""
    return CACTUS_AVAILABLE


def get_version() -> Optional[str]:
    """Get Cactus version"""
    return CACTUS_VERSION


def get_status() -> dict:
    """Get Cactus integration status"""
    cfg = get_config()
    
    status = {
        "available": CACTUS_AVAILABLE,
        "version": CACTUS_VERSION,
        "enabled": cfg.enabled if CACTUS_AVAILABLE else False,
        "components": {}
    }
    
    if CACTUS_AVAILABLE and cfg.enabled:
        status["components"] = {
            "privacy_classifier": cfg.privacy_use_cactus,
            "speech_to_text": cfg.stt_use_cactus,
            "planner": cfg.planner_use_cactus,
            "vision": cfg.vision_use_cactus,
        }
        
        status["features"] = {
            "local_inference": True,
            "zero_api_cost": True,
            "complete_privacy": True,
            "offline_capable": True,
        }
    
    return status


def disable_telemetry():
    """Disable Cactus telemetry"""
    import os
    os.environ["CACTUS_TELEMETRY"] = "0"
    cfg = get_config()
    cfg.telemetry_enabled = False


def print_status():
    """Print Cactus integration status"""
    status = get_status()
    
    print("=" * 60)
    print("Cactus AI Integration Status")
    print("=" * 60)
    
    if not status["available"]:
        print("X Cactus NOT installed")
        print("   Install: pip install -U cactus-compute")
        return
    
    print(f"OK Cactus {status['version']} installed")
    
    if not status["enabled"]:
        print("!  Cactus integration DISABLED")
        return
    
    print("\nActive Components:")
    for comp, enabled in status["components"].items():
        icon = "OK" if enabled else "  "
        print(f"{icon} {comp.replace('_', ' ').title()}")
    
    print("\nFeatures:")
    for feat, enabled in status["features"].items():
        print(f"OK {feat.replace('_', ' ').title()}")
    
    print("\nBenefits:")
    print("  $ Zero API costs after model download")
    print("  # Complete privacy (100% local)")
    print("  * No network latency")
    print("  @ Works fully offline")
    
    print("=" * 60)


# Initialize on import
if CACTUS_AVAILABLE:
    # Disable telemetry by default
    disable_telemetry()
