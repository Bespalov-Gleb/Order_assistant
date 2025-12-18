"""
Скрипт для инициализации базы данных
"""
from app import app, db
from models import Order, OrderItem, FilterWord

def init_database():
    """Создает таблицы в базе данных"""
    with app.app_context():
        # Создаем все таблицы
        db.create_all()
        print("✓ Таблицы базы данных созданы успешно")
        
        # Добавляем примеры фильтров (опционально)
        default_filters = [
            "Табак",
            "Табак для кальяна",
            "Undercoal",
            "Бестабачная смесь для нагревания"
        ]
        
        for word in default_filters:
            existing = FilterWord.query.filter_by(word=word).first()
            if not existing:
                filter_word = FilterWord(word=word)
                db.session.add(filter_word)
        
        db.session.commit()
        print(f"✓ Добавлено {len(default_filters)} фильтров по умолчанию")
        
        print("\n✓ Инициализация базы данных завершена!")
        print("Теперь вы можете запустить приложение командой: python app.py")

if __name__ == '__main__':
    init_database()



