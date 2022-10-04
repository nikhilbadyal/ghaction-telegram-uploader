import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from queue import PriorityQueue
from time import perf_counter
from typing import Any, List, Tuple

import requests
from loguru import logger
from requests import Session
from tqdm import tqdm

temp_folder = Path(f"{os.getcwd()}/apks")
session = Session()
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")
if not GITHUB_REPOSITORY:
    logger.error("GITHUB_REPOSITORY not specified")
    sys.exit(-1)
repo_url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/releases/latest"


class Downloader:
    def __init__(self, response):
        self._CHUNK_SIZE = 2**21 * 5
        self._QUEUE: PriorityQueue[Tuple] = PriorityQueue()
        self._QUEUE_LENGTH = 0
        self.response = response

    @classmethod
    async def initialize(cls):
        logger.debug("Fetching latest assets...")
        print(repo_url)
        response = requests.get(repo_url).json()
        print(response)
        self = cls(response)
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
        with temp_folder.joinpath(file_name).open("wb") as dl_file, bar:
            for chunk in resp.iter_content(self._CHUNK_SIZE):
                size = dl_file.write(chunk)
                bar.update(size)
        self._QUEUE.put((perf_counter() - start, file_name))
        logger.debug(f"Downloaded {file_name}")

    def __download_assets(self, asset_url: str, file_name: str) -> None:
        self.__download(asset_url, file_name=file_name)

    def download_latest(self) -> List:
        downloaded_files = []
        assets_from_api = self.response["assets"]
        assets: List[Tuple[Any, Any]] = []
        for asset in assets_from_api:
            asset_url = asset["browser_download_url"]
            app_name = asset["name"]
            downloaded_files.append(str(temp_folder) + "/" + app_name)
            assets.append((asset_url, app_name))
        with ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(lambda repo: self.__download_assets(*repo), assets)
        logger.info(f"Downloaded all assets {downloaded_files}")
        return downloaded_files
