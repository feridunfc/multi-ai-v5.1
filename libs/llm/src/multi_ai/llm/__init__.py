# libs/llm/src/multi_ai/llm/__init__.py
from .hybrid_router import llm_router
from .parser import CodeParser

__all__ = ['llm_router', 'CodeParser']