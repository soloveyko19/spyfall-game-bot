from aiogram.filters import BaseFilter
from aiogram.types import Message


class ChatTypeFilter(BaseFilter):
    def __init__(self, *chat_types: str):
        super().__init__()
        self.chat_types = chat_types

    async def __call__(self, message: Message):
        if isinstance(self.chat_types, str):
            return message.chat.type == self.chat_types
        else:
            return message.chat.type in self.chat_types
