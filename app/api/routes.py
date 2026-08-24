from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_current_admin, get_current_user
from app.schemas.item import ItemCreate, ItemResponse
from app.schemas.user import UpdateProfileRequest, UserProfile
from app.services.items import create_item, list_items
from app.services.users import ensure_user_profile, list_users, revoke_refresh_tokens, update_user_profile

from .ruff_router import ruff_router
from .semgrep_router import semgrep_routner


router = APIRouter(prefix="/api/v1")



router.include_router(ruff_router, prefix="/ruff", tags=["ruff"])
router.include_router(semgrep_routner, prefix="/semgrep", tags=["semgrep"])


# USER ROUTES
@router.get("/me", response_model=UserProfile)
async def me(user: Annotated[dict, Depends(get_current_user)]):
    return ensure_user_profile(user)


@router.patch("/me", response_model=UserProfile)
async def update_me(
    payload: UpdateProfileRequest,
    user: Annotated[dict, Depends(get_current_user)],
):
    return update_user_profile(user["uid"], payload.model_dump(exclude_none=True))


@router.post("/me/revoke-sessions", status_code=204)
async def revoke_sessions(user: Annotated[dict, Depends(get_current_user)]):
    revoke_refresh_tokens(user["uid"])


@router.get("/admin/users")
async def admin_users(user: Annotated[dict, Depends(get_current_admin)]):
    return list_users()


@router.post("/items", response_model=ItemResponse)
async def add_item(
    payload: ItemCreate,
    user: Annotated[dict, Depends(get_current_user)],
):
    return create_item(user["uid"], payload.name, payload.description)


@router.get("/items", response_model=list[ItemResponse])
async def get_items(
    user: Annotated[dict, Depends(get_current_user)],
    limit: int = Query(default=100, ge=1, le=500),
):
    return list_items(user["uid"], limit)
