#!/bin/bash
# Проверка существующего Python на сервере

echo "Проверка Python..."

# Проверка разных путей
PATHS=(
    "/usr/bin/python3"
    "/usr/bin/python"
    "/usr/local/bin/python3"
    "/usr/local/bin/python"
    "/opt/python3/bin/python3"
    "$HOME/.local/bin/python3"
)

for path in "${PATHS[@]}"; do
    if [ -f "$path" ]; then
        echo "✅ Найден: $path"
        $path --version
    fi
done

# Проверка через which
echo ""
echo "Поиск через which:"
which python3 2>/dev/null && python3 --version || echo "python3 не найден"
which python 2>/dev/null && python --version || echo "python не найден"

# Проверка через find
echo ""
echo "Поиск Python в системе:"
find /usr -name "python3*" -type f 2>/dev/null | head -5

