#!/usr/bin/env python3
"""
Тестовый скрипт для проверки Yandex SpeechKit TTS API
Помогает диагностировать проблемы с авторизацией
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Получаем настройки из .env
api_key = os.environ.get('YANDEX_TTS_API_KEY', '')
folder_id = os.environ.get('YANDEX_TTS_FOLDER_ID', '')

print("=" * 60)
print("🧪 ТЕСТ YANDEX SPEECHKIT TTS API")
print("=" * 60)
print()

if not api_key:
    print("❌ ОШИБКА: YANDEX_TTS_API_KEY не установлен в .env")
    exit(1)

print(f"✅ API ключ найден: {api_key[:10]}...")
print(f"   Folder ID: {folder_id if folder_id else 'не указан'}")
print()

# URL API
url = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'

# Заголовки
headers = {
    'Authorization': f'Api-Key {api_key}'
}

# Данные запроса (form-urlencoded)
data = {
    'text': 'Тестовое сообщение',
    'lang': 'ru-RU',
    'voice': 'jane',
    'format': 'oggopus'
}

print("📡 Отправка запроса:")
print(f"   URL: {url}")
print(f"   Method: POST")
print(f"   Headers: Authorization=Api-Key {api_key[:10]}...")
print(f"   Data: text=Тестовое сообщение, lang=ru-RU, voice=jane, format=oggopus")
print(f"   Content-Type: application/x-www-form-urlencoded (автоматически)")
print()

try:
    response = requests.post(url, headers=headers, data=data, timeout=10)
    
    print(f"📥 Ответ сервера:")
    print(f"   Status Code: {response.status_code}")
    print(f"   Headers: {dict(response.headers)}")
    print()
    
    if response.status_code == 200:
        print("✅ УСПЕХ! API ключ работает!")
        print(f"   Размер аудио: {len(response.content)} байт")
        # Сохраняем тестовый файл
        with open('test_audio.ogg', 'wb') as f:
            f.write(response.content)
        print("   Аудио сохранено в: test_audio.ogg")
    else:
        print("❌ ОШИБКА!")
        print(f"   Ответ: {response.text}")
        print()
        print("💡 Возможные причины:")
        print("   1. API ключ создан для личного аккаунта, а не для сервисного")
        print("   2. Роль 'ai.speechkit-tts.user' не назначена сервисному аккаунту")
        print("   3. API ключ неверный или отозван")
        print("   4. Проблемы с платежным аккаунтом Yandex Cloud")
        
except Exception as e:
    print(f"❌ ИСКЛЮЧЕНИЕ: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)

