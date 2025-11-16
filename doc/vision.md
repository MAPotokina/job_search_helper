# Technical Vision - Job Search Helper

## 1. Технологии

### Backend
- **Python 3.10+** - основной язык разработки
- **FastAPI** - веб-фреймворк (быстрый, простой, автодокументация)
- **SQLite** - встроенная база данных (нулевая настройка)
- **Pydantic** - валидация данных (встроено в FastAPI)

### Frontend
- **HTML + Vanilla JavaScript + CSS** - минимальный стек без фреймворков
- Никаких сборщиков (webpack, vite) на старте

### LLM Integration
- **OpenAI API** (GPT-3.5-turbo для начала) - анализ вакансий и помощь с cover letters
- **openai** (официальная Python библиотека)

### Дополнительные библиотеки
- **SQLAlchemy** - ORM для работы с базой данных
- **python-dotenv** - управление переменными окружения
- **uvicorn** - ASGI сервер для FastAPI

### Инструменты разработки
- **venv** - виртуальное окружение (уже настроено)
- **requirements.txt** - управление зависимостями

## 2. Принципы разработки

### Философия
- **KISS (Keep It Simple, Stupid)** - максимальная простота во всём
- **MVP-first** - работающий прототип важнее идеального кода
- **Монолитная архитектура** - всё в одном приложении
- **No premature optimization** - оптимизируем только реальные проблемы

### Технические решения
- **Single-user приложение** - без системы аутентификации на MVP
- **Синхронный код** - async только в FastAPI endpoints где необходимо
- **ORM (SQLAlchemy)** - для удобной работы с БД, но без сложных связей
- **Минимальная валидация** - только критичные проверки через Pydantic
- **Прямолинейная структура** - простые модули, минимум абстракций

### Что НЕ делаем на MVP
- ❌ Система аутентификации и авторизации
- ❌ Модульные тесты (добавим позже)
- ❌ CI/CD пайплайны
- ❌ Docker и контейнеризация
- ❌ Микросервисная архитектура
- ❌ Кэширование
- ❌ Асинхронная обработка задач (Celery и т.п.)

## 3. Структура проекта

```
JobSearchHelper/
├── app/
│   ├── main.py              # FastAPI приложение, точка входа
│   ├── database.py          # Настройка БД и SQLAlchemy
│   ├── models.py            # SQLAlchemy модели (таблицы)
│   ├── schemas.py           # Pydantic схемы для API
│   ├── llm.py               # Работа с OpenAI API
│   └── static/              # Статические файлы для фронтенда
│       ├── index.html       # Главная страница
│       ├── style.css        # Стили
│       └── app.js           # Логика фронтенда
├── templates/
│   └── cover_letter_base.txt  # Базовый шаблон cover letter пользователя
├── data/
│   └── jobs.db              # SQLite база (создаётся автоматически)
├── .env                     # Переменные окружения (OPENAI_API_KEY)
├── .env.example             # Пример .env файла
├── .gitignore               # Исключения для git
├── requirements.txt         # Зависимости Python
├── idea.md                  # Описание идеи проекта
└── vision.md                # Технический дизайн (этот документ)
```

### Принципы структуры
- **Плоская организация** - все модули на одном уровне в папке `app/`
- **Один файл = одна ответственность** - database, models, llm, schemas раздельно
- **Минимум вложенности** - никаких подпакетов типа `routers/`, `services/`, `utils/`
- **Логи в консоль** - без файлов логов на MVP

## 4. Архитектура проекта

### Общая схема (3-tier architecture)

```
┌─────────────────────────────────────┐
│   Frontend (HTML/JS/CSS)            │  ← Браузер пользователя
│   - Форма добавления вакансии       │
│   - Список вакансий                 │
│   - Генерация cover letter          │
└──────────────┬──────────────────────┘
               │ HTTP/JSON (REST API)
┌──────────────▼──────────────────────┐
│   FastAPI Application (main.py)     │
│   - REST endpoints (CRUD)           │
│   - Валидация (Pydantic schemas)    │
│   - Статическая раздача файлов      │
└──────┬────────────────────┬─────────┘
       │                    │
       │                    └──────────┐
       │                               │
┌──────▼──────────┐          ┌─────────▼────────┐
│  SQLAlchemy ORM │          │  LLM Service     │
│  (models.py)    │          │  (llm.py)        │
│  - Job model    │          │  - Sponsorship   │
│  - CRUD ops     │          │  - Cover letter  │
└──────┬──────────┘          └─────────┬────────┘
       │                               │
┌──────▼──────────┐          ┌─────────▼────────┐
│  SQLite DB      │          │  OpenAI API      │
│  (jobs.db)      │          │  (GPT-3.5)       │
└─────────────────┘          └──────────────────┘
```

