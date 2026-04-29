import os

os.environ.setdefault("JWT_SECRET", "pytest_jwt_secret_key_at_least_32chars!!")
os.environ.setdefault("JWT_ALG", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
os.environ.setdefault("APP_NAME", "auth-pytest")
