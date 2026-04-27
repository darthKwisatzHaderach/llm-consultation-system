from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "bot-service"
    ENV: str = "local"

    telegram_bot_token: str = Field(default="", validation_alias="TELEGRAM_BOT_TOKEN")
    auth_service_url: str = Field(default="http://localhost:8000", validation_alias="AUTH_SERVICE_URL")

    jwt_secret: str = Field(default="change_me_super_secret", validation_alias="JWT_SECRET")
    jwt_alg: str = Field(default="HS256", validation_alias="JWT_ALG")

    redis_url: str = Field(default="redis://redis:6379/0", validation_alias="REDIS_URL")
    rabbitmq_url: str = Field(
        default="amqp://guest:guest@rabbitmq:5672//",
        validation_alias="RABBITMQ_URL",
    )

    openrouter_api_key: str = Field(default="", validation_alias="OPENROUTER_API_KEY")
    openrouter_base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        validation_alias="OPENROUTER_BASE_URL",
    )
    openrouter_model: str = Field(
        default="stepfun/step-3.5-flash:free",
        validation_alias="OPENROUTER_MODEL",
    )
    openrouter_site_url: str = Field(
        default="https://example.com",
        validation_alias="OPENROUTER_SITE_URL",
    )
    openrouter_app_name: str = Field(
        default="bot-service",
        validation_alias="OPENROUTER_APP_NAME",
    )


settings = Settings()
