#!/bin/bash
# Установка Python и настройка окружения

# 1. Создание рабочей директории
mkdir -p ~/order-assistant
cd ~/order-assistant

# 2. Установка Miniconda (если еще не установлена)
if [ ! -d "$HOME/miniconda3" ]; then
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
    bash Miniconda3-latest-Linux-x86_64.sh -b -p ~/miniconda3
    rm Miniconda3-latest-Linux-x86_64.sh
fi

# 3. Добавление в PATH
export PATH="$HOME/miniconda3/bin:$PATH"

# 4. Создание venv
~/miniconda3/bin/python3 -m venv venv

# 5. Активация venv
source venv/bin/activate

# 6. Обновление pip
pip install --upgrade pip

echo "✅ Готово! Python установлен, venv создан и активирован"
echo "Используйте: source venv/bin/activate"

