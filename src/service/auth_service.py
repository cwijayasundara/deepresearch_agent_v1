"""Authentication service — password auth and JWT tokens."""

import logging
from datetime import datetime, timedelta, timezone

import jwt

from src.types.errors import AuthError
from src.types.requests import AuthToken

logger = logging.getLogger(__name__)


class AuthService:
    """Handles password authentication and JWT token management."""

    def __init__(
        self,
        shared_password: str,
        jwt_secret: str,
        jwt_algorithm: str,
        jwt_expire_hours: int,
    ) -> None:
        self._shared_password = shared_password
        self._jwt_secret = jwt_secret
        self._jwt_algorithm = jwt_algorithm
        self._jwt_expire_hours = jwt_expire_hours

    def authenticate(self, password: str) -> AuthToken:
        """Authenticate with shared password, return JWT."""
        if password != self._shared_password:
            logger.warning("Failed authentication attempt")
            raise AuthError("Invalid password")

        now = datetime.now(timezone.utc)
        payload = {
            "sub": "user",
            "iat": now,
            "exp": now + timedelta(hours=self._jwt_expire_hours),
        }
        token = jwt.encode(
            payload, self._jwt_secret, algorithm=self._jwt_algorithm
        )
        return AuthToken(access_token=token, token_type="bearer")

    def verify_token(self, token: str) -> dict[str, str]:
        """Verify and decode a JWT token."""
        try:
            return jwt.decode(
                token, self._jwt_secret, algorithms=[self._jwt_algorithm]
            )
        except jwt.PyJWTError as exc:
            raise AuthError("Invalid token") from exc
