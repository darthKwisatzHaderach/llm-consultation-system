from app.core.exceptions import InvalidCredentialsError, UserAlreadyExistsError, UserNotFoundError
from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.users import UsersRepository
from app.schemas.user import UserPublic


def _normalize_email(email: str) -> str:
    return email.strip().lower()


class AuthUsecase:
    def __init__(self, users: UsersRepository):
        self.users = users

    async def register(self, email: str, password: str) -> UserPublic:
        email = _normalize_email(email)
        existing = await self.users.get_by_email(email)
        if existing is not None:
            raise UserAlreadyExistsError()

        password_hash = hash_password(password)
        user = await self.users.create(email=email, password_hash=password_hash)
        return UserPublic.model_validate(user)

    async def login(self, email: str, password: str) -> str:
        email = _normalize_email(email)
        user = await self.users.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()

        return create_access_token(sub=str(user.id), role=user.role)

    async def me(self, user_id: int) -> UserPublic:
        user = await self.users.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError()
        return UserPublic.model_validate(user)
