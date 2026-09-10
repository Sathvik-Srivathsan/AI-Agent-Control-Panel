from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    OMNIROUTE_BASE_URL: str = "http://localhost:20128/v1"
    OMNIROUTE_API_KEY: str = ""
    MODEL: str = ""
    WORKSPACE_DIR: str = "./workspace"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def workspace_path(self) -> Path:
        return Path(self.WORKSPACE_DIR).resolve()


settings = Settings()
