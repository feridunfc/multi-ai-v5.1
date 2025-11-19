import base64
import os
import asyncio
from typing import Optional, ClassVar, Dict
from contextlib import asynccontextmanager

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class KMSClient:
    async def get_secret(self, key: str) -> Optional[str]:
        raise NotImplementedError

    async def set_secret(self, key: str, value: str) -> bool:
        raise NotImplementedError

    async def health_check(self) -> bool:
        raise NotImplementedError


class LocalKMSClient(KMSClient):
    def __init__(self) -> None:
        self._secrets: Dict[str, str] = {}
        self._lock = asyncio.Lock()
        
        password = os.getenv("LOCAL_KMS_PASSWORD", "default-insecure-password").encode()
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100_000)
        key = base64.urlsafe_b64encode(kdf.derive(password))
        self._fernet = Fernet(key)

    async def get_secret(self, key: str) -> Optional[str]:
        async with self._lock:
            enc = self._secrets.get(key)
            if not enc:
                return None
            return self._fernet.decrypt(enc.encode()).decode()

    async def set_secret(self, key: str, value: str) -> bool:
        async with self._lock:
            enc = self._fernet.encrypt(value.encode()).decode()
            self._secrets[key] = enc
            return True

    async def health_check(self) -> bool:
        return True


class KMSManager:
    _instance: ClassVar[Optional["KMSManager"]] = None

    def __init__(self) -> None:
        self._client: KMSClient = LocalKMSClient()

    @classmethod
    async def get_instance(cls) -> "KMSManager":
        if cls._instance is None:
            cls._instance = KMSManager()
        return cls._instance

    async def get_secret(self, key: str) -> Optional[str]:
        env_key = f"MULTI_AI_{key.upper()}"
        env_val = os.getenv(env_key)
        if env_val:
            return env_val
        return await self._client.get_secret(key)

    async def set_secret(self, key: str, value: str) -> bool:
        return await self._client.set_secret(key, value)

    async def health_check(self) -> bool:
        return await self._client.health_check()

    @asynccontextmanager
    async def secret_context(self, key: str):
        secret = await self.get_secret(key)
        try:
            yield secret
        finally:
            if secret:
                del secret
