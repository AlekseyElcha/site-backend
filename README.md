Платформа по приёму обращений абонентов.

Проект находится в активной разработке.

---

## 🚀 Быстрый старт

### Для обновления кода на сервере (НОВОЕ!):

**📖 [БЫСТРОЕ_ОБНОВЛЕНИЕ.md](БЫСТРОЕ_ОБНОВЛЕНИЕ.md)** - исправление 504 ошибки

**Windows:**
```powershell
.\update_server.ps1
```

**Linux/Mac:**
```bash
chmod +x update_server.sh
./update_server.sh
```

---

### Для полного деплоя приложения:

**📖 [НАЧНИТЕ ОТСЮДА → START_HERE.md](START_HERE.md)**

Или используйте автоматический скрипт:

**Windows:**
```powershell
.\redeploy.ps1
```

**Linux/Mac:**
```bash
chmod +x redeploy.sh
./redeploy.sh
```

---

## 📚 Документация

### Основные документы:
- **[START_HERE.md](START_HERE.md)** ⭐ - начните с этого файла!
- **[КРАТКАЯ_ИНСТРУКЦИЯ.md](КРАТКАЯ_ИНСТРУКЦИЯ.md)** - быстрая инструкция на русском
- **[DEPLOY_README.md](DEPLOY_README.md)** - полная инструкция по деплою

### Техническая документация:
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - архитектура приложения
- **[SUMMARY_FIXES.md](SUMMARY_FIXES.md)** - резюме исправлений
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - решение проблем

### Справочники:
- **[COMMANDS_CHEATSHEET.md](COMMANDS_CHEATSHEET.md)** - шпаргалка команд Docker
- **[CHECKLIST.md](CHECKLIST.md)** - чеклист для деплоя

### Скрипты:
- `redeploy.sh` / `redeploy.ps1` - автоматический перезапуск
- `diagnose.sh` / `diagnose.ps1` - диагностика проблем

---

## 🏗️ Архитектура

```
Frontend (React + Vite) → Nginx → FastAPI Backend → PostgreSQL + Redis
                                                   ↓
                                                  S3 Storage
```

Подробнее в [ARCHITECTURE.md](ARCHITECTURE.md)

---

## 🔧 Разработка

### Требования:
- Docker & Docker Compose
- Python 3.14
- Node.js 20+

### Локальный запуск:
```bash
# 1. Скопировать .env_template в .env и заполнить
cp .env_template .env

# 2. Запустить все сервисы
docker-compose up -d

# 3. Проверить статус
docker-compose ps
```

### Полезные команды:
```bash
# Логи
docker-compose logs -f

# Перезапуск
docker-compose restart

# Остановка
docker-compose down
```

Больше команд в [COMMANDS_CHEATSHEET.md](COMMANDS_CHEATSHEET.md)

---

## 🐛 Проблемы?

1. Запустите диагностику: `./diagnose.sh` или `.\diagnose.ps1`
2. Проверьте [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
3. Посмотрите логи: `docker-compose logs -f`

---

## 📝 API Endpoints

- `/auth/*` - авторизация
- `/questions/*` - работа с вопросами
- `/handle_questions/*` - обработка вопросов
- `/files/*` - работа с файлами

---

## 🔐 Переменные окружения

Скопируйте `.env_template` в `.env` и заполните:

```bash
MAIL_SERVICE_SECRET=...
MAIL_FROM_ADDRESS=...
KEY_ID=...
SECRET=...
ENDPOINT=...
CONTAINER=...
```

---

## 📦 Технологии

**Backend:**
- Python 3.14
- FastAPI
- SQLAlchemy
- PostgreSQL
- Redis
- Alembic

**Frontend:**
- React
- TypeScript
- Vite

**Infrastructure:**
- Docker
- Docker Compose
- Nginx
- S3 Storage

---

## 📄 Лицензия

Проект находится в активной разработке.
