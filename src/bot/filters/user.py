from aiogram.types import Message
from aiogram.filters import BaseFilter

from database.models import User


class AdminFilter(BaseFilter):
    async def __call__(self, message: Message):
        user = await User.get(tg_id=message.from_user.id)
        if user and user.is_admin:
            return True
