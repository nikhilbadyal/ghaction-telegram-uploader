from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from queue import PriorityQueue
from time import perf_counter
from typing import Any, List, Tuple

import requests
from loguru import logger
from requests import Session
from tqdm import tqdm

temp_folder = Path("/app/apks")
session = Session()


class Downloader:
    @classmethod
    async def initialize(cls, url):
        self = cls()
        logger.debug("Fetching latest...")
        self.url = url
        self._CHUNK_SIZE = 2**21 * 5
        self._QUEUE = PriorityQueue()
        self._QUEUE_LENGTH = 0
        self.response = requests.get(url).json()
        return self

    def __download(self, url: str, file_name: str) -> None:
        logger.debug(f"Trying to download {file_name} from {url}")
        self._QUEUE_LENGTH += 1
        start = perf_counter()
        resp = session.get(url, stream=True)
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

    def __download_assets(self, url: str, file_name: str) -> None:
        self.__download(url, file_name=file_name)

    def download_latest(self) -> List:
        downloaded_files = []
        assets_from_api = self.response["assets"]
        assets: List[Tuple[Any, Any]] = []
        for asset in assets_from_api:
            url = asset["browser_download_url"]
            app_name = asset["name"]
            downloaded_files.append(str(temp_folder) + "/" + app_name)
            assets.append((url, app_name))
        with ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(lambda repo: self.__download_assets(*repo), assets)
        logger.info(f"Downloaded all revanced apps {downloaded_files}")
        return downloaded_files