### API Endpoints

**Статические файлы:**
- `GET /` - главная страница (index.html)

**Job Management:**
- `GET /api/jobs` - получить все вакансии
- `POST /api/jobs` - добавить новую вакансию
- `GET /api/jobs/{id}` - получить вакансию по ID
- `PUT /api/jobs/{id}` - обновить вакансию (включая статус)
- `DELETE /api/jobs/{id}` - удалить вакансию

**LLM Features:**
- `POST /api/extract-job-info` - извлечение названия и компании из описания (автоматически)
- `POST /api/analyze-sponsorship` - анализ текста вакансии на visa sponsorship
- `POST /api/analyze-match` - анализ соответствия резюме вакансии
- `POST /api/generate-cover-letter` - генерация персонализированного cover letter

### Ключевые решения
- **Монолит** - всё в одном FastAPI приложении
- **REST API** - стандартные HTTP методы и JSON
- **Синхронные вызовы LLM** - пользователь ждёт ответа
- **Хранение cover letters в БД** - для истории и повторного использования
- **Без middleware** - минимальная обработка запросов
- **Без роутеров** - все endpoints в main.py

## 5. Модель данных

### Таблица: `jobs`

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | Integer (PK) | Уникальный идентификатор |
| `title` | String(200) | Название позиции |
| `company` | String(200) | Название компании |
| `job_url` | String(500) | Ссылка на вакансию |
| `job_description` | Text | Полное описание вакансии |
| `has_visa_sponsorship` | Boolean (nullable) | Есть ли sponsorship (null/true/false) |
| `sponsorship_analysis` | Text (nullable) | Результат анализа LLM |
| `resume_match_percentage` | Integer (nullable) | Соответствие резюме (0-100) |
| `match_analysis` | Text (nullable) | Объяснение от LLM |
| `status` | String(50) | Статус заявки (enum) |
| `cover_letter` | Text (nullable) | Сгенерированное cover letter |
| `applied_date` | DateTime (nullable) | Дата подачи заявки |
| `response_date` | DateTime (nullable) | Дата получения ответа |
| `days_to_response` | Integer (nullable) | Дни до ответа (автовычисляемое) |
| `created_at` | DateTime | Дата создания записи |
| `updated_at` | DateTime | Дата последнего обновления |

### Enum: Status
- `new` - добавлена в систему, ещё не подавал
- `applied` - заявка подана
- `interview` - пригласили на интервью
- `offer` - предложили оффер
- `rejected` - отказали

### Файлы пользователя

```
templates/
  ├── cover_letter_base.txt  # Базовый шаблон cover letter
  └── user_resume.txt         # Резюме пользователя (для анализа)
```

### Логика работы
- **days_to_response**: вычисляется автоматически при установке `response_date`
- **resume_match_percentage**: заполняется по запросу пользователя (кнопка "Analyze Match")
- **has_visa_sponsorship**: заполняется через LLM-анализ текста описания
- **cover_letter**: генерируется по запросу на основе `user_resume.txt` + `cover_letter_base.txt` + `job_description`

## 6. Работа с LLM

### LLM Функции

#### 1. Анализ Visa Sponsorship
**Функция:** `analyze_visa_sponsorship(job_description: str)`
- **Вход:** текст описания вакансии (макс. 5000 символов)
- **Выход:** `{"has_sponsorship": bool, "analysis": str}`
- **Модель:** GPT-3.5-turbo
- **Промпт:** из конфиг-файла

#### 2. Resume Match Analysis
**Функция:** `analyze_resume_match(resume: str, job_description: str)`
- **Вход:** резюме + описание вакансии (макс. 5000 символов каждое)
- **Выход:** `{"match_percentage": int, "analysis": str}`
- **Модель:** GPT-3.5-turbo
- **Промпт:** из конфиг-файла

#### 3. Cover Letter Generation
**Функция:** `generate_cover_letter(resume: str, template: str, job_description: str, job_title: str, company: str)`
- **Вход:** резюме + базовый шаблон + описание вакансии + название позиции + компания
- **Выход:** `{"cover_letter": str}`
- **Модель:** GPT-3.5-turbo
- **Промпт:** из конфиг-файла

