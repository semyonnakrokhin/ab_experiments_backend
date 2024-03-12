from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict
from pytz import UTC


def convert_datetime_to_gmt(dt: datetime) -> str:
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=UTC)

    return dt.strftime("%Y-%m-%dT%H:%M:%S%z")


class CustomModel(BaseModel):
    model_config = ConfigDict(
        json_encoders={datetime: convert_datetime_to_gmt},
        populate_by_name=True,
    )


class HTTPError(CustomModel):
    detail: str


class ColorOptions(Enum):
    RED = "#FF0000"
    GREEN = "#00FF00"
    BLUE = "#0000FF"


class PriceOptions(Enum):
    FIVE = 5
    TEN = 10
    TWENTY = 20
    FIFTY = 50


class ExperimentModel(CustomModel):
    pass


class ColorExperimentDto(ExperimentModel):
    name: str = "button_color"
    option: ColorOptions


class PriceExperimentDto(ExperimentModel):
    name: str = "price"
    option: PriceOptions


class ExperimentsDto(CustomModel):
    device_token: str
    button_color: ColorOptions
    price: PriceOptions
