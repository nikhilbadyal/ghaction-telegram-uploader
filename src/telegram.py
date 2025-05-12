"""Telegram Bridge."""

from pathlib import Path
from typing import Any, Self

from loguru import logger
from pyrogram import Client

from src.config import UploaderConfig
from src.downloader.download import Downloader
from src.strings import initializing_connection, project_name, uploading


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
        logger.debug(initializing_connection)
        app = Client(
            project_name,
            bot_token=config.bot_token,
            api_id=config.api_id,
            api_hash=config.api_hash,
        )
        self = cls(app, downloader, config)
        await self.app.start()
        return self

    async def progress(self: Self, current: Any, total: Any) -> None:
        """Report upload progress."""
        logger.debug(f"{current * 100 / total:.1f}%")

    async def __upload_to_tg(self: Self, folder: str) -> None:
        path = Path(folder)
        if path.is_dir():
            for child in sorted(path.iterdir()):
                await self.__upload_to_tg(str(child))
        elif str(path) in self.downloader.downloaded_files:
            logger.debug(uploading.format(path.name))
            await self.app.send_document(
                chat_id=self.config.chat_id,
                document=str(path),
                disable_notification=True,
                caption=f"`{path.name}`",
                progress=self.progress,
            )

    async def upload_latest(self: Self, folder: Any) -> None:
        """Upload the latest assets to telegram.

        :param folder: Folder where assets are stored
        """
        await self.__send_sticker()
        await self.__send_message()
        await self.__upload_to_tg(folder)

    async def __send_sticker(self: Self) -> None:
        if self.config.sticker_id:
            await self.app.send_sticker(
                chat_id=self.config.chat_id, sticker=self.config.sticker_id, disable_notification=True
            )

    async def __send_message(self: Self) -> None:
        if self.config.message:
            message = self.config.message
        else:
            message = f"""
            New Release(s)🥳
See Changelog [here]({self.downloader.changes})
            """
        await self.app.send_message(chat_id=self.config.chat_id, text=message)
