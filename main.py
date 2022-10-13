"""
Entrypoint file
"""
import asyncio

from src.downloader import Downloader, temp_folder
from src.telegram import Telegram


async def main() -> None:
    """
    Entrypoint
    """
    downloader = await Downloader.initialize()
    downloaded_files = downloader.download_latest()
    telegram = await Telegram.initialize(downloaded_files)
    await telegram.upload_latest(temp_folder)


asyncio.run(main())
