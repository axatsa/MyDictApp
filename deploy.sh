#!/bin/bash
set -e
echo '🚀 Начинаем деплой MyDict'

PROJECT_DIR="/home/temp/MyDictApp"

if [ -d "$PROJECT_DIR" ]; then
    cd "$PROJECT_DIR"
else
    echo "❌ Ошибка: Папка $PROJECT_DIR не найдена!"
    exit 1
fi

# 1. Проверяем .env
if [ ! -f ".env" ]; then
    echo "❌ Файл .env не найден! Скопируй .env.example → .env и заполни значения."
    exit 1
fi

# 2. Принудительное обновление кода
echo '🔄 Принудительная загрузка кода из GitHub...'
git fetch origin main
git reset --hard origin/main

# 3. Определяем команду docker compose
if docker compose version >/dev/null 2>&1; then
    DOCKER_CMD="docker compose"
elif docker-compose version >/dev/null 2>&1; then
    DOCKER_CMD="docker-compose"
else
    echo "❌ Ошибка: Docker Compose не найден!"
    exit 1
fi
echo "🛠️ Используем команду: $DOCKER_CMD"

# 4. Проверяем GEMINI_API_KEY
source .env 2>/dev/null || true
if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ GEMINI_API_KEY не задан в .env!"
    exit 1
fi
echo "✅ Gemini API key найден"

# 5. Проверяем внешнюю сеть Traefik
if ! docker network inspect web >/dev/null 2>&1; then
    echo "🌐 Создаём внешнюю сеть 'web' для Traefik..."
    docker network create web
fi

# 6. Остановка и удаление старых контейнеров
echo '🧹 Очистка старых контейнеров...'
$DOCKER_CMD -f docker-compose.prod.yml down --remove-orphans
docker rm -f mydict_backend mydict_frontend 2>/dev/null || true

# 7. Сборка и запуск
echo '🔨 Пересборка и запуск контейнеров...'
$DOCKER_CMD -f docker-compose.prod.yml up -d --build --force-recreate

# 8. Ожидание готовности backend
echo '⏳ Ожидание готовности backend...'
MAX_WAIT=60
WAITED=0
until curl -s http://localhost:8000/api/stats >/dev/null 2>&1 || \
      docker exec mydict_backend curl -s http://localhost:8000/api/stats >/dev/null 2>&1; do
    if [ $WAITED -ge $MAX_WAIT ]; then
        echo "⚠️  Backend не ответил за ${MAX_WAIT}с, но продолжаем..."
        break
    fi
    sleep 2
    WAITED=$((WAITED + 2))
    echo "   ...ждём backend (${WAITED}с)"
done

# 9. Сидируем начальные слова (если база пустая)
echo '🌱 Проверяем базу данных...'
docker exec mydict_backend python seed.py || echo "⚠️  Сид пропущен (возможно, слова уже есть)"

echo ''
echo '✅ Деплой успешно завершен!'
echo '🌐 Проект доступен по адресу: https://mydict.classplay.uz'
echo ''
echo 'Полезные команды:'
echo '  docker logs mydict_backend -f    # логи backend'
echo '  docker logs mydict_frontend -f   # логи frontend'
