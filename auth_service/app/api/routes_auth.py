from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_auth_uc, get_current_user_id
from app.schemas.auth import RegisterRequest, TokenResponse
from app.schemas.user import UserPublic
from app.usecases.auth import AuthUsecase

router = APIRouter()


@router.post("/register", response_model=UserPublic)
async def register(body: RegisterRequest, uc: AuthUsecase = Depends(get_auth_uc)):
    return await uc.register(body.email, body.password)


@router.post("/login", response_model=TokenResponse)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    uc: AuthUsecase = Depends(get_auth_uc),
):
    token = await uc.login(form.username, form.password)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserPublic)
async def me(
    user_id: int = Depends(get_current_user_id),
    uc: AuthUsecase = Depends(get_auth_uc),
):
    return await uc.me(user_id)
