import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Конфигурация приложения"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    APPLICATION_ROOT = os.environ.get('APP_PREFIX', '/')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///order_assistant.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload settings
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'xlsx'}
    
    # Audio settings
    TTS_LANGUAGE = 'ru'
    TTS_SLOW = False
    
    # Yandex SpeechKit settings
    # OAuth токен для получения IAM токена (рекомендуется, как в рабочем примере)
    YANDEX_TTS_OAUTH_TOKEN = os.environ.get('YANDEX_TTS_OAUTH_TOKEN', '')
    # API ключ (альтернативный способ, если OAuth токен недоступен)
    YANDEX_TTS_API_KEY = os.environ.get('YANDEX_TTS_API_KEY', '')
    YANDEX_TTS_FOLDER_ID = os.environ.get('YANDEX_TTS_FOLDER_ID', '')
    YANDEX_TTS_VOICE = os.environ.get('YANDEX_TTS_VOICE', 'jane')  # jane, oksana, omazh, zahar, ermil
    YANDEX_TTS_ENABLED = os.environ.get('YANDEX_TTS_ENABLED', 'false').lower() == 'true'



