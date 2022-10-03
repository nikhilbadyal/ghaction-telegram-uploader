import os
from concurrent.futures import ThreadPoolExecutor
from typing import Any, List, Tuple

import requests
from loguru import logger
from pyrogram import Client

from downloader import Downloader, temp_folder

API_ID = os.getenv("INPUT_API_ID")
API_HASH = os.getenv(
    "INPUT_API_HASH",
)
BOT_TOKEN = os.getenv(
    "INPUT_BOT_TOKEN",
)
CHAT_ID: int = int(os.getenv("INPUT_CHAT_ID"))
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")
default_sticker = (
    "CAACAgUAAxkBAAEYpFpjOplSFK_q93KWoJKqWHGfgPMxMwACuAYAApqD2VV9UCzjLNawRCoE"
)
sticker_id = os.getenv("INPUT_STICKER_ID", default_sticker)
app: Client
downloaded_files = []


def upload_to_tg(folder: str) -> None:
    global app
    if os.path.isdir(folder):
        directory_contents = os.listdir(folder)
        logger.debug(f"Found {directory_contents}")
        directory_contents.sort()
        for single_file in directory_contents:
            upload_to_tg(os.path.join(folder, single_file))
    else:
        if folder in downloaded_files:
            logger.debug(f"Uploading {folder}")
            app.send_document(chat_id=CHAT_ID, document=folder)
        else:
            logger.debug(f"Skipped {folder}")


def send_sticker() -> None:
    global app
    app.send_sticker(chat_id=CHAT_ID, sticker=sticker_id)


def send_message() -> None:
    global app
    app.send_message(chat_id=CHAT_ID, text="New Releas🥳")


def download_apk() -> None:
    downloader = Downloader
    url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/releases/latest"
    response = requests.get(url).json()
    assets_from_api = response["assets"]
    assets: List[Tuple[Any, Any]] = []
    for asset in assets_from_api:
        url = asset["browser_download_url"]
        app_name = asset["name"]
        downloaded_files.append(str(temp_folder) + "/" + app_name)
        assets.append((url, app_name))
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(lambda repo: downloader.download_assets(*repo), assets)
    logger.info(f"Downloaded all revanced apps {downloaded_files}")


def initialize_telegram() -> None:
    logger.debug("Initializing Telegram connection...")
    global app
    app = Client(
        "ghaction-telegram", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH
    )
    app.start()
    app.get_chat(CHAT_ID)


def main() -> None:
    global app
    download_apk()
    initialize_telegram()
    send_sticker()
    send_message()
    upload_to_tg(temp_folder)


main()
