import hashlib
import hmac
import logging
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization

logger = logging.getLogger(__name__)


class SecurityValidator:
    """Güvenlik doğrulama sınıfı"""

    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key or Fernet.generate_key().decode()
        self.cipher_suite = Fernet(self.secret_key.encode())

    def validate_github_webhook(self, payload: bytes, signature: str) -> bool:
        """GitHub webhook imzasını doğrula"""
        if not self.secret_key:
            logger.warning("Secret key not set, skipping validation")
            return True

        expected_signature = "sha256=" + hmac.new(
            self.secret_key.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    def encrypt_sensitive_data(self, data: str) -> str:
        """Hassas verileri şifrele"""
        encrypted = self.cipher_suite.encrypt(data.encode())
        return encrypted.decode()

    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Şifreli veriyi çöz"""
        decrypted = self.cipher_suite.decrypt(encrypted_data.encode())
        return decrypted.decode()

    def validate_manifest_hash(self, manifest_data: Dict[str, Any], expected_hash: str) -> bool:
        """Manifest hash'ini doğrula"""
        import json
        manifest_json = json.dumps(manifest_data, sort_keys=True)
        computed_hash = hashlib.sha256(manifest_json.encode()).hexdigest()
        return computed_hash == expected_hash


class KMSManager:
    """Key Management System Manager"""

    def __init__(self):
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()

    def get_public_key_pem(self) -> str:
        """Public key'i PEM formatında getir"""
        pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode()

    def sign_data(self, data: bytes) -> bytes:
        """Veriyi imzala"""
        signature = self.private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature


# Global instances
kms_manager = KMSManager()
security_validator = SecurityValidator()