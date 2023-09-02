"""Downloader."""
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from queue import PriorityQueue
from time import perf_counter
from typing import Any, Dict, List, Self, Tuple

import requests
from loguru import logger
from tqdm import tqdm

from src.config import UploaderConfig
from src.constant import REQUEST_TIMEOUT, temp_folder
from src.exception import DownloadError
from src.strings import downloaded_all, fetching_assets, no_release_found, no_url, not_found, skipping_asset
from src.utils import handle_request_response


class Downloader(object):
    """Downloader."""

    def __init__(self: Self, response: Dict[Any, Any], changes: str, config: UploaderConfig) -> None:
        self._CHUNK_SIZE = 10485760
        self._QUEUE: PriorityQueue[Tuple[float, str]] = PriorityQueue()
        self._QUEUE_LENGTH = 0
        self.response = response
        self.downloaded_files: List[str] = []
        self.changes = changes
        self.config = config

    def _download(self: Self, url: str, file_name: str) -> None:
        if not url:
            raise DownloadError(no_url)
        logger.info(f"Trying to download {file_name} from {url}")
        self._QUEUE_LENGTH += 1
        start = perf_counter()
        headers = {}
        if self.config.personal_access_token and "github" in url:
            logger.debug("Using personal access token")
            headers["Authorization"] = f"token {self.config.personal_access_token}"
        response = requests.get(url, stream=True, headers=headers, timeout=REQUEST_TIMEOUT)
        handle_request_response(response, url)
        total = int(response.headers.get("content-length", 0))
        bar = tqdm(
            desc=file_name,
            total=total,
            unit="iB",
            unit_scale=True,
            unit_divisor=1024,
            colour="green",
        )
        with self.config.temp_folder.joinpath(file_name).open("wb") as dl_file, bar:
            for chunk in response.iter_content(self._CHUNK_SIZE):
                size = dl_file.write(chunk)
                bar.update(size)
        self._QUEUE.put((perf_counter() - start, file_name))
        logger.debug(f"Downloaded {file_name}")

    @classmethod
    async def initialize(cls, config: UploaderConfig) -> Self:
        """Fetch the Latest Release from GitHub."""
        logger.debug(fetching_assets)
        response = requests.get(config.repo_url, timeout=REQUEST_TIMEOUT)
        handle_request_response(response, config.repo_url)
        response_json = response.json()
        changelog_response = requests.get(config.changelog_url, timeout=REQUEST_TIMEOUT)
        handle_request_response(changelog_response, config.changelog_url)
        changelog_response_json = changelog_response.json()
        if response_json.get("message") == not_found:
            logger.info(no_release_found.format(config.repo_url))
            sys.exit(0)
        changes = changelog_response_json.get("html_url")
        return cls(response_json, changes, config)

    def __download_assets(self: Self, asset_url: str, file_name: str) -> None:
        self._download(asset_url, file_name=file_name)

    def download_latest(self: Self, config: UploaderConfig) -> None:
        """Download all latest assets :return: List of downloaded assets."""
        assets_from_api = self.response["assets"]
        matched_assets: List[Tuple[Any, Any]] = []
        all_assets: List[Tuple[Any, Any]] = []
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
        with ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(lambda repo: self.__download_assets(*repo), matched_assets)
        logger.info(downloaded_all.format(self.downloaded_files))

    def __str__(self: Self) -> str:
        """Returns the str representation of the app."""
        attrs = vars(self)
        return ", ".join([f"{key}: {value}" for key, value in attrs.items()])
