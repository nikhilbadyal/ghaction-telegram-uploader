import os
import sys

from loguru import logger
from pyrogram import Client

default_sticker = (
    "CAACAgUAAxkBAAEYpFpjOplSFK_q93KWoJKqWHGfgPMxMwACuAYAApqD2VV9UCzjLNawRCoE"
)


class Telegram:
    @classmethod
    async def initialize(cls, downloaded_files):
        self = cls()
        logger.debug("Initializing Telegram connection...")
        try:
            self.API_ID = os.getenv("INPUT_API_ID")
            self.API_HASH = os.getenv(
                "INPUT_API_HASH",
            )
            self.BOT_TOKEN = os.getenv(
                "INPUT_BOT_TOKEN",
            )
            self.CHAT_ID = int(os.getenv("INPUT_CHAT_ID"))
        except TypeError as e:
            logger.error(f"Please provide all required inputs {e}")
            sys.exit(-1)
        self.app = Client(
            "ghaction-telegram",
            bot_token=self.BOT_TOKEN,
            api_id=self.API_ID,
            api_hash=self.API_HASH,
        )
        self.downloaded_files = downloaded_files
        self.sticker_id = os.getenv("INPUT_STICKER_ID", default_sticker)
        await self.app.start()
        await self.app.get_chat(self.CHAT_ID)
        return self

    async def __upload_to_tg(self, folder: str) -> None:
        if os.path.isdir(folder):
            directory_contents = os.listdir(folder)
            logger.debug(f"Found {directory_contents}")
            directory_contents.sort()
            for single_file in directory_contents:
                self.upload_to_tg(os.path.join(folder, single_file))
        else:
            if folder in self.downloaded_files:
                logger.debug(f"Uploading {folder}")
                await self.app.send_document(chat_id=self.CHAT_ID, document=folder)
            else:
                logger.debug(f"Skipped {folder}")

    async def upload_latest(self, folder: str) -> None:
        await self.__send_sticker()
        await self.__send_message()
        await self.__upload_to_tg(folder)

    async def __send_sticker(self) -> None:
        await self.app.send_sticker(chat_id=self.CHAT_ID, sticker=self.sticker_id)

    async def __send_message(self) -> None:
        await self.app.send_message(chat_id=self.CHAT_ID, text="New Release🥳")
