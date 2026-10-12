from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication & Identity"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user",
    description="Validates Supabase Bearer JWT and returns the synchronized user profile.",
)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
