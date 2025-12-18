import os
import requests
from gtts import gTTS
from models import FilterWord
from config import Config
from yandex_auth import YandexAuth
from yandex_speech_service import YandexSpeechService


def should_filter_item(item_name, filter_words):
    """
    Проверяет, содержит ли название товара фильтруемые слова
    
    Args:
        item_name: Название товара
        filter_words: Список объектов FilterWord из БД
    
    Returns:
        bool: True если товар нужно отфильтровать (пропустить озвучивание)
    """
    if not filter_words:
        return False
    
    item_name_lower = item_name.lower()
    
    for filter_word in filter_words:
        if filter_word.word.lower() in item_name_lower:
            return True
    
    return False


def clean_text_for_speech(text):
    """
    Очищает текст для лучшего озвучивания
    Убирает символы, которые плохо озвучиваются
    """
    # Заменяем & на "и"
    text = text.replace('&', ' и ')
    
    # Убираем лишние пробелы
    text = ' '.join(text.split())
    
    return text




def generate_tts_yandex(text, output_path='static/audio/speech.ogg', voice='jane'):
    """
    Генерирует аудио файл из текста с помощью Yandex SpeechKit TTS (API v3)
    Использует рабочий код из infrastructure/
    
    Args:
        text: Текст для озвучивания
        output_path: Путь к выходному файлу (OGG формат)
        voice: Голос (jane, oksana, omazh, zahar, ermil)
    
    Returns:
        str: Путь к созданному файлу или None в случае ошибки
    """
    print("=" * 60)
    print("🔍 [YANDEX TTS v3] Начало генерации")
    print(f"   Текст: {text[:50]}...")
    print(f"   Путь: {output_path}")
    print(f"   Голос: {voice}")
    print("=" * 60)
    
    try:
        oauth_token = Config.YANDEX_TTS_OAUTH_TOKEN
        folder_id = Config.YANDEX_TTS_FOLDER_ID
        
        print(f"🔑 [YANDEX TTS] OAUTH_TOKEN: {'✅ Установлен' if oauth_token else '❌ ОТСУТСТВУЕТ'}")
        print(f"🔑 [YANDEX TTS] FOLDER_ID: {'✅ Установлен' if folder_id else '❌ ОТСУТСТВУЕТ'}")
        
        if not oauth_token:
            print("❌ [YANDEX TTS] ОШИБКА: отсутствует YANDEX_TTS_OAUTH_TOKEN")
            print("   Получите OAuth токен: https://oauth.yandex.ru/authorize?response_type=token&client_id=<client_id>")
            print("   Или используйте: https://yandex.cloud/ru/docs/iam/concepts/authorization/oauth-token")
            return None
        
        if not folder_id:
            print("❌ [YANDEX TTS] ОШИБКА: отсутствует YANDEX_TTS_FOLDER_ID")
            print("   Укажите Folder ID вашего каталога в Yandex Cloud")
            return None
        
        # Создаем директорию если не существует
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Очищаем текст
        clean_text = clean_text_for_speech(text)
        
        # Инициализируем авторизацию и сервис
        auth = YandexAuth(oauth_token, folder_id)
        speech_service = YandexSpeechService(folder_id)
        
        # Получаем IAM токен
        print("🔑 [YANDEX TTS] Получение IAM токена из OAuth токена...")
        iam_token = auth.get_iam_token()
        
        if not iam_token:
            print("❌ [YANDEX TTS] Не удалось получить IAM токен")
            print("   Проверьте правильность OAuth токена")
            return None
        
        # Синтезируем речь через API v3
        print("🎤 [YANDEX TTS] Синтез речи через API v3...")
        audio_data = speech_service.synthesize(clean_text, iam_token, voice=voice, format="OGG_OPUS")
        
        if not audio_data:
            print("❌ [YANDEX TTS] Не удалось синтезировать речь")
            return None
        
        # Сохраняем аудио
        with open(output_path, 'wb') as f:
            f.write(audio_data)
        
        file_size = len(audio_data)
        print(f"✅ [YANDEX TTS v3] УСПЕХ! Аудио сохранено: {output_path} ({file_size} байт)")
        print("=" * 60)
        return output_path
    
    except Exception as e:
        print(f"❌ [YANDEX TTS] ИСКЛЮЧЕНИЕ: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        return None


def generate_tts(text, output_path='static/audio/speech.mp3', lang='ru', slow=False):
    """
    Генерирует аудио файл из текста.
    Использует Yandex SpeechKit если настроен, иначе Google TTS (gTTS).
    
    Args:
        text: Текст для озвучивания
        output_path: Путь к выходному файлу
        lang: Язык (по умолчанию 'ru')
        slow: Медленная речь (по умолчанию False, игнорируется для Yandex)
    
    Returns:
        str: Путь к созданному файлу или None в случае ошибки
    """
    print("\n" + "=" * 60)
    print("🎤 [TTS] Начало генерации речи")
    print(f"   Текст: {text[:50]}...")
    print(f"   Путь: {output_path}")
    print("=" * 60)
    
    # Проверяем настройки Yandex
    yandex_enabled = Config.YANDEX_TTS_ENABLED
    api_key = Config.YANDEX_TTS_API_KEY
    folder_id = Config.YANDEX_TTS_FOLDER_ID
    voice = Config.YANDEX_TTS_VOICE
    
    print(f"🔧 [TTS] YANDEX_TTS_ENABLED: {yandex_enabled} (тип: {type(yandex_enabled)})")
    print(f"🔧 [TTS] YANDEX_TTS_API_KEY: {'✅ Есть' if api_key else '❌ НЕТ'} ({len(api_key) if api_key else 0} символов)")
    print(f"🔧 [TTS] YANDEX_TTS_FOLDER_ID: {'✅ Есть' if folder_id else '❌ НЕТ'} ({len(folder_id) if folder_id else 0} символов)")
    print(f"🔧 [TTS] YANDEX_TTS_VOICE: {voice}")
    
    # Пробуем Yandex SpeechKit если включен
    if yandex_enabled:
        print("✅ [TTS] Yandex TTS ВКЛЮЧЕН - пробуем использовать")
        # Меняем расширение на .ogg для Yandex
        yandex_path = output_path.replace('.mp3', '.ogg')
        result = generate_tts_yandex(text, yandex_path, voice)
        if result:
            print("✅ [TTS] Использован Yandex TTS")
            return result
        # Если Yandex не сработал, fallback на gTTS
        print("⚠️  [TTS] Yandex TTS не сработал, используем gTTS (fallback)")
    else:
        print("ℹ️  [TTS] Yandex TTS ОТКЛЮЧЕН - используем gTTS")
    
    # Fallback на Google TTS
    print("🔄 [TTS] Использование Google TTS (gTTS)")
    try:
        # Создаем директорию если не существует
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Очищаем текст
        clean_text = clean_text_for_speech(text)
        print(f"📝 [TTS] Очищенный текст: {clean_text[:50]}...")
        
        # Генерируем аудио через gTTS
        print("📡 [TTS] Отправка запроса в Google TTS...")
        tts = gTTS(text=clean_text, lang=lang, slow=slow)
        tts.save(output_path)
        
        file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
        print(f"✅ [TTS] Аудио сгенерировано через gTTS: {output_path} ({file_size} байт)")
        print("=" * 60 + "\n")
        return output_path
    
    except Exception as e:
        print(f"❌ [TTS] ОШИБКА генерации через gTTS: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 60 + "\n")
        return None


def generate_order_speech(order_number):
    """
    Генерирует речь для объявления номера заказа
    
    Args:
        order_number: Номер заказа
    
    Returns:
        str: Путь к аудио файлу
    """
    text = f"Заказ номер {order_number}"
    # Используем правильное расширение в зависимости от TTS провайдера
    if Config.YANDEX_TTS_ENABLED:
        return generate_tts(text, output_path=f'static/audio/order_{order_number}.ogg')
    else:
        return generate_tts(text, output_path=f'static/audio/order_{order_number}.mp3')


def generate_item_speech(item_name, quantity, item_id):
    """
    Генерирует речь для объявления товара
    
    Args:
        item_name: Название товара
        quantity: Количество
        item_id: ID товара (для уникального имени файла)
    
    Returns:
        str: Путь к аудио файлу
    """
    # Формируем текст с количеством
    if quantity == 1:
        text = f"{item_name}"
    else:
        text = f"{item_name}, {quantity} штук"
    
    # Используем правильное расширение в зависимости от TTS провайдера
    if Config.YANDEX_TTS_ENABLED:
        return generate_tts(text, output_path=f'static/audio/item_{item_id}.ogg')
    else:
        return generate_tts(text, output_path=f'static/audio/item_{item_id}.mp3')


def prepare_items_for_assembly(items, filter_words):
    """
    Подготавливает список товаров для сборки с учетом фильтров
    
    Args:
        items: Список объектов OrderItem
        filter_words: Список объектов FilterWord
    
    Returns:
        list: Список словарей с информацией о товарах для озвучивания
    """
    prepared_items = []
    
    for item in items:
        should_announce = not should_filter_item(item.name, filter_words)
        
        prepared_items.append({
            'id': item.id,
            'row_number': item.row_number,
            'name': item.name,
            'quantity': item.quantity,
            'unit': item.unit,
            'status': item.status,
            'should_announce': should_announce,
            'filtered_reason': 'Содержит фильтруемое слово' if not should_announce else None
        })
    
    return prepared_items


# Функции для работы с Web Speech API будут использоваться на клиентской стороне
# Здесь мы только готовим данные для отправки на frontend



