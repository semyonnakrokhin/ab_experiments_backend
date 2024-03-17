from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List

from apps.src.app_types import D


class AbstractDatabaseRepository(ABC, Generic[D]):
    @abstractmethod
    async def insert_one(self, data: D) -> D:
        pass

    @abstractmethod
    async def select_some_by_params(self, params: Dict[str, Any]) -> List[D]:
        pass
