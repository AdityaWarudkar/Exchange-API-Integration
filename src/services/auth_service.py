from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import get_settings
from src.core.security import create_token, decode_token, hash_password, verify_password
from src.models.user import User
from src.repositories.balances import BalanceRepository
from src.repositories.users import UserRepository
from src.schemas.auth import RegisterRequest, TokenPair


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.users = UserRepository(db)

    async def register(self, payload: RegisterRequest) -> User:
        if await self.users.get_by_email(payload.email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="email already registered")
        user = await self.users.create(
            User(email=payload.email, hashed_password=hash_password(payload.password), role=payload.role)
        )
        await BalanceRepository(self.db).get_or_create_usdt(user.id, get_settings().paper_starting_balance)
        await self.db.commit()
        return user

    async def login(self, email: str, password: str) -> TokenPair:
        user = await self.users.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")
        return self._tokens(user)

    async def refresh(self, refresh_token: str) -> TokenPair:
        try:
            payload = decode_token(refresh_token)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid refresh token") from exc
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid refresh token")
        user = await self.users.get(int(payload["sub"]))
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user no longer exists")
        return self._tokens(user)

    def _tokens(self, user: User) -> TokenPair:
        settings = get_settings()
        claims = {"role": user.role.value}
        return TokenPair(
            access_token=create_token(
                str(user.id),
                "access",
                timedelta(minutes=settings.access_token_expire_minutes),
                claims,
            ),
            refresh_token=create_token(
                str(user.id),
                "refresh",
                timedelta(days=settings.refresh_token_expire_days),
                claims,
            ),
        )

