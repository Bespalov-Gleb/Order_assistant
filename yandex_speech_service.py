"""
Yandex SpeechKit TTS сервис (синхронная версия)
Адаптировано из infrastructure/speech_internal_service.py
Использует API v3 для синтеза речи
"""
import base64
import json

import requests


class YandexSpeechService:
    def __init__(self, folder_id: str):
        self.folder_id = folder_id

    def synthesize(self, text: str, iam_token: str, voice: str = "jane", format: str = "OGG_OPUS") -> bytes | None:
        """
        Синтез речи через API v3 (синхронная версия)
        
        Args:
            text: Текст для синтеза
            iam_token: IAM токен для авторизации
            voice: Голос (jane, oksana, omazh, zahar, ermil)
            format: Формат аудио (OGG_OPUS, MP3, LINEAR16_PCM)
        
        Returns:
            bytes: Аудио данные или None в случае ошибки
        """
        print(f"🎤 [YANDEX TTS v3] Синтез речи: {text[:50]}...")
        
        try:
            hints = []
            if voice:
                hints.append({"voice": voice})
            
            url = "https://tts.api.cloud.yandex.net/tts/v3/utteranceSynthesis"
            
            headers = {
                "Authorization": f"Bearer {iam_token}",
                "Content-Type": "application/json",
                "x-folder-id": self.folder_id,
            }
            
            payload = {
                "text": text,
                "hints": hints,
                "outputAudioSpec": {
                    "containerAudio": {"containerAudioType": format.upper()}
                },
                "loudnessNormalizationType": "LUFS",
                "unsafeMode": True,
            }
            
            print(f"📡 [YANDEX TTS v3] Отправка запроса на {url}")
            print(f"   Headers: Authorization=Bearer {iam_token[:20]}..., x-folder-id={self.folder_id}")
            print(f"   Payload: text={text[:30]}..., voice={voice}, format={format}")
            
            response = requests.post(url, headers=headers, json=payload, timeout=30, stream=True)
            
            print(f"📥 [YANDEX TTS v3] Ответ: статус {response.status_code}")
            
            if response.status_code != 200:
                error_text = response.text
                print(f"❌ [YANDEX TTS v3] Ошибка синтеза: {error_text}")
                return None
            
            # API v3 возвращает поток JSON строк (NDJSON формат)
            # Каждая строка содержит чанк аудио в base64
            all_audio = bytearray()
            
            for line in response.iter_lines():
                if not line:
                    continue
                
                try:
                    line_str = line.decode('utf-8')
                    if not line_str.strip():
                        continue
                    
                    result = json.loads(line_str)
                    audio_data = result.get("result", {}).get("audioChunk", {}).get("data")
                    
                    if audio_data:
                        chunk = base64.b64decode(audio_data)
                        all_audio.extend(chunk)
                        
                except json.JSONDecodeError as e:
                    print(f"⚠️  [YANDEX TTS v3] Ошибка парсинга JSON строки: {e}")
                    continue
                except Exception as e:
                    print(f"⚠️  [YANDEX TTS v3] Ошибка обработки чанка: {e}")
                    continue
            
            if not all_audio:
                print("❌ [YANDEX TTS v3] Нет аудио данных в ответе")
                return None
            
            print(f"✅ [YANDEX TTS v3] Аудио синтезировано: {len(all_audio)} байт")
            return bytes(all_audio)
            
        except Exception as e:
            print(f"❌ [YANDEX TTS v3] Ошибка синтеза речи: {e}")
            import traceback
            traceback.print_exc()
            return None

