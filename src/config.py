"""Env Configurations."""

from environs import Env, EnvValidationError


class UploaderConfig:
    """Revanced Configurations."""

    def __init__(self, env: Env) -> None:
        self.env = env
        self.assets_pattern = env.str("INPUT_ASSETS_PATTERN", ".*")
        try:
            self.send_message = env.bool("INPUT_SEND_MESSAGE", True)
        except EnvValidationError:
            self.send_message = True
        try:
            self.send_sticker = env.bool("INPUT_SEND_STICKER", False)
        except EnvValidationError:
            self.send_sticker = False
        try:
            self.message = env.str("INPUT_MESSAGE", None)
        except EnvValidationError:
            self.message = None
