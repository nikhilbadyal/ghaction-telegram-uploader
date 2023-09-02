"""Env Configurations."""
from typing import Self

from environs import Env
from requests import Session

from src.constant import default_sticker

session = Session()


class UploaderConfig(object):
    """Revanced Configurations."""

    def __init__(self: Self, env: Env) -> None:
        self.env = env
        self.assets_pattern = env.str("INPUT_ASSETS_PATTERN", ".*")
        self.send_message = env.bool("INPUT_SEND_MESSAGE", True)
        self.send_sticker = env.bool("INPUT_SEND_STICKER", False)
        self.message = env.str("INPUT_MESSAGE", None)
        self.sticker_id = env.str("INPUT_STICKER_ID", default_sticker)
        self.chat_id = env.int("INPUT_CHAT_ID")
        self.api_id = env.str("INPUT_API_ID")
        self.api_hash = env.str("INPUT_API_HASH")
        self.bot_token = env.str("INPUT_BOT_TOKEN")
        self.GITHUB_REPOSITORY = env.str("INPUT_DOWNLOAD_GITHUB_REPOSITORY", env.str("GITHUB_REPOSITORY"))
        self.CHANGELOG_GITHUB_REPOSITORY = env.str("INPUT_CHANGELOG_GITHUB_REPOSITORY", self.GITHUB_REPOSITORY)
        self.repo_url = f"https://api.github.com/repos/{self.GITHUB_REPOSITORY}/releases/latest"
        self.changelog_url = f"https://api.github.com/repos/{self.CHANGELOG_GITHUB_REPOSITORY}/releases/latest"
