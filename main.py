"""Entrypoint file."""

import asyncio

from environs import Env

from src.config import UploaderConfig
from src.constant import temp_folder
from src.downloader.download import Downloader
from src.telegram import Telegram


async def main() -> None:
    """Entrypoint."""
    env = Env()
    config = UploaderConfig(env)
    downloader = await Downloader.initialize(config)
    await downloader.download_latest(config)
    telegram = await Telegram.initialize(downloader, config)
    await telegram.upload_latest(temp_folder)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
