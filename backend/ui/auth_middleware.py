"""Authentication middleware for protected routes."""

from fastapi import HTTPException

from backend.service.auth_service import AuthService
from backend.types.errors import AuthError


def require_auth(
    authorization: str | None, auth_service: AuthService
) -> dict[str, str]:
    """Validate Bearer token and return decoded payload."""
    if authorization is None:
        raise HTTPException(status_code=401, detail="Missing authorization")

    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0] != "Bearer":
        raise HTTPException(status_code=401, detail="Invalid auth scheme")

    try:
        return auth_service.verify_token(parts[1])
    except AuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
