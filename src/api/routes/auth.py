from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_db
from src.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenPair, UserRead
from src.services.auth_service import AuthService

router = APIRouter(tags=["Authentication"])


@router.post("/register", response_model=UserRead, status_code=201)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService(db).register(payload)


@router.post("/login", response_model=TokenPair)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService(db).login(payload.email, payload.password)


@router.post("/refresh", response_model=TokenPair)
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService(db).refresh(payload.refresh_token)

