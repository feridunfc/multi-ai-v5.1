# libs/core/src/multi_ai/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
import time
from functools import wraps
from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)

# Safe Metric Creation - Mevcut kodunuz
def get_or_create_counter(name, doc, labels):
    try:
        return Counter(name, doc, labels)
    except ValueError:
        return REGISTRY._names_to_collectors[name]

def get_or_create_histogram(name, doc, labels):
    try:
        return Histogram(name, doc, labels)
    except ValueError:
        return REGISTRY._names_to_collectors[name]

# Metrics Definitions - Mevcut metriklerinize eklemeler
AGENT_REQUESTS = get_or_create_counter('agent_requests_total', 'Total agent requests', ['agent_id', 'status'])
AGENT_DURATION = get_or_create_histogram('agent_duration_seconds', 'Agent execution time', ['agent_id'])
BUDGET_USAGE = get_or_create_counter('budget_usage_usd', 'Total budget usage in USD', ['agent_id', 'model'])
SECURITY_EVENTS = get_or_create_counter('security_events_total', 'Security violations', ['severity', 'rule'])

# EKSİK OLAN METRİKLERİ EKLEYELİM
LLM_TOKENS = get_or_create_counter('llm_tokens_total', 'Total LLM tokens processed', ['model', 'provider'])

def track_agent_metrics(agent_id: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                AGENT_REQUESTS.labels(agent_id=agent_id, status='success').inc()
                return result
            except Exception as e:
                AGENT_REQUESTS.labels(agent_id=agent_id, status='error').inc()
                raise e
            finally:
                duration = time.time() - start
                AGENT_DURATION.labels(agent_id=agent_id).observe(duration)
        return wrapper
    return decorator

# EKSİK OLAN track_time FONKSİYONUNU EKLEYELİM
def track_time(agent_name: str):
    """track_agent_metrics ile uyumlu track_time implementasyonu"""
    return track_agent_metrics(agent_name)

def record_llm_usage(model: str, provider: str, tokens: int):
    """LLM token kullanımını kaydet"""
    LLM_TOKENS.labels(model=model, provider=provider).inc(tokens)

def get_metrics():
    return generate_latest(REGISTRY)

# __all__ ekleyelim
__all__ = [
    'track_agent_metrics', 
    'track_time', 
    'LLM_TOKENS',
    'AGENT_REQUESTS', 
    'AGENT_DURATION', 
    'BUDGET_USAGE',
    'SECURITY_EVENTS',
    'record_llm_usage',
    'get_metrics'
]