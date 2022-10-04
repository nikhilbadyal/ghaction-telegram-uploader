import asyncio
import os

from downloader import Downloader, temp_folder
from telegram import Telegram

GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")
url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/releases/latest"


async def main() -> None:
    downloader = await Downloader.initialize(url)
    downloaded_files = downloader.download_latest()
    telegram = await Telegram.initialize(downloaded_files)
    await telegram.upload_latest(temp_folder)

asyncio.run(main())
