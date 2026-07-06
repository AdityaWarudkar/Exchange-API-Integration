from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any

from src.models.enums import OrderSide, OrderType


class ExchangeClient(ABC):
    name: str

    @abstractmethod
    async def connect(self) -> None: ...

    @abstractmethod
    async def disconnect(self) -> None: ...

    @abstractmethod
    async def get_ticker(self, symbol: str) -> dict[str, Any]: ...

    @abstractmethod
    async def get_orderbook(self, symbol: str, limit: int = 20) -> dict[str, Any]: ...

    @abstractmethod
    async def get_balance(self) -> dict[str, Any]: ...

    @abstractmethod
    async def place_order(
        self,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: float,
        price: float | None = None,
    ) -> dict[str, Any]: ...

    @abstractmethod
    async def cancel_order(self, order_id: str, symbol: str) -> dict[str, Any]: ...

    @abstractmethod
    async def get_positions(self) -> list[dict[str, Any]]: ...

    @abstractmethod
    async def subscribe_market(self, symbol: str) -> AsyncIterator[dict[str, Any]]: ...

