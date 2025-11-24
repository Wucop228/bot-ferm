from datetime import timedelta

from jose import jwt

from app.core.config import get_settings
from app.core.security import get_password_hash, verify_password, create_jwt_token


def test_password_hash_and_verify() -> None:
    raw_password = "super-secret"
    hashed = get_password_hash(raw_password)

    assert hashed != raw_password
    assert verify_password(raw_password, hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_create_jwt_token_contains_expected_claims() -> None:
    settings = get_settings()

    token = create_jwt_token(
        data={"sub": "123", "ver": "v1"},
        expires_delta=timedelta(minutes=5),
        token_type="access",
    )

    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    assert decoded["sub"] == "123"
    assert decoded["ver"] == "v1"
    assert decoded["type"] == "access"
    assert "exp" in decoded
    assert "iat" in decoded