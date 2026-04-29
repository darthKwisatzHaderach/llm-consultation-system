import os

os.environ.setdefault("JWT_SECRET", "pytest_bot_jwt_secret_at_least_32chars!!")
os.environ.setdefault("JWT_ALG", "HS256")
os.environ.setdefault("OPENROUTER_API_KEY", "test-openrouter-key")
os.environ.setdefault("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
