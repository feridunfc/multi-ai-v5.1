from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
from typing import Optional
from pathlib import Path

class KMSSettings(BaseSettings):
    model_config = ConfigDict(extra='ignore')
    provider: str = Field(default='local')
    endpoint: Optional[str] = None
    token: Optional[str] = None
    mount_path: str = Field(default='secret')

class DatabaseSettings(BaseSettings):
    model_config = ConfigDict(extra='ignore')
    url: str = 'postgresql://temporal:temporal@localhost:5432/temporal'
    pool_size: int = 20
    echo: bool = False

class RedisSettings(BaseSettings):
    model_config = ConfigDict(extra='ignore')
    url: str = 'redis://localhost:6379'
    stream_key: str = 'multi_ai:events'
    consumer_group: str = 'multi_ai_workers'
    consumer_name: str = 'worker_01'

class TemporalSettings(BaseSettings):
    model_config = ConfigDict(extra='ignore')
    namespace: str = 'default'
    address: str = 'localhost:7233'
    task_queue: str = 'multi-ai-tasks'

class ObservabilitySettings(BaseSettings):
    model_config = ConfigDict(extra='ignore')
    enabled: bool = True
    endpoint: Optional[str] = None
    service_name: str = 'multi-ai-platform'
    service_version: str = '5.1.0'
    log_level: str = 'INFO'

# --- DÜZELTİLEN KISIM: OLLAMA AYARLARI ---
class OllamaSettings(BaseSettings):
    model_config = ConfigDict(extra='ignore')
    # Windows için 127.0.0.1 zorunlu, /v1 kaldırıldı
    base_url: str = 'http://127.0.0.1:11434'
    default_model: str = 'llama3.2:1b'
    coder_model: str = 'deepseek-coder:6.7b'
    temperature: float = 0.2

class PlatformSettings(BaseSettings):
    model_config = ConfigDict(env_prefix='MULTI_AI_', case_sensitive=False, extra='ignore')

    environment: str = 'development'
    debug: bool = True
    log_format: str = 'json'

    kms: KMSSettings = Field(default_factory=KMSSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    temporal: TemporalSettings = Field(default_factory=TemporalSettings)
    observability: ObservabilitySettings = Field(default_factory=ObservabilitySettings)

    # ARTIK 'llm' YERİNE 'ollama' KULLANILIYOR
    ollama: OllamaSettings = Field(default_factory=OllamaSettings)

    github_app_id: Optional[str] = None
    github_private_key: Optional[str] = None
    github_webhook_secret: Optional[str] = "dummy_secret"

    base_dir: Path = Path.cwd()
    cache_dir: Path = Path.cwd() / '.cache'

settings = PlatformSettings()
