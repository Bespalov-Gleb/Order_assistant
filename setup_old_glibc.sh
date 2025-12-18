#!/bin/bash
# Установка для старого GLIBC (2.17)

# 1. Создание рабочей директории
mkdir -p ~/order-assistant
cd ~/order-assistant

# 2. Установка старой версии Miniconda (для GLIBC 2.17)
if [ ! -d "$HOME/miniconda3" ]; then
    # Старая версия Miniconda, совместимая с GLIBC 2.17
    wget https://repo.anaconda.com/miniconda/Miniconda3-py39_4.12.0-Linux-x86_64.sh
    bash Miniconda3-py39_4.12.0-Linux-x86_64.sh -b -p ~/miniconda3
    rm Miniconda3-py39_4.12.0-Linux-x86_64.sh
fi

# 3. Добавление в PATH
export PATH="$HOME/miniconda3/bin:$PATH"

# 4. Создание venv
~/miniconda3/bin/python3 -m venv venv

# 5. Активация venv
source venv/bin/activate

echo "✅ Готово!"

