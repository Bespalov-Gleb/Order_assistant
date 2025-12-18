#!/bin/bash
# Скрипт для развертывания на icesmoke.store/voice/

echo "==================================================="
echo "  Развертывание Order Assistant на icesmoke.store"
echo "==================================================="
echo ""

# 1. Установка зависимостей
echo "1. Установка зависимостей..."
pip3 install -r requirements.txt
pip3 install gunicorn

# 2. Создание .env файла
if [ ! -f .env ]; then
    echo "2. Создание .env файла..."
    cp production.env.example .env
    echo "   ⚠️  ВАЖНО: Отредактируйте .env и укажите правильные параметры!"
    read -p "   Нажмите Enter после редактирования .env..."
else
    echo "2. .env файл уже существует"
fi

# 3. Создание базы данных
echo "3. Создание базы данных..."
python3 create_db_direct.py

# 4. Инициализация таблиц
echo "4. Инициализация таблиц..."
python3 init_db.py

# 5. Создание systemd service
echo "5. Создание systemd service..."
sudo tee /etc/systemd/system/order-assistant.service > /dev/null <<EOF
[Unit]
Description=Order Assistant Flask Application
After=network.target postgresql.service

[Service]
User=$USER
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/venv/bin"
ExecStart=$(pwd)/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 6. Запуск сервиса
echo "6. Запуск сервиса..."
sudo systemctl daemon-reload
sudo systemctl enable order-assistant
sudo systemctl start order-assistant

echo ""
echo "==================================================="
echo "  ✓ Развертывание завершено!"
echo "==================================================="
echo ""
echo "Добавьте в Nginx конфигурацию icesmoke.store:"
echo "  см. nginx_config_example.conf"
echo ""
echo "Затем перезагрузите Nginx:"
echo "  sudo systemctl reload nginx"
echo ""
echo "Проверка статуса:"
echo "  sudo systemctl status order-assistant"
echo ""

