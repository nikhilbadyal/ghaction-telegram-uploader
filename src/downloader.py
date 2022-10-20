"""Downloader."""
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from queue import PriorityQueue
from time import perf_counter
from typing import Any, Dict, List, Tuple

import requests
from loguru import logger
from requests import Session
from tqdm import tqdm

from src.config import UploaderConfig

temp_folder = Path(f"{os.getcwd()}/apks")
session = Session()
GITHUB_REPOSITORY = os.getenv("INPUT_DOWNLOAD_GITHUB_REPOSITORY", None)
print(os.environ)
if not GITHUB_REPOSITORY:
    GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")
CHANGELOG_GITHUB_REPOSITORY = os.getenv(
    "INPUT_CHANGELOG_GITHUB_REPOSITORY", GITHUB_REPOSITORY
)
repo_url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/releases/latest"
changelog_url = (
    f"https://api.github.com/repos/{CHANGELOG_GITHUB_REPOSITORY}/releases/latest"
)


class Downloader:
    """Downloader."""

    def __init__(self, response: Dict[Any, Any], changes: str):
        self._CHUNK_SIZE = 10485760
        self._QUEUE: PriorityQueue[Tuple[float, str]] = PriorityQueue()
        self._QUEUE_LENGTH = 0
        self.response = response
        self.downloaded_files: List[str] = []
        self.changes = changes

    @classmethod
    async def initialize(cls) -> "Downloader":
        """
        Fetch the Latest Release from GitHub
        :return:
        """
        logger.debug("Fetching latest assets...")
        response = requests.get(repo_url).json()
        changelog_response = requests.get(changelog_url).json()
        if response.get("message") == "Not Found":
            logger.info(f"No Release found in {repo_url}. Exiting.")
            sys.exit(0)
        changes = changelog_response.get("html_url")
        self = cls(response, changes)
        return self

    def __download(self, assets_url: str, file_name: str) -> None:
        logger.debug(f"Trying to download {file_name} from {assets_url}")
        self._QUEUE_LENGTH += 1
        start = perf_counter()
        resp = session.get(assets_url, stream=True)
        total = int(resp.headers.get("content-length", 0))
        bar = tqdm(
            desc=file_name,
            total=total,
            unit="iB",
            unit_scale=True,
            unit_divisor=1024,
            colour="green",
        )
        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)
        with temp_folder.joinpath(file_name).open("wb") as dl_file, bar:
            for chunk in resp.iter_content(self._CHUNK_SIZE):
                size = dl_file.write(chunk)
                bar.update(size)
        self._QUEUE.put((perf_counter() - start, file_name))
        logger.debug(f"Downloaded {file_name}")

    def __download_assets(self, asset_url: str, file_name: str) -> None:
        self.__download(asset_url, file_name=file_name)

    def download_latest(self, config: UploaderConfig) -> None:
        """
        Download all latest assets
        :return: List of downloaded assets
        """
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
                logger.info(f"{asset[1]} matched.")
            else:
                logger.debug(f"Skipping {asset[1]}.")
        with ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(lambda repo: self.__download_assets(*repo), matched_assets)
        logger.info(f"Downloaded all assets {self.downloaded_files}")
