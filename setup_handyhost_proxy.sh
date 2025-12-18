#!/bin/bash
# Настройка проксирования с HandyHost на Timeweb

# 1. Создание папки для автоподдомена
mkdir -p ~/www/voice.icesmoke.store
cd ~/www/voice.icesmoke.store

# 2. Создание .htaccess для проксирования (если Apache)
cat > .htaccess << 'EOF'
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ https://your-app.timeweb.cloud/$1 [P,L]

# Проксирование заголовков
ProxyPreserveHost On
ProxyPassReverse / https://your-app.timeweb.cloud/
EOF

# 3. Или создание index.php для редиректа (если .htaccess не работает)
cat > index.php << 'EOF'
<?php
header('Location: https://your-app.timeweb.cloud' . $_SERVER['REQUEST_URI']);
exit;
?>
EOF

echo "✅ Папка создана"
echo "⚠️  Замените 'your-app.timeweb.cloud' на реальный URL вашего приложения на Timeweb"