#### 4. Extract Job Info (автоматическое извлечение)
**Функция:** `extract_job_info(job_description: str)`
- **Вход:** текст описания вакансии
- **Выход:** `{"title": str, "company": str}`
- **Модель:** GPT-3.5-turbo
- **Промпт:** из конфиг-файла
- **Использование:** автоматически при добавлении новой вакансии

### Технические параметры

```python
# Настройки OpenAI API
MODEL = "gpt-3.5-turbo"
TEMPERATURE = 0.3  # Более детерминированные ответы
MAX_TOKENS = 1000
TIMEOUT = 30  # секунд

# Ограничения
MAX_JOB_DESCRIPTION_LENGTH = 5000  # символов
MAX_RESUME_LENGTH = 5000  # символов
```

### Конфигурация промптов

**Файл:** `app/prompts.py`

```python
PROMPTS = {
    "visa_sponsorship": "...",
    "resume_match": "...",
    "cover_letter": "...",
    "extract_job_info": "..."
}
```

### Обработка ошибок
- **API недоступен** → возвращаем HTTP 503 с сообщением об ошибке
- **Rate limit** → возвращаем HTTP 429 с сообщением
- **Timeout** → возвращаем HTTP 504
- **Длинный текст** → автоматически обрезаем до лимита перед отправкой
- **Нет retry** → одна попытка, при ошибке сразу возвращаем пользователю

## 7. Мониторинг LLM

### Таблица: `llm_logs`

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | Integer (PK) | Уникальный идентификатор |
| `function_name` | String(100) | Название функции (visa_sponsorship, resume_match, cover_letter) |
| `status` | String(50) | Статус выполнения (success, error) |
| `execution_time` | Float | Время выполнения в секундах |
| `tokens_used` | Integer (nullable) | Количество использованных токенов |
| `error_message` | Text (nullable) | Сообщение об ошибке |
| `created_at` | DateTime | Timestamp запроса |

### Логирование

**Формат консольных логов:**
```
[2025-11-16 10:30:45] LLM | analyze_visa_sponsorship | SUCCESS | 2.3s | 150 tokens
[2025-11-16 10:31:12] LLM | generate_cover_letter | ERROR | 0.5s | OpenAI timeout
[2025-11-16 10:32:00] LLM | analyze_resume_match | SUCCESS | 3.1s | 280 tokens
```

**Что логируем:**
- Timestamp
- Название функции
- Статус (SUCCESS/ERROR)
- Время выполнения
- Использованные токены (если успех)
- Текст ошибки (если ошибка)

### Страница статистики

**URL:** `GET /stats` или отдельная секция в UI

**Показываем:**
- Общее количество LLM запросов
- Успешных / с ошибками
- Общее количество токенов
- Примерная стоимость (токены × цена GPT-3.5-turbo)
- Разбивка по функциям (сколько раз каждая)
- Среднее время выполнения

### Расчёт стоимости

```python
# Примерные цены GPT-3.5-turbo (на ноябрь 2025)
COST_PER_1K_TOKENS = 0.002  # $0.002 за 1K tokens

total_cost = (total_tokens / 1000) * COST_PER_1K_TOKENS
```

### API Endpoint для статистики
- `GET /api/stats` - получить статистику использования LLM

## 8. Сценарии работы

### Сценарий 1: Добавление новой вакансии
1. Пользователь открывает главную страницу
2. Вставляет **только URL и описание вакансии** в форму
3. Нажимает "Add Job"
4. **Система автоматически через LLM извлекает:**
   - Название позиции (title)
   - Название компании (company)
5. Сохраняет в БД со статусом "new"
6. Вакансия появляется в списке с автозаполненными полями

### Сценарий 2: Анализ visa sponsorship
1. Пользователь видит вакансию в списке
2. Нажимает кнопку "Check Sponsorship"
3. Система отправляет описание в LLM
4. Получает результат (да/нет + объяснение)
5. Обновляет `has_visa_sponsorship` и `sponsorship_analysis` в БД
6. Показывает результат пользователю (badge или icon)

### Сценарий 3: Проверка соответствия резюме
1. Пользователь нажимает "Analyze Match" на конкретной вакансии
2. Система читает `templates/user_resume.txt`
3. Отправляет резюме + описание вакансии в LLM
4. Получает процент (0-100) + объяснение
5. Сохраняет `resume_match_percentage` и `match_analysis` в БД
6. Показывает процент и объяснение

