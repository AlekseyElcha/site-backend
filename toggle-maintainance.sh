#!/bin/bash

NGINX_CONTAINER="site-backend-frontend-1"
MAINTENANCE_FILE="/etc/nginx/maintenance.enable"
MAINTENANCE_HTML="/var/www/maintenance.html"

if ! docker ps --format '{{.Names}}' | grep -q "^${NGINX_CONTAINER}$"; then
    echo "Контейнер ${NGINX_CONTAINER} не запущен!"
    echo "Запущенные контейнеры:"
    docker ps --format 'table {{.Names}}\t{{.Status}}'
    exit 1
fi

case "$1" in
    on)
        echo "Включаем режим обслуживания..."
        docker exec $NGINX_CONTAINER touch $MAINTENANCE_FILE
        docker exec $NGINX_CONTAINER nginx -s reload
        echo "Режим обслуживания включен для ask.domofon-servis-odi.ru"
        ;;
    off)
        echo "Выключаем режим обслуживания..."
        docker exec $NGINX_CONTAINER rm -f $MAINTENANCE_FILE
        docker exec $NGINX_CONTAINER nginx -s reload
        echo "Режим обслуживания выключен"
        ;;
    status)
        if docker exec $NGINX_CONTAINER test -f $MAINTENANCE_FILE 2>/dev/null; then
            echo "Режим обслуживания: ВКЛЮЧЕН"
        else
            echo "Режим обслуживания: ВЫКЛЮЧЕН"
        fi
        ;;
    *)
        echo "Использование: $0 {on|off|status}"
        echo ""
        echo "Команды:"
        echo "  on     - Включить режим обслуживания"
        echo "  off    - Выключить режим обслуживания"
        echo "  status - Проверить статус"
        exit 1
        ;;
esac