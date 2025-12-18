# Как проверить доступ к Nginx

## Способ 1: Через веб-консоль (если есть)

### Шаг 1: Проверьте наличие файлов конфигурации Nginx

В веб-консоли выполните:

```bash
# Проверка наличия конфигурации Nginx
ls -la /etc/nginx/
ls -la /etc/nginx/sites-available/
ls -la /etc/nginx/sites-enabled/
ls -la /etc/nginx/conf.d/
```

**Если команды работают** → ✅ Есть доступ к конфигурации Nginx

**Если "Permission denied"** → ❌ Нет доступа (shared hosting)

### Шаг 2: Проверьте конфигурацию домена icesmoke.store

```bash
# Поиск конфигурации для icesmoke.store
grep -r "icesmoke.store" /etc/nginx/
# или
find /etc/nginx/ -name "*icesmoke*"
# или
cat /etc/nginx/sites-enabled/icesmoke.store
```

**Если нашли файл конфигурации** → ✅ Можно редактировать

### Шаг 3: Проверьте тип веб-сервера

```bash
# Проверка, какой веб-сервер используется
ps aux | grep nginx
ps aux | grep apache
ps aux | grep httpd

# Или проверка через systemctl
systemctl status nginx
systemctl status apache2
```

---

## Способ 2: Через панель управления хостингом

### Если это ISPmanager:

1. Зайдите в панель управления
2. Найдите раздел **"Веб-серверы"** или **"Nginx"**
3. Если есть возможность редактировать конфигурацию → ✅ Есть доступ

### Если это cPanel:

1. Зайдите в **"Apache Configuration"** или **"Nginx Configuration"**
2. Если есть раздел для редактирования → ✅ Есть доступ

---

## Способ 3: Проверка через файлы на сервере

### Проверьте наличие `.htaccess` (Apache)

```bash
# Если в www/ есть .htaccess файлы
ls -la ~/www/.htaccess
ls -la ~/www/*/.htaccess
```

**Если есть `.htaccess`** → Возможно Apache, можно настроить через `.htaccess`

### Проверьте структуру www/

```bash
# Что находится в www/
ls -la ~/www/
ls -la ~/www/icesmoke.store/  # если есть подпапка для домена
```

---

## Способ 4: Проверка через HTTP заголовки

В браузере откройте `icesmoke.store` и проверьте заголовки ответа:

1. **F12** → вкладка **Network**
2. Обновите страницу
3. Посмотрите заголовок **Server**:
   - `Server: nginx/...` → Nginx
   - `Server: Apache/...` → Apache

---

## Что делать дальше:

### ✅ Если есть доступ к Nginx:

1. Найдите конфигурацию `icesmoke.store`
2. Добавьте блок `location /voice/` (см. `nginx_config_example.conf`)
3. Перезагрузите Nginx: `sudo systemctl reload nginx`

### ✅ Если есть только Apache + `.htaccess`:

Можно настроить через `.htaccess`, но для Flask нужен прокси, что сложнее.

### ❌ Если нет доступа:

Рассмотрите вариант с поддоменом `voice.icesmoke.store`

---

## Быстрая проверка (одна команда):

```bash
# Проверка всего сразу
echo "=== Nginx ===" && \
ls -la /etc/nginx/ 2>/dev/null && echo "✅ Nginx доступен" || echo "❌ Nginx недоступен" && \
echo "" && \
echo "=== Apache ===" && \
ls -la /etc/apache2/ 2>/dev/null && echo "✅ Apache доступен" || echo "❌ Apache недоступен" && \
echo "" && \
echo "=== Веб-сервер процесс ===" && \
ps aux | grep -E "nginx|apache|httpd" | grep -v grep
```

