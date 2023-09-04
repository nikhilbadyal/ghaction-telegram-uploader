"""Env Configurations."""
from pathlib import Path
from typing import Self

from environs import Env
from requests import Session

from src.constant import GITHUB_API_LATEST_RELEASE_URL, default_sticker

session = Session()


class UploaderConfig(object):
    """Revanced Configurations."""

    def __init__(self: Self, env: Env) -> None:
        self.env = env
        self.assets_pattern = env.str("INPUT_ASSETS_PATTERN", ".*")
        self.send_message = bool(env.str("INPUT_SEND_MESSAGE", True))
        self.send_sticker = bool(env.str("INPUT_SEND_STICKER", False))
        self.message = env.str("INPUT_MESSAGE", None)
        self.sticker_id = env.str("INPUT_STICKER_ID", default_sticker)
        self.chat_id = env.int("INPUT_CHAT_ID")
        self.api_id = env.str("INPUT_API_ID")
        self.api_hash = env.str("INPUT_API_HASH")
        self.bot_token = env.str("INPUT_BOT_TOKEN")
        self.GITHUB_REPOSITORY = env.str("INPUT_DOWNLOAD_GITHUB_REPOSITORY") or env.str("GITHUB_REPOSITORY")
        self.CHANGELOG_GITHUB_REPOSITORY = env.str("INPUT_CHANGELOG_GITHUB_REPOSITORY") or self.GITHUB_REPOSITORY
        self.repo_url = GITHUB_API_LATEST_RELEASE_URL.format(self.GITHUB_REPOSITORY)
        self.changelog_url = GITHUB_API_LATEST_RELEASE_URL.format(self.CHANGELOG_GITHUB_REPOSITORY)
        self.personal_access_token = env.str("INPUT_PERSONAL_ACCESS_TOKEN", None)
        self.temp_folder_name = "apks"
        self.temp_folder = Path(self.temp_folder_name)

    def __str__(self: Self) -> str:
        """Returns the str representation of the app."""
        attrs = vars(self)
        return ", ".join([f"{key}: {value}" for key, value in attrs.items()])
