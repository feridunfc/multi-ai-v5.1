"""
MultiAI Utils Package
"""

__version__ = "1.0.0"
__author__ = "MultiAI Team"

# Package initialization
try:
    from .robust_ollama_client import RobustOllamaClient, ollama_client
except ImportError:
    # Fallback for missing modules
    class RobustOllamaClient:
        def __init__(self):
            pass


    ollama_client = RobustOllamaClient()

__all__ = ['RobustOllamaClient', 'ollama_client']