### Сценарий 4: Генерация cover letter
1. Пользователь нажимает "Generate Cover Letter"
2. Система читает:
   - `templates/user_resume.txt`
   - `templates/cover_letter_base.txt`
3. Отправляет в LLM вместе с описанием вакансии, названием и компанией
4. Получает персонализированное cover letter
5. Сохраняет в поле `cover_letter` в БД
6. Показывает письмо в модальном окне (можно скопировать/скачать)

### Сценарий 5: Обновление статуса заявки
1. Пользователь меняет статус через dropdown (new → applied → interview → offer/rejected)
2. **При переходе в "applied":**
   - Система автоматически ставит `applied_date = today()`
   - Поле остаётся редактируемым (можно изменить дату)
3. **При переходе в "offer" или "rejected":**
   - Система автоматически ставит `response_date = today()`
   - Автоматически вычисляет `days_to_response = response_date - applied_date`
   - Поле `response_date` остаётся редактируемым
4. Изменения сохраняются в БД

### Сценарий 6: Просмотр статистики
1. Пользователь открывает страницу `/stats` или секцию Statistics
2. Видит общую статистику по использованию LLM:
   - Количество запросов
   - Использованные токены
   - Примерная стоимость
   - Разбивка по функциям
3. Может использовать для контроля расходов

## 9. Деплой

### Локальный запуск (MVP)

**Подход:** Простой локальный запуск на машине разработчика

**Требования:**
- Python 3.10+
- Virtual environment (venv)
- OpenAI API ключ

**Скрипт запуска:** `run.sh`
```bash
#!/bin/bash

# Активируем виртуальное окружение
source venv/bin/activate

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please create .env file with OPENAI_API_KEY"
    exit 1
fi

# Запускаем FastAPI приложение
echo "Starting Job Search Helper..."
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Доступ:** `http://localhost:8000`

### Инструкция в README

**Шаги запуска:**
1. Клонировать репозиторий
2. Создать `.env` файл с `OPENAI_API_KEY=your_key_here`
3. Активировать venv: `source venv/bin/activate`
4. Установить зависимости: `pip install -r requirements.txt`
5. Запустить: `./run.sh` или `uvicorn app.main:app --reload`
6. Открыть браузер: `http://localhost:8000`

**Первый запуск:**
- Создать файл `templates/user_resume.txt` с вашим резюме
- Создать файл `templates/cover_letter_base.txt` с базовым шаблоном
- База данных `data/jobs.db` создастся автоматически

### Что НЕ делаем на MVP
- ❌ Docker/контейнеризация
- ❌ CI/CD пайплайны
- ❌ Production WSGI сервер (Gunicorn)
- ❌ Reverse proxy (Nginx)
- ❌ HTTPS/SSL
- ❌ Удалённый доступ
- ❌ Мультипользовательский режим

### Остановка приложения
- `Ctrl+C` в терминале где запущен uvicorn

## 10. Подход к конфигурированию

### Структура конфигурации

**Принцип:** Разделение секретов, настроек и промптов по разным файлам

### Файл: `.env` (секретные данные)
```env
OPENAI_API_KEY=sk-proj-...
DATABASE_URL=sqlite:///./data/jobs.db
```

- **НЕ коммитится в git** (в .gitignore)
- Только API ключи и чувствительные данные

### Файл: `.env.example` (шаблон для пользователей)
```env
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=sqlite:///./data/jobs.db
```

- **Коммитится в git** как пример
- Помогает другим разработчикам настроить окружение

### Файл: `app/config.py` (технические настройки)
```python
import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-3.5-turbo"
OPENAI_TEMPERATURE = 0.3
OPENAI_MAX_TOKENS = 1000
OPENAI_TIMEOUT = 30  # секунд

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/jobs.db")

# Ограничения на длину текста
MAX_JOB_DESCRIPTION_LENGTH = 5000  # символов
MAX_RESUME_LENGTH = 5000  # символов

# Стоимость для расчёта в статистике
COST_PER_1K_TOKENS = 0.002  # $0.002 за 1K tokens (GPT-3.5-turbo)
```

