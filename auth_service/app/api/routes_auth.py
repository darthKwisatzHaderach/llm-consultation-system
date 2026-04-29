from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import AuthUsecaseDep, CurrentUserId
from app.schemas.auth import RegisterRequest, TokenResponse
from app.schemas.user import UserPublic

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=UserPublic)
async def register(body: RegisterRequest, uc: AuthUsecaseDep):
    return await uc.register(body.email, body.password)


@router.post("/login", response_model=TokenResponse)
async def login(uc: AuthUsecaseDep, form: OAuth2PasswordRequestForm = Depends()):
    token = await uc.login(form.username, form.password)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserPublic)
async def me(user_id: CurrentUserId, uc: AuthUsecaseDep):
    return await uc.me(user_id)
