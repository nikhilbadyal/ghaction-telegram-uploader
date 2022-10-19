"""Env Configurations."""

from environs import Env


class UploaderConfig:
    """Revanced Configurations."""

    def __init__(self, env: Env) -> None:
        self.env = env
        self.assets_pattern = env.str("INPUT_ASSETS_PATTERN", ".*")
