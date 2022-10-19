"""Entrypoint file."""
import asyncio

from environs import Env

from src.config import UploaderConfig
from src.downloader import Downloader, temp_folder
from src.telegram import Telegram


async def main() -> None:
    """Entrypoint."""
    env = Env()
    config = UploaderConfig(env)
    downloader = await Downloader.initialize()
    downloader.download_latest(config)
    telegram = await Telegram.initialize(downloader)
    await telegram.upload_latest(temp_folder)


asyncio.run(main())
