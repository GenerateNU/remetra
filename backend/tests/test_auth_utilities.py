"""Unit tests for authentication utility functions."""

from datetime import timedelta

from services.auth_service import create_access_token, decode_access_token, get_password_hash, verify_password


class TestPasswordUtilities:
    """Test password hashing and verification utilities."""

    def test_password_hash_and_verify(self):
        """Test password can be hashed and verified."""
        password = "mysecretpassword"
        hashed = get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 0
        assert verify_password(password, hashed)
        assert not verify_password("wrongpassword", hashed)

    def test_different_passwords_different_hashes(self):
        """Test that same password generates different hashes (due to salt)."""
        password = "password123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)


class TestJWTUtilities:
    """Test JWT token creation and decoding."""

    def test_create_and_decode_token(self):
        """Test JWT token can be created and decoded."""
        data = {"sub": "testuser"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "testuser"
        assert "exp" in payload

    def test_decode_invalid_token(self):
        """Test decoding invalid token returns None."""
        invalid_token = "this.is.invalid"
        payload = decode_access_token(invalid_token)
        assert payload is None

    def test_create_token_with_custom_expiry(self):
        """Test creating token with custom expiration."""
        data = {"sub": "testuser"}
        expires = timedelta(minutes=30)
        token = create_access_token(data, expires_delta=expires)

        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "testuser"
