from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.services.user import UserService
from src.services.auth import AuthService
from src.models.base import User
from src.schemas.user import UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.patch("/avatar", response_model=UserResponse)
async def update_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
) -> User:
    user_service = UserService(db)
    return await user_service.update_avatar(current_user, file)
