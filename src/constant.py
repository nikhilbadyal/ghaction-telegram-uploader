"""Common constants."""
from pathlib import Path

REQUEST_TIMEOUT = 60
default_sticker = "CAACAgUAAxkBAAEYpFpjOplSFK_q93KWoJKqWHGfgPMxMwACuAYAApqD2VV9UCzjLNawRCoE"
temp_folder = Path(f"{Path.cwd()}/apks")
status_code_200 = 200
GITHUB_API_BASE_URL = "https://api.github.com"
GITHUB_API_REPO_URL = GITHUB_API_BASE_URL + "/repos/{}"
GITHUB_API_LATEST_RELEASE_URL = GITHUB_API_REPO_URL + "/releases/latest"
