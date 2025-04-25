#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# --- Параметры (настройте под себя) ---
REMOTE_USER="deployuser"
REMOTE_HOST="example.com"
REMOTE_PORT=22
REMOTE_PATH="/home/${REMOTE_USER}/car_park"
GIT_BRANCH="main"
GIT_REPO="git@github.com:cyrilliusg/CarPark.git"
LOCAL_ENV_FILE=".env"
COMPOSE_PROJECT="carpark"
SSH_OPTS="-p ${REMOTE_PORT} -o BatchMode=yes -o ConnectTimeout=10"

echo "==> Проверяем локальный .env"
[ -f "${LOCAL_ENV_FILE}" ] || { echo "Ошибка: ${LOCAL_ENV_FILE} не найден"; exit 1; }

# Создаём директорию на сервере, если её нет, и чистим временный env
ssh ${SSH_OPTS} "${REMOTE_USER}@${REMOTE_HOST}" bash <<'EOSSH'
set -euo pipefail
REMOTE_PATH="/home/deployuser/car_park"
mkdir -p "${REMOTE_PATH}"
rm -f "${REMOTE_PATH}/.env.tmp"
EOSSH

echo "==> Копируем .env → ${REMOTE_HOST}:${REMOTE_PATH}/.env.tmp"
scp -P "${REMOTE_PORT}" "${LOCAL_ENV_FILE}" \
    "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}/.env.tmp"

# Основной блок на сервере
ssh ${SSH_OPTS} "${REMOTE_USER}@${REMOTE_HOST}" bash <<'EOSSH'
set -euo pipefail
IFS=$'\n\t'
REMOTE_PATH="/home/deployuser/car_park"
GIT_BRANCH="main"
GIT_REPO="git@github.com:cyrilliusg/CarPark.git"
COMPOSE_PROJECT="carpark"

# Проверяем зависимости
for cmd in git docker docker-compose; do
  command -v "$cmd" >/dev/null 2>&1 || { echo "Ошибка: $cmd не установлен"; exit 1; }
done

cd "${REMOTE_PATH}"

# Клонируем или убеждаемся, что это нужный репозиторий
if [ ! -d ".git" ]; then
  echo "==> Репозиторий не найден, клонируем"
  rm -rf ./*
  git clone -b "${GIT_BRANCH}" "${GIT_REPO}" .
elif ! git config --get remote.origin.url | grep -q "${GIT_REPO}"; then
  echo "Ошибка: удалённый репозиторий не совпадает"
  exit 1
fi

# Обновляем код
git fetch origin "${GIT_BRANCH}"
git reset --hard "origin/${GIT_BRANCH}"

# Обновляем .env
if mv .env.tmp .env; then
  echo "==> .env обновлён"
else
  echo "==> .env.tmp не найден, оставляем старый .env"
fi

# Останавливаем, удаляем контейнеры
echo "==> Останавливаем контейнеры"
docker-compose -p "${COMPOSE_PROJECT}" down --remove-orphans

# Тянем образы и билдим
echo "==> Обновляем образы и билдим"
docker-compose -p "${COMPOSE_PROJECT}" pull --ignore-pull-failures
docker-compose -p "${COMPOSE_PROJECT}" up -d --build

# Миграции и статика (Django)
echo "==> Запускаем миграции и сбор статики"
docker-compose -p "${COMPOSE_PROJECT}" run --rm web python manage.py migrate --noinput
docker-compose -p "${COMPOSE_PROJECT}" run --rm web python manage.py collectstatic --noinput

# Чистка dangling-ресурсов
echo "==> Чистим dangling images/containers"
docker image prune -f
docker container prune -f

echo "==> Деплой завершён успешно!"
EOSSH
