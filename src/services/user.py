from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.user_repository import UserRepository
from src.services.cloud_image import CloudImage
from src.models.base import User


class UserService:
    def __init__(self, db: AsyncSession):
        self.repository = UserRepository(db)

    async def update_avatar(self, user: User, file: UploadFile) -> User:
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="File must be an image"
            )

        public_id = f"ContactsApp/{user.id}"

        content = await file.read()

        result = await CloudImage.upload(content, public_id=public_id)

        return await self.repository.update_avatar(user, result["secure_url"])
