"""Telegram Bridge."""
import os
import sys
from pathlib import Path
from typing import Any, Self

from loguru import logger
from pyrogram import Client

from src.config import UploaderConfig
from src.downloader import Downloader


class Telegram(object):
    """Class to manage Telegram."""

    # noinspection IncorrectFormatting
    def __init__(
        self: Self,
        app: Client,
        downloader: Downloader,
        config: UploaderConfig,
    ) -> None:
        self.app = app
        self.downloader = downloader
        self.config = config

    # noinspection IncorrectFormatting
    @classmethod
    async def initialize(cls, downloader: Downloader, config: UploaderConfig) -> Self:
        """Initialize Telegram Connection.

        Args:
            config: Environment variables
            downloader: Downloader
        :return:
        """
        logger.debug("Initializing Telegram connection...")
        try:
            app = Client(
                "ghaction-telegram",
                bot_token=config.bot_token,
                api_id=config.api_id,
                api_hash=config.api_hash,
            )
            self = cls(app, downloader, config)
            await self.app.start()
        except TypeError as e:
            logger.error(f"Please provide all required inputs {e}")
            sys.exit(-1)
        else:
            return self

    async def progress(self: Self, current: Any, total: Any) -> None:
        """Report upload progress."""
        logger.debug(f"{current * 100 / total:.1f}%")

    async def __upload_to_tg(self: Self, folder: str) -> None:
        if Path(folder).is_dir():
            directory_contents = os.listdir(folder)
            logger.debug(f"Found {directory_contents}")
            directory_contents.sort()
            for single_file in directory_contents:
                await self.__upload_to_tg(os.path.join(folder, single_file))
        elif folder in self.downloader.downloaded_files:
            logger.debug(f"Uploading {folder}")
            await self.app.send_document(
                chat_id=self.config.chat_id,
                document=folder,
                disable_notification=True,
                caption=f"`{Path(folder).name}`",
                progress=self.progress,
            )
        else:
            logger.debug(f"Skipped {folder}")

    async def upload_latest(self: Self, folder: Any) -> None:
        """Upload the latest assets to telegram.

        :param folder: Folder where assets are stored
        """
        await self.__send_sticker()
        await self.__send_message()
        await self.__upload_to_tg(folder)

    async def __send_sticker(self: Self) -> None:
        if self.config.send_sticker:
            await self.app.send_sticker(
                chat_id=self.config.chat_id, sticker=self.config.sticker_id, disable_notification=True
            )

    async def __send_message(self: Self) -> None:
        if self.config.send_message:
            if self.config.message and self.config.message != "":
                message = self.config.message
            else:
                message = f"""
                New Release(s)🥳
See Changelog [here]({self.downloader.changes})
                """
            await self.app.send_message(chat_id=self.config.chat_id, text=message)
