import os
import sys

from loguru import logger
from pyrogram import Client

default_sticker = (
    "CAACAgUAAxkBAAEYpFpjOplSFK_q93KWoJKqWHGfgPMxMwACuAYAApqD2VV9UCzjLNawRCoE"
)


class Telegram:
    def __init__(self, chat_id, app, sticker_id, downloaded_files):
        self.chat_id = chat_id
        self.app = app
        self.sticker_id = sticker_id
        self.downloaded_files = downloaded_files

    @classmethod
    async def initialize(cls, downloaded_files):
        logger.debug("Initializing Telegram connection...")
        try:
            api_id = os.getenv("INPUT_API_ID")
            api_hash = os.getenv(
                "INPUT_API_HASH",
            )
            bot_token = os.getenv(
                "INPUT_BOT_TOKEN",
            )
            str_chat_id = os.getenv("INPUT_CHAT_ID", "")
            if not str_chat_id:
                raise TypeError("Missing Chat ID")
            chat_id = int(str_chat_id)

            app = Client(
                "ghaction-telegram",
                bot_token=bot_token,
                api_id=api_id,
                api_hash=api_hash,
            )
            sticker_id = os.getenv("INPUT_STICKER_ID", default_sticker)
            if not sticker_id or len(sticker_id) == 0:
                sticker_id = default_sticker
            self = cls(chat_id, app, sticker_id, downloaded_files)
            await self.app.start()
            await self.app.get_chat(self.chat_id)
            return self
        except TypeError as e:
            logger.error(f"Please provide all required inputs {e}")
            sys.exit(-1)

    async def __upload_to_tg(self, folder: str) -> None:
        if os.path.isdir(folder):
            directory_contents = os.listdir(folder)
            logger.debug(f"Found {directory_contents}")
            directory_contents.sort()
            for single_file in directory_contents:
                await self.__upload_to_tg(os.path.join(folder, single_file))
        else:
            if folder in self.downloaded_files:
                logger.debug(f"Uploading {folder}")
                await self.app.send_document(chat_id=self.chat_id, document=folder)
            else:
                logger.debug(f"Skipped {folder}")

    async def upload_latest(self, folder: str) -> None:
        await self.__send_sticker()
        await self.__send_message()
        await self.__upload_to_tg(folder)

    async def __send_sticker(self) -> None:
        await self.app.send_sticker(chat_id=self.chat_id, sticker=self.sticker_id)

    async def __send_message(self) -> None:
        await self.app.send_message(chat_id=self.chat_id, text="New Release(s)🥳")
