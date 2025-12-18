#!/bin/bash
# Установка Python локально в домашнюю директорию (для shared hosting)

set -e

echo "==================================================="
echo "  Установка Python локально"
echo "==================================================="
echo ""

# Проверка текущей директории
HOME_DIR="$HOME"
PYTHON_DIR="$HOME_DIR/python"
PYTHON_VERSION="3.11.7"

echo "📁 Домашняя директория: $HOME_DIR"
echo "📁 Python будет установлен в: $PYTHON_DIR"
echo ""

# Создаем директорию для Python
mkdir -p "$PYTHON_DIR"
cd "$PYTHON_DIR"

echo "📥 Скачивание Python $PYTHON_VERSION..."
echo ""

# Скачиваем исходники Python
if [ ! -f "Python-$PYTHON_VERSION.tgz" ]; then
    wget https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz
else
    echo "✅ Файл уже скачан"
fi

echo "📦 Распаковка..."
tar -xzf Python-$PYTHON_VERSION.tgz
cd Python-$PYTHON_VERSION

echo "⚙️  Конфигурация (это может занять время)..."
./configure --prefix="$PYTHON_DIR" --enable-optimizations

echo "🔨 Компиляция (это займет 10-20 минут)..."
make -j$(nproc 2>/dev/null || echo 2)

echo "📦 Установка..."
make install

echo ""
echo "==================================================="
echo "  ✅ Python установлен!"
echo "==================================================="
echo ""
echo "Добавьте в ~/.bashrc или ~/.profile:"
echo "  export PATH=\"$PYTHON_DIR/bin:\$PATH\""
echo ""
echo "Или используйте напрямую:"
echo "  $PYTHON_DIR/bin/python3 --version"
echo ""

