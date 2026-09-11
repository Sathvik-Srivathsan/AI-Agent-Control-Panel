from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_ENV_CANDIDATES = [Path(".env"), _PROJECT_ROOT / ".env"]
_ENV_FILES = tuple(str(p) for p in _ENV_CANDIDATES if p.exists())


class Settings(BaseSettings):
    OMNIROUTE_BASE_URL: str = "http://localhost:20128/v1"
    OMNIROUTE_API_KEY: str = ""
    MODEL: str = ""
    WORKSPACE_DIR: str = "./workspace"

    model_config = SettingsConfigDict(env_file=_ENV_FILES, env_file_encoding="utf-8")

    @property
    def workspace_path(self) -> Path:
        return Path(self.WORKSPACE_DIR).resolve()


settings = Settings()
