# libs/core/src/multi_ai/core/__init__.py
from .settings import settings, PlatformSettings
from .security import KMSManager, SecurityValidator, kms_manager, security_validator
from .budget import budget_guard
from .audit import audit_logger
from .ledger import ledger
from .metrics import track_time, LLM_TOKENS

__all__ = [
    'settings', 'PlatformSettings',
    'KMSManager', 'SecurityValidator', 'kms_manager', 'security_validator',
    'budget_guard', 'audit_logger', 'ledger', 'track_time', 'LLM_TOKENS'
]

# Package initialization
def init_core():
    """Core modülünü başlat"""
    from . import settings
    from .security import KMSManager

    # Security system initialization
    kms_manager = KMSManager()

    # Audit system ready
    audit_logger.info("MultiAI Core initialized", version=__version__)

    return {
        "status": "initialized",
        "version": __version__,
        "components": {
            "security": "active",
            "budget": "active",
            "ledger": "active",
            "metrics": "active"
        }
    }


# Auto-initialize on import
_CORE_STATUS = init_core()