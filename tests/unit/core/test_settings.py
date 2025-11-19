from multi_ai.core.settings import PlatformSettings

def test_settings_defaults():
    s = PlatformSettings()
    assert s.environment == "development"
    assert s.redis.stream_key == "multi_ai:events"
