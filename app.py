import os
import logging
import traceback
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.utils import secure_filename
from config import Config
from models import db, Order, OrderItem, FilterWord
from excel_parser import parse_excel_file, validate_excel_file
from voice_handler import generate_item_speech, generate_order_speech, prepare_items_for_assembly

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Поддержка префикса URL (для развертывания на icesmoke.store/voice/)
app.config['APPLICATION_ROOT'] = os.environ.get('APP_PREFIX', '/')

# Инициализация базы данных
db.init_app(app)

# Создание директорий
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/audio', exist_ok=True)

# Создание таблиц БД при первом запуске
def init_database():
    """Инициализация базы данных"""
    with app.app_context():
        try:
            db.create_all()
            logger.info("✓ База данных инициализирована")
        except Exception as e:
            logger.error(f"✗ Ошибка при инициализации БД: {e}")
            logger.error(traceback.format_exc())

# Инициализируем БД при импорте модуля
init_database()


def allowed_file(filename):
    """Проверка разрешенного расширения файла"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    """Главная страница со списком заказов"""
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('index.html', orders=orders)


@app.route('/upload', methods=['POST'])
def upload_file():
    """Загрузка Excel файла заказа"""
    try:
        logger.info("Начало загрузки файла")
        
        if 'file' not in request.files:
            logger.warning("Файл не найден в запросе")
            flash('Файл не выбран', 'error')
            return redirect(url_for('index'))
        
        file = request.files['file']
        
        if file.filename == '':
            logger.warning("Имя файла пустое")
            flash('Файл не выбран', 'error')
            return redirect(url_for('index'))
        
        if not file or not allowed_file(file.filename):
            logger.warning(f"Недопустимый формат файла: {file.filename}")
            flash('Недопустимый формат файла. Разрешены только .xlsx файлы', 'error')
            return redirect(url_for('index'))
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        logger.info(f"Сохранение файла: {filepath}")
        file.save(filepath)
        
        # Валидация файла
        logger.info("Валидация файла")
        is_valid, error_message = validate_excel_file(filepath)
        if not is_valid:
            logger.error(f"Ошибка валидации: {error_message}")
            try:
                os.remove(filepath)
            except Exception as e:
                logger.warning(f"Не удалось удалить файл: {e}")
            flash(f'Ошибка в файле: {error_message}', 'error')
            return redirect(url_for('index'))
        
        # Парсинг файла
        logger.info("Парсинг файла")
        order = parse_excel_file(filepath, filename)
        logger.info(f"Заказ распарсен: {order.order_number}, товаров: {len(order.items)}")
        
        # Проверка на дублирование заказа
        existing_order = Order.query.filter_by(order_number=order.order_number).first()
        if existing_order:
            logger.warning(f"Заказ {order.order_number} уже существует")
            try:
                os.remove(filepath)
            except Exception as e:
                logger.warning(f"Не удалось удалить файл: {e}")
            flash(f'Заказ № {order.order_number} уже существует', 'warning')
            return redirect(url_for('index'))
        
        # Сохранение в БД
        logger.info("Сохранение в БД")
        db.session.add(order)
        db.session.commit()
        logger.info(f"Заказ {order.order_number} успешно сохранен")
        
        flash(f'Заказ № {order.order_number} успешно загружен ({len(order.items)} товаров)', 'success')
        return redirect(url_for('index'))
        
    except Exception as e:
        logger.error(f"КРИТИЧЕСКАЯ ОШИБКА при загрузке файла: {e}")
        logger.error(traceback.format_exc())
        
        # Пытаемся удалить файл если он был создан
        if 'filepath' in locals() and os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception as del_error:
                logger.warning(f"Не удалось удалить файл: {del_error}")
        
        # Откатываем транзакцию БД если она была начата
        try:
            db.session.rollback()
        except Exception as rollback_error:
            logger.warning(f"Ошибка при откате транзакции: {rollback_error}")
        
        flash(f'Ошибка при обработке файла: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/order/<int:order_id>')
def view_order(order_id):
    """Просмотр деталей заказа"""
    order = Order.query.get_or_404(order_id)
    return render_template('order_view.html', order=order)


@app.route('/order/<int:order_id>/assembly')
def order_assembly(order_id):
    """Страница сборки заказа"""
    order = Order.query.get_or_404(order_id)
    
    # Получаем фильтры слов
    filter_words = FilterWord.query.all()
    
    # Подготавливаем товары с учетом фильтров
    prepared_items = prepare_items_for_assembly(order.items, filter_words)
    
    return render_template('order_assembly.html', order=order, items=prepared_items)


@app.route('/api/order/<int:order_id>/item/<int:item_id>/status', methods=['POST'])
def update_item_status(order_id, item_id):
    """API для обновления статуса товара"""
    data = request.get_json()
    status = data.get('status')
    
    if status not in ['pending', 'completed', 'skipped']:
        return jsonify({'error': 'Недопустимый статус'}), 400
    
    item = OrderItem.query.filter_by(id=item_id, order_id=order_id).first_or_404()
    item.status = status
    db.session.commit()
    
    return jsonify({'success': True, 'status': status})


@app.route('/api/order/<int:order_id>/complete', methods=['POST'])
def complete_order(order_id):
    """API для завершения сборки заказа"""
    data = request.get_json()
    status = data.get('status', 'собран')
    
    if status not in ['собран', 'в_архив']:
        return jsonify({'error': 'Недопустимый статус'}), 400
    
    order = Order.query.get_or_404(order_id)
    order.status = status
    db.session.commit()
    
    return jsonify({'success': True, 'status': status})


@app.route('/api/order/<int:order_id>/delete', methods=['POST'])
def delete_order(order_id):
    """API для удаления заказа"""
    order = Order.query.get_or_404(order_id)
    
    # Удаляем файл
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], order.filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    
    db.session.delete(order)
    db.session.commit()
    
    return jsonify({'success': True})


@app.route('/settings')
def settings():
    """Страница настроек фильтров"""
    filter_words = FilterWord.query.order_by(FilterWord.created_at.desc()).all()
    return render_template('settings.html', filter_words=filter_words)


@app.route('/api/filter/add', methods=['POST'])
def add_filter():
    """API для добавления фильтра слов"""
    data = request.get_json()
    word = data.get('word', '').strip()
    
    if not word:
        return jsonify({'error': 'Слово не может быть пустым'}), 400
    
    # Проверка на дублирование
    existing = FilterWord.query.filter_by(word=word).first()
    if existing:
        return jsonify({'error': 'Это слово уже в списке фильтров'}), 400
    
    filter_word = FilterWord(word=word)
    db.session.add(filter_word)
    db.session.commit()
    
    return jsonify({'success': True, 'filter': filter_word.to_dict()})


@app.route('/api/filter/<int:filter_id>', methods=['DELETE'])
def delete_filter(filter_id):
    """API для удаления фильтра"""
    filter_word = FilterWord.query.get_or_404(filter_id)
    db.session.delete(filter_word)
    db.session.commit()
    
    return jsonify({'success': True})


@app.route('/api/tts/item/<int:item_id>')
def generate_item_tts(item_id):
    """API для генерации TTS для товара"""
    item = OrderItem.query.get_or_404(item_id)
    
    audio_path = generate_item_speech(item.name, item.quantity, item.id)
    
    if audio_path:
        # Возвращаем относительный путь для frontend
        return jsonify({'success': True, 'audio_url': '/' + audio_path})
    else:
        return jsonify({'error': 'Ошибка генерации аудио'}), 500


@app.route('/api/tts/order/<int:order_id>')
def generate_order_tts(order_id):
    """API для генерации TTS для номера заказа"""
    order = Order.query.get_or_404(order_id)
    
    audio_path = generate_order_speech(order.order_number)
    
    if audio_path:
        return jsonify({'success': True, 'audio_url': '/' + audio_path})
    else:
        return jsonify({'error': 'Ошибка генерации аудио'}), 500


def check_tts_config():
    """Проверка конфигурации TTS при старте приложения"""
    from config import Config
    print("\n" + "=" * 60)
    print("🚀 Инициализация Order Assistant")
    print("=" * 60)
    
    print("🔧 Проверка настроек TTS:")
    print(f"   YANDEX_TTS_ENABLED: {Config.YANDEX_TTS_ENABLED} (тип: {type(Config.YANDEX_TTS_ENABLED)})")
    print(f"   YANDEX_TTS_API_KEY: {'✅ Установлен' if Config.YANDEX_TTS_API_KEY else '❌ НЕ УСТАНОВЛЕН'}")
    if Config.YANDEX_TTS_API_KEY:
        print(f"      (первые 10 символов: {Config.YANDEX_TTS_API_KEY[:10]}...)")
    print(f"   YANDEX_TTS_FOLDER_ID: {'✅ Установлен' if Config.YANDEX_TTS_FOLDER_ID else '❌ НЕ УСТАНОВЛЕН'}")
    if Config.YANDEX_TTS_FOLDER_ID:
        print(f"      (значение: {Config.YANDEX_TTS_FOLDER_ID})")
    print(f"   YANDEX_TTS_VOICE: {Config.YANDEX_TTS_VOICE}")
    
    if Config.YANDEX_TTS_ENABLED and Config.YANDEX_TTS_API_KEY:
        print("✅ Yandex TTS настроен и будет использоваться")
        if not Config.YANDEX_TTS_FOLDER_ID:
            print("   ⚠️  FOLDER_ID не указан - будет использован каталог сервисного аккаунта")
    else:
        print("ℹ️  Будет использоваться Google TTS (gTTS)")
    
    print("=" * 60 + "\n")


if __name__ == '__main__':
    # Проверяем конфигурацию TTS перед запуском сервера
    check_tts_config()
    app.run(debug=True, host='0.0.0.0', port=5000)



