from pathlib import Path
from queue import PriorityQueue
from time import perf_counter

from loguru import logger
from requests import Session
from tqdm import tqdm

temp_folder = Path("/app/apks")
session = Session()


class Downloader(object):
    _CHUNK_SIZE = 2**21 * 5
    _QUEUE = PriorityQueue()
    _QUEUE_LENGTH = 0

    @classmethod
    def _download(cls, url: str, file_name: str) -> None:
        logger.debug(f"Trying to download {file_name} from {url}")
        cls._QUEUE_LENGTH += 1
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
            for chunk in resp.iter_content(cls._CHUNK_SIZE):
                size = dl_file.write(chunk)
                bar.update(size)
        cls._QUEUE.put((perf_counter() - start, file_name))
        logger.debug(f"Downloaded {file_name}")

    @classmethod
    def download_assets(cls, url: str, file_name: str) -> None:
        cls._download(url, file_name=file_name)
