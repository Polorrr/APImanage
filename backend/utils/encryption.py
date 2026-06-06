"""Encryption utilities for API key storage."""
import os
import base64
import hashlib

from django.conf import settings

# Use Fernet (AES-128-CBC with HMAC) for simplicity
# Falls back to simple obfuscation if cryptography not installed
try:
    from cryptography.fernet import Fernet

    def _get_key():
        raw = getattr(settings, 'ENCRYPTION_KEY', None) or os.getenv('ENCRYPTION_KEY', 'aimanage-default-key-change-me')
        # Derive a valid Fernet key from any string
        key = hashlib.sha256(raw.encode()).digest()
        return base64.urlsafe_b64encode(key)

    def encrypt(plaintext: str) -> str:
        """Encrypt a string. Returns base64-encoded ciphertext."""
        if not plaintext:
            return ''
        f = Fernet(_get_key())
        return f.encrypt(plaintext.encode()).decode()

    def decrypt(ciphertext: str) -> str:
        """Decrypt a base64-encoded ciphertext. Returns plaintext."""
        if not ciphertext:
            return ''
        f = Fernet(_get_key())
        return f.decrypt(ciphertext.encode()).decode()

except ImportError:
    # Fallback: base64 obfuscation (not secure, but functional)
    def encrypt(plaintext: str) -> str:
        if not plaintext:
            return ''
        return base64.b64encode(plaintext.encode()).decode()

    def decrypt(ciphertext: str) -> str:
        if not ciphertext:
            return ''
        try:
            return base64.b64decode(ciphertext.encode()).decode()
        except Exception:
            return ciphertext  # Return as-is if not base64
