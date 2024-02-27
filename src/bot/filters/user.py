from aiogram.types import Message
from aiogram.filters import BaseFilter

from database.models import User


class AdminFilter(BaseFilter):
    async def __call__(self, message: Message, db_user: User):
        if db_user and db_user.is_admin:
            return True
