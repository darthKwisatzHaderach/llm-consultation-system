def jwt_storage_key(telegram_user_id: int) -> str:
    return f"token:{telegram_user_id}"
