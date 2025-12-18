from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Order(db.Model):
    """Модель заказа"""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(100), nullable=False, unique=True)
    order_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='новый')  # новый, собран, в_архив
    filename = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Order {self.order_number}>'
    
    def to_dict(self):
        """Преобразование в словарь для JSON"""
        return {
            'id': self.id,
            'order_number': self.order_number,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'status': self.status,
            'filename': self.filename,
            'created_at': self.created_at.isoformat(),
            'items_count': len(self.items)
        }


class OrderItem(db.Model):
    """Модель товара в заказе"""
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    row_number = db.Column(db.Integer, nullable=False)  # Номер строки в заказе
    name = db.Column(db.String(500), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String(50), default='шт')
    code = db.Column(db.String(100))  # Код товара (если есть)
    status = db.Column(db.String(50), nullable=False, default='pending')  # pending, completed, skipped
    
    def __repr__(self):
        return f'<OrderItem {self.name} x{self.quantity}>'
    
    def to_dict(self):
        """Преобразование в словарь для JSON"""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'row_number': self.row_number,
            'name': self.name,
            'quantity': self.quantity,
            'unit': self.unit,
            'code': self.code,
            'status': self.status
        }


class FilterWord(db.Model):
    """Модель фильтра слов для пропуска при озвучивании"""
    __tablename__ = 'filter_words'
    
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(200), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<FilterWord {self.word}>'
    
    def to_dict(self):
        """Преобразование в словарь для JSON"""
        return {
            'id': self.id,
            'word': self.word,
            'created_at': self.created_at.isoformat()
        }



