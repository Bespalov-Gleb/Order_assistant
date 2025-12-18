#!/bin/bash
# Простая установка Python через pyenv (если доступен) или Miniconda

set -e

echo "==================================================="
echo "  Установка Python (простой способ)"
echo "==================================================="
echo ""

HOME_DIR="$HOME"

# Вариант 1: Проверка, есть ли уже Python где-то
echo "🔍 Проверка существующего Python..."
if command -v python3 &> /dev/null; then
    echo "✅ Python3 уже установлен: $(python3 --version)"
    python3 --version
    exit 0
fi

# Вариант 2: Установка Miniconda (самый простой способ)
echo ""
echo "📥 Установка Miniconda (легковесная версия Anaconda)..."
echo ""

CONDA_DIR="$HOME_DIR/miniconda3"

if [ ! -d "$CONDA_DIR" ]; then
    # Скачиваем Miniconda
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
    
    # Устанавливаем
    bash miniconda.sh -b -p "$CONDA_DIR"
    
    # Инициализируем
    "$CONDA_DIR/bin/conda" init bash
    
    echo ""
    echo "✅ Miniconda установлена!"
    echo ""
    echo "Добавьте в ~/.bashrc:"
    echo "  export PATH=\"$CONDA_DIR/bin:\$PATH\""
    echo ""
    echo "Или используйте:"
    echo "  $CONDA_DIR/bin/python3 --version"
else
    echo "✅ Miniconda уже установлена в $CONDA_DIR"
fi

echo ""
echo "📦 Установка pip пакетов через conda..."
"$CONDA_DIR/bin/conda" install -y pip

echo ""
echo "==================================================="
echo "  ✅ Готово!"
echo "==================================================="
echo ""
echo "Используйте:"
echo "  $CONDA_DIR/bin/python3"
echo "  $CONDA_DIR/bin/pip3"
echo ""

