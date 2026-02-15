from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PROJECT_NAME: str = "Behalysis API"
    PROJECT_VERSION: str = "1.0.0"
    DEBUG: bool = False

    DATABASE_URL: str = "postgresql+asyncpg://behalysis:behalysis@localhost:5432/behalysis"

    DATA_DIR: Path = Path("./data")
    IMAGES_DIR: Path = Path("./data/images")

    MAX_IMAGE_SIZE_BYTES: int = 2 * 1024 * 1024  # 2 MB

    @property
    def sync_database_url(self) -> str:
        return self.DATABASE_URL.replace("+asyncpg", "+psycopg2").replace(
            "postgresql+psycopg2", "postgresql"
        )


settings = Settings()

# Ensure data directories exist
settings.IMAGES_DIR.mkdir(parents=True, exist_ok=True)
