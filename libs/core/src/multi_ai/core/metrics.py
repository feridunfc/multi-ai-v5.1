from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
import time
import functools

LLM_TOKENS = Counter('multiai_llm_tokens_total', 'Total tokens', ['model', 'provider'])
AGENT_DURATION = Histogram('multiai_agent_duration_seconds', 'Agent time', ['agent_type'])

def track_time(agent_name: str):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.time()
            try:
                return await func(*args, **kwargs)
            finally:
                AGENT_DURATION.labels(agent_type=agent_name).observe(time.time() - start)
        return wrapper
    return decorator
