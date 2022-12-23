"""Telegram Bridge."""
import os
import sys
from typing import Any

from loguru import logger
from pyrogram import Client

from src.config import UploaderConfig
from src.downloader import Downloader

default_sticker = (
    "CAACAgUAAxkBAAEYpFpjOplSFK_q93KWoJKqWHGfgPMxMwACuAYAApqD2VV9UCzjLNawRCoE"
)


class Telegram:
    """Class to manage Telegram."""

    # noinspection IncorrectFormatting
    def __init__(
        self,
        chat_id: int,
        app: Client,
        sticker_id: str,
        downloader: Downloader,
        config: UploaderConfig,
    ):
        self.chat_id = chat_id
        self.app = app
        self.sticker_id = sticker_id
        self.downloader = downloader
        self.config = config

    # noinspection IncorrectFormatting
    @classmethod
    async def initialize(
        cls, downloader: Downloader, config: UploaderConfig
    ) -> "Telegram":
        """Initialize Telegram Connection.

        Args:
            config: Environment variables
            downloader: Downloader
        :return:
        """
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
            self = cls(chat_id, app, sticker_id, downloader, config)
            await self.app.start()
            chat_info = await self.app.get_chat(self.chat_id)
            self.chat_id = chat_info.id
            return self
        except TypeError as e:
            logger.error(f"Please provide all required inputs {e}")
            sys.exit(-1)

    async def progress(self, current: Any, total: Any) -> None:
        """Report upload progress."""
        logger.debug(f"{current * 100 / total:.1f}%")

    async def __upload_to_tg(self, folder: str) -> None:
        if os.path.isdir(folder):
            directory_contents = os.listdir(folder)
            logger.debug(f"Found {directory_contents}")
            directory_contents.sort()
            for single_file in directory_contents:
                await self.__upload_to_tg(os.path.join(folder, single_file))
        else:
            if folder in self.downloader.downloaded_files:
                logger.debug(f"Uploading {folder}")
                await self.app.send_document(
                    chat_id=self.chat_id,
                    document=folder,
                    disable_notification=True,
                    caption=folder,
                    progress=self.progress,
                )
            else:
                logger.debug(f"Skipped {folder}")

    async def upload_latest(self, folder: Any) -> None:
        """Uploaded the latest assets to telegram.

        :param folder: Folder where assets are stored
        """
        await self.__send_sticker()
        await self.__send_message()
        await self.__upload_to_tg(folder)

    async def __send_sticker(self) -> None:
        if self.config.send_sticker:
            await self.app.send_sticker(
                chat_id=self.chat_id, sticker=self.sticker_id, disable_notification=True
            )

    async def __send_message(self) -> None:
        if self.config.send_message:
            if self.config.message and self.config.message != "":
                message = self.config.message
            else:
                message = f"""
                New Release(s)🥳
See Changelog [here]({self.downloader.changes})
                """
            await self.app.send_message(chat_id=self.chat_id, text=message)
