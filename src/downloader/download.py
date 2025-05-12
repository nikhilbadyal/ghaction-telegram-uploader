"""Downloader."""

import asyncio
import re
from queue import PriorityQueue
from time import perf_counter
from typing import Any, Self

import aiohttp
from aiohttp import ClientSession
from loguru import logger
from tqdm import tqdm

from src.config import UploaderConfig
from src.constant import REQUEST_TIMEOUT, temp_folder
from src.exception import DownloadError, ReleaseNotFoundError
from src.strings import downloaded_all, fetching_assets, no_release_found, no_url, not_found, skipping_asset


class Downloader(object):
    """Downloader."""

    def __init__(self: Self, response: dict[Any, Any], changes: str, config: UploaderConfig) -> None:
        self._CHUNK_SIZE = 10485760
        self._QUEUE: PriorityQueue[tuple[float, str]] = PriorityQueue()
        self._QUEUE_LENGTH = 0
        self.response = response
        self.downloaded_files: list[str] = []
        self.changes = changes
        self.config = config

    async def _download(self: Self, url: str, file_name: str) -> None:
        if not url:
            raise DownloadError(no_url)
        logger.info(f"Trying to download {file_name} from {url}")
        self._QUEUE_LENGTH += 1
        start = perf_counter()
        headers = {}
        if self.config.personal_access_token and "github" in url:
            logger.debug("Using personal access token")
            headers["Authorization"] = f"token {self.config.personal_access_token}"
        async with aiohttp.ClientSession() as session:
            response = await Downloader.fetch(session, url)
            total = int(response.headers.get("content-length", 0))
            bar = tqdm(
                desc=file_name,
                total=total,
                unit="iB",
                unit_scale=True,
                unit_divisor=1024,
                colour="green",
            )
            if not temp_folder.exists():
                temp_folder.mkdir(parents=True)
            with self.config.temp_folder.joinpath(file_name).open("wb") as dl_file, bar:
                async for chunk in response.content.iter_any():
                    size = dl_file.write(chunk)
                    bar.update(size)
        self._QUEUE.put((perf_counter() - start, file_name))
        logger.debug(f"Downloaded {file_name}")

    @staticmethod
    async def fetch(session: ClientSession, url: str) -> Any:
        """Fetch from url."""
        return await session.get(url, timeout=REQUEST_TIMEOUT)

    @staticmethod
    async def fetch_json(session: ClientSession, url: str) -> Any:
        """Fetch from url."""
        response = await Downloader.fetch(session, url)
        return await response.json()

    @classmethod
    async def initialize(cls, config: UploaderConfig) -> Self:
        """Fetch the Latest Release from GitHub."""
        logger.debug(fetching_assets)
        async with aiohttp.ClientSession() as session:
            response_json, changelog_response_json = await asyncio.gather(
                Downloader.fetch_json(session, config.repo_url), Downloader.fetch_json(session, config.changelog_url)
            )
            if response_json.get("message") == not_found:
                raise ReleaseNotFoundError(no_release_found.format(config.repo_url), url=config.repo_url)
            changes = changelog_response_json.get("html_url")
            return cls(response_json, changes, config)

    async def download_latest(self: Self, config: UploaderConfig) -> None:
        """Download all latest assets :return: List of downloaded assets."""
        assets_from_api = self.response["assets"]
        matched_assets: list[tuple[Any, Any]] = []
        all_assets: list[tuple[Any, Any]] = []
        for asset in assets_from_api:
            asset_url = asset["browser_download_url"]
            app_name = asset["name"]
            all_assets.append((asset_url, app_name))
        for asset in all_assets:
            if re.search(config.assets_pattern, asset[1]):
                self.downloaded_files.append(str(temp_folder) + "/" + asset[1])
                matched_assets.append(asset)
            else:
                logger.debug(skipping_asset.format({asset[1]}))
        tasks = []
        for repo in matched_assets:
            task = asyncio.create_task(self._download(*repo))
            tasks.append(task)

        await asyncio.gather(*tasks)
        logger.info(downloaded_all.format(self.downloaded_files))

    def __str__(self: Self) -> str:
        """Returns the str representation of the app."""
        attrs = vars(self)
        return ", ".join([f"{key}: {value}" for key, value in attrs.items()])
