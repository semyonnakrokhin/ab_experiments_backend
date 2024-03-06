import os
from pprint import pprint
from typing import Optional

from pydantic import BaseModel, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict

_apps_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)
)


class BrokerSettings(BaseModel):
    model_config = ConfigDict(extra="allow")

    transport: str
    userid: Optional[str] = None
    password: Optional[str] = None
    hostname: Optional[str] = None
    port: Optional[str] = None
    virtual_host: Optional[str] = None

    def __init__(self, **data):
        super().__init__(**data)
        self.broker_url = self.get_broker_url

    @property
    def get_broker_url(self):
        url = (
            f"{self.transport}://"
            + (u := "" if not self.user else f"{self.user}")
            + (p := "" if not self.password else f":{self.password}")
            + ("" if not any([u, p]) else "@")
            + f"{self.hostname}"
            + ("" if not self.port else f":{self.port}")
            + ("" if not self.virtual_host else f"/{self.virtual_host}")
        )

        return url


class ResultBackendSettings(BaseModel):
    model_config = ConfigDict(extra="allow")

    db: Optional[str] = None
    scheme: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None
    host: Optional[str] = None
    port: Optional[str] = None
    dbname: Optional[str] = None

    def __init__(self, **data):
        super().__init__(**data)
        self.result_backend_url = self.get_result_backend_url

    @property
    def get_result_backend_url(self):
        if not self.db:
            return "rpc://"

        url = (
            f"{self.db}"
            + ("" if not self.scheme else f"+{self.scheme}")
            + "://"
            + (u := "" if not self.user else f"{self.user}")
            + (p := "" if not self.password else f":{self.password}")
            + ("" if not any([u, p]) else "@")
            + f"{self.host}"
            + ("" if not self.port else f":{self.port}")
            + ("" if not self.dbname else f"/{self.dbname}")
        )

        return url


class CelerySettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file=os.path.join(_apps_dir, ".env.celery"),
        extra="allow",
    )

    broker: BrokerSettings
    result_backend: ResultBackendSettings


celery_settings = CelerySettings()


if __name__ == "__main__":
    celery_settings = CelerySettings()
    pprint(celery_settings.model_dump())
    c = 1
