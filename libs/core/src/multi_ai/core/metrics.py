from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
import time
from functools import wraps

# Safe Metric Creation
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

# Metrics Definitions
AGENT_REQUESTS = get_or_create_counter('agent_requests_total', 'Total agent requests', ['agent_id', 'status'])
AGENT_DURATION = get_or_create_histogram('agent_duration_seconds', 'Agent execution time', ['agent_id'])
BUDGET_USAGE = get_or_create_counter('budget_usage_usd', 'Total budget usage in USD', ['agent_id', 'model'])
SECURITY_EVENTS = get_or_create_counter('security_events_total', 'Security violations', ['severity', 'rule'])

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

def get_metrics():
    return generate_latest(REGISTRY)