### Файл: `app/prompts.py` (промпты для LLM)
```python
PROMPTS = {
    "extract_job_info": """
        Extract the job title and company name from this job description.
        Return JSON: {"title": "...", "company": "..."}
        """,
    
    "visa_sponsorship": """
        Analyze this job description and determine if visa sponsorship is offered.
        Return JSON: {"has_sponsorship": true/false, "analysis": "..."}
        """,
    
    "resume_match": """
        Compare this resume with the job requirements.
        Return JSON: {"match_percentage": 0-100, "analysis": "..."}
        """,
    
    "cover_letter": """
        Generate a personalized cover letter based on the resume,
        base template, and job description.
        Return JSON: {"cover_letter": "..."}
        """
}
```

### Преимущества подхода
- **Секреты отдельно** - `.env` никогда не попадёт в git
- **Настройки централизованы** - все параметры в `config.py`
- **Промпты редактируемы** - легко менять без поиска по коду
- **Простота** - нет сложных конфиг-систем, YAML, JSON файлов

## 11. Подход к логгированию

### Принцип

**Минимальное логирование в консоль** - без файлов, без ротации, без сложных систем

### Что логируем

#### 1. Запуск приложения
```
[2025-11-16 10:00:00] INFO | Application started on http://127.0.0.1:8000
[2025-11-16 10:00:00] INFO | Database connected: sqlite:///./data/jobs.db
[2025-11-16 10:00:00] INFO | OpenAI API configured
```

#### 2. API запросы (основные операции)
```
[2025-11-16 10:01:23] INFO | POST /api/jobs | 201 Created | Job ID: 42
[2025-11-16 10:02:15] INFO | GET /api/jobs | 200 OK | 15 jobs returned
[2025-11-16 10:03:00] INFO | DELETE /api/jobs/42 | 204 No Content
```

#### 3. LLM вызовы (детально)
```
[2025-11-16 10:03:45] LLM | extract_job_info | SUCCESS | 2.1s | 120 tokens
[2025-11-16 10:04:12] LLM | analyze_visa_sponsorship | SUCCESS | 3.5s | 180 tokens
[2025-11-16 10:05:00] LLM | generate_cover_letter | SUCCESS | 5.2s | 450 tokens
[2025-11-16 10:06:30] LLM | analyze_resume_match | ERROR | 0.5s | OpenAI timeout
```

#### 4. Ошибки (всё подробно)
```
[2025-11-16 10:07:00] ERROR | Database error: unable to open database file
[2025-11-16 10:08:15] ERROR | OpenAI API error: Rate limit exceeded
[2025-11-16 10:09:30] ERROR | File not found: templates/user_resume.txt
```

### Технические детали

**Библиотека:** Стандартный `logging` модуль Python

**Настройка:**
```python
import logging

# Простая конфигурация
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)
```

**Уровни логов:**
- `INFO` - нормальная работа (старт, API calls, LLM успех)
- `ERROR` - ошибки (API errors, DB errors, file errors)
- `DEBUG` - отключен на MVP (можно включить для отладки)

### Что НЕ логируем
- ❌ Полные тексты job descriptions (слишком длинно)
- ❌ API ключи и секреты
- ❌ Содержимое резюме пользователя
- ❌ Полные тексты cover letters
- ❌ SQL запросы (не нужно на MVP)

### Куда логируем
- ✅ **Консоль (stdout)** - единственный выход
- ❌ Файлы - не используем
- ❌ Внешние сервисы (Sentry, CloudWatch) - не используем

### Пример использования в коде
```python
from app.config import logger

# Успешная операция
logger.info("Job created successfully", extra={"job_id": job.id})

# Ошибка
logger.error(f"Failed to call OpenAI API: {error_message}")
```

---

## Заключение

Этот документ описывает **минимально жизнеспособный продукт (MVP)** для Job Search Helper - простое, функциональное приложение для проверки идеи.

### Ключевые принципы MVP
- ✅ **KISS** - максимальная простота
- ✅ **Монолит** - всё в одном месте
- ✅ **Single-user** - один пользователь, локальный запуск
- ✅ **Быстрый старт** - от нуля до работающего приложения за минимальное время
- ✅ **Без оверинжиниринга** - никаких лишних технологий и паттернов

### Готовность к разработке
Документ содержит всё необходимое для начала разработки:
- Технологический стек определён
- Архитектура спроектирована
- Модель данных описана
- Сценарии работы детализированы
- Подход к реализации согласован

### Следующие шаги
1. Создать структуру проекта
2. Настроить окружение (requirements.txt, .env)
3. Реализовать базу данных и модели
4. Реализовать LLM интеграцию
5. Создать API endpoints
6. Разработать простой веб-интерфейс
7. Тестирование и запуск

**Документ готов к использованию как техническое задание для разработки!**


