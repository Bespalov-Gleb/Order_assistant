"""
Yandex Cloud авторизация (синхронная версия)
Адаптировано из infrastructure/auth_handler.py
"""
import json
import os
import time
from datetime import datetime, timezone

import requests


class YandexAuth:
    def __init__(self, oauth_token: str, folder_id: str, private_key: str = None):
        self.oauth_token = oauth_token
        self.folder_id = folder_id
        self.private_key = private_key
        self.service_account_id = None
        self.key_id = None
        self.iam_token: str | None = None
        self.iam_token_expiration: datetime | None = None

    def get_iam_token(self) -> str | None:
        """Получение IAM токена через OAuth (синхронная версия)"""
        # Проверяем кэш
        if self.iam_token and self.iam_token_expiration and self.iam_token_expiration > datetime.now(tz=timezone.utc):
            return self.iam_token

        try:
            response = requests.post(
                "https://iam.api.cloud.yandex.net/iam/v1/tokens",
                json={"yandexPassportOauthToken": self.oauth_token},
                timeout=10
            )
            
            if response.status_code != 200:
                error_data = response.json() if response.content else {}
                if error_data.get("code") == 16:
                    print("❌ [YANDEX AUTH] OAuth токен неверный или истек")
                    return None
                print(f"❌ [YANDEX AUTH] Ошибка получения IAM токена: {response.status_code} - {response.text}")
                return None
            
            data = response.json()
            self.iam_token = data["iamToken"]
            # Парсим expiresAt (формат: "2024-01-01T12:00:00.000000000Z")
            expires_at_str = data["expiresAt"]
            try:
                # Упрощенный парсинг: убираем наносекунды и Z, добавляем timezone
                if "." in expires_at_str:
                    expires_at_str = expires_at_str.split(".")[0]
                if expires_at_str.endswith("Z"):
                    expires_at_str = expires_at_str[:-1]
                if not expires_at_str.endswith("+00:00") and not expires_at_str.endswith("-00:00"):
                    expires_at_str += "+00:00"
                self.iam_token_expiration = datetime.fromisoformat(expires_at_str)
            except Exception as e:
                # Если не удалось распарсить, устанавливаем время истечения через 12 часов
                print(f"⚠️  [YANDEX AUTH] Не удалось распарсить expiresAt, устанавливаем 12 часов: {e}")
                from datetime import timedelta
                self.iam_token_expiration = datetime.now(tz=timezone.utc) + timedelta(hours=12)
            
            print(f"✅ [YANDEX AUTH] IAM токен получен (истекает: {self.iam_token_expiration})")
            return self.iam_token
            
        except Exception as e:
            print(f"❌ [YANDEX AUTH] Ошибка получения IAM токена: {e}")
            import traceback
            traceback.print_exc()
            return None

