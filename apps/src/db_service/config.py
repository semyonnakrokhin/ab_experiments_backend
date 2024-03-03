import os

from pydantic_settings import BaseSettings, SettingsConfigDict

_apps_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)
)


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(_apps_dir, ".env"), extra="allow"
    )

    mode: str
    db_host: str
    db_port: str
    db_user: str
    db_pass: str
    db_name: str

    def __init__(self, **data):
        super().__init__(**data)
        self.dsn = self.async_postgres_dsn

    @property
    def async_postgres_dsn(self) -> str:
        return (
            f"postgresql+asyncpg"
            f"://{self.db_user}"
            f":{self.db_pass}@{self.db_host}"
            f":{self.db_port}/{self.db_name}"
        )
