# ghaction-telegram-uploader

A GitHub Action to automatically fetch the latest release assets from any GitHub repository and upload them to a specified Telegram chat, group, or channel as documents, with optional message and sticker support.

---

## Features

- **Automatic Asset Download:** Fetches release assets from a GitHub repository (matches by regex).
- **Telegram Upload:** Uploads all matched assets to a Telegram chat/channel via a bot.
- **Customizable Messaging:** Sends a message (custom or auto-generated) and optionally a sticker along with uploads.
- **Docker-based:** Runs in a Docker container for isolation and reproducibility.
- **Secure:** Supports GitHub personal access token for accessing private repos and secure Telegram credentials.
- **Progress Reporting:** Uses tqdm and loguru for progress and debug logging.
- **Highly Configurable:** All settings via action inputs/environment variables.

---

## How it Works

1. **Initialization**: Reads configuration from GitHub Action inputs/environment variables.
2. **Download Phase**:
   - Fetches the latest release info from the GitHub API.
   - Downloads all release assets matching a provided regex pattern.
   - Supports use of GitHub personal access token for private repos.
3. **Telegram Phase**:
   - Initializes a Pyrogram Telegram bot connection using the provided credentials.
   - Sends an optional sticker and/or message.
   - Uploads each downloaded asset as a document to the target chat/channel.
   - Logs progress and errors throughout.

---

## Usage

### Minimal Example

```yaml
- name: Upload GitHub Release Assets to Telegram
  uses: nikhilbadyal/ghaction-telegram-uploader@v1
  with:
    API_ID: ${{ secrets.TELEGRAM_API_ID }}
    API_HASH: ${{ secrets.TELEGRAM_API_HASH }}
    BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
    CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
    DOWNLOAD_GITHUB_REPOSITORY: "OWNER/REPO"   # e.g. nikhilbadyal/docker-py-revanced
    ASSETS_PATTERN: ".*\\.apk$"                # Only APK assets (optional, default: all)
    MESSAGE: "New builds are here!"
    STICKER_ID: "CAACAgUAAx..."                # Optional
```

### Full Input Reference

| Name                        | Required | Description                                                                                       |
|-----------------------------|----------|---------------------------------------------------------------------------------------------------|
| `API_ID`                    | Yes      | Telegram API ID (get from https://my.telegram.org).                                               |
| `API_HASH`                  | Yes      | Telegram API Hash (get from https://my.telegram.org).                                             |
| `BOT_TOKEN`                 | Yes      | Telegram Bot token (from BotFather).                                                              |
| `CHAT_ID`                   | Yes      | Chat/Channel ID to send files to (can be numeric or `@username`).                                 |
| `STICKER_ID`                | No       | Sticker to send before uploads.                                                                   |
| `CHANGELOG_GITHUB_REPOSITORY` | No     | Repository (OWNER/REPO) to fetch changelog from (defaults to DOWNLOAD_GITHUB_REPOSITORY).         |
| `DOWNLOAD_GITHUB_REPOSITORY` | No      | Repository (OWNER/REPO) to download release assets from (defaults to current repo).               |
| `ASSETS_PATTERN`            | No       | Regex pattern for asset name matching (default: `.*`, i.e., all assets).                          |
| `MESSAGE`                   | No       | Message to send before uploads. If not set, sends auto-generated changelog link.                  |
| `PERSONAL_ACCESS_TOKEN`     | No       | GitHub personal access token (for downloading from private repos).                                |

---

## How to get Telegram credentials

- **API_ID & API_HASH:** Register your app at https://my.telegram.org.
- **BOT_TOKEN:** Create a bot via BotFather and get the token.
- **CHAT_ID:** You can use [userinfobot](https://t.me/userinfobot) to get your `chat_id`, or use negative IDs for channels/supergroups.

---

## Example Workflow

```yaml
name: Upload Release to Telegram
on:
  release:
    types: [published]

jobs:
  telegram-upload:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Upload assets to Telegram
        uses: nikhilbadyal/ghaction-telegram-uploader@v1
        with:
          API_ID: ${{ secrets.TELEGRAM_API_ID }}
          API_HASH: ${{ secrets.TELEGRAM_API_HASH }}
          BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
          DOWNLOAD_GITHUB_REPOSITORY: ${{ github.repository }}
          ASSETS_PATTERN: ".*"
          MESSAGE: "Release ${{ github.ref_name }} is live! 🚀"
```

---

## Internal Architecture

- **main.py**: Entrypoint; orchestrates Downloader and Telegram upload logic.
- **src/config.py**: Loads and validates all configuration/environment variables.
- **src/downloader/download.py**: Handles GitHub API interaction, asset filtering, and downloading.
- **src/telegram.py**: Handles Telegram connection, sticker/message sending, and file uploads via Pyrogram.
- **src/constant.py**: Stores constants (e.g., API URLs, timeouts, temp folder).
- **src/exception.py**: Custom error classes for robust error handling.
- **src/strings.py**: User-facing and log messages.

---

## Dependencies

- [Pyrogram](https://docs.pyrogram.org/) (Telegram Bot API)
- [aiohttp](https://docs.aiohttp.org/) (Async HTTP for downloads)
- [tqdm](https://tqdm.github.io/) (Progress bars)
- [loguru](https://github.com/Delgan/loguru) (Logging)
- [environs](https://github.com/sloria/environs) (Env var parsing)
- [requests](https://docs.python-requests.org/) (For some API calls)

All dependencies are listed in `requirements.txt`.

---

## Development

- **Build Docker image:**
  ```
  docker build -t ghaction-telegram-uploader .
  ```
- **Run locally:**
  Set all required environment variables as per the inputs above and run `python main.py`.

---

## License

MIT License. See [LICENSE](LICENSE) for full text.

---

## Author

- [@nikhilbadyal](https://github.com/nikhilbadyal)
