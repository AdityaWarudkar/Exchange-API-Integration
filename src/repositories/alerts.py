from sqlalchemy.ext.asyncio import AsyncSession

from src.models.alert import Alert


class AlertRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def add(self, alert: Alert) -> Alert:
        self.db.add(alert)
        await self.db.flush()
        await self.db.refresh(alert)
        return alert

