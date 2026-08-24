from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from app.core.firebase import firebase_auth


async def get_current_user(authorization: Annotated[str | None, Header()] = None) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Firebase ID token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    try:
        decoded = firebase_auth().verify_id_token(token, check_revoked=True)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid or revoked Firebase ID token") from exc

    return decoded


async def get_current_admin(user: Annotated[dict, Depends(get_current_user)]) -> dict:
    if not user.get("admin", False):
        raise HTTPException(status_code=403, detail="Admin role required")
    return user
