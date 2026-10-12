import uuid
from datetime import datetime, timezone, timedelta
from typing import Any
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import jwt

# Generate persistent ECC (P-256) keypair for the test session
TEST_EC_PRIVATE_KEY = ec.generate_private_key(ec.SECP256R1())
TEST_EC_PUBLIC_KEY_PEM = TEST_EC_PRIVATE_KEY.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
).decode("utf-8")

# A secondary different EC key to test signature mismatch
WRONG_EC_PRIVATE_KEY = ec.generate_private_key(ec.SECP256R1())


def create_test_es256_jwt(
    user_id: uuid.UUID,
    email: str = "analyst@vigilx.com",
    private_key: Any = TEST_EC_PRIVATE_KEY,
    expires_in_seconds: int = 3600,
    audience: str = "authenticated",
    algorithm: str = "ES256",
    kid: str = "vigilx-test-key-1",
) -> str:
    """
    Generate an authentic ECC P-256 (ES256) signed token for unit testing.
    NOTE: For test harnesses only.
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "email": email,
        "aud": audience,
        "role": "authenticated",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=expires_in_seconds)).timestamp()),
        "user_metadata": {
            "full_name": "Test Analyst",
        },
    }
    headers = {"kid": kid, "alg": algorithm} if algorithm != "none" else {"alg": "none"}
    if algorithm == "none":
        return jwt.encode(payload, key="", algorithm="none")
    return jwt.encode(payload, private_key, algorithm=algorithm, headers=headers)
