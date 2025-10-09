# MAX System - Руководство по использованию

## Быстрый старт

### 1. Запуск системы

Запустите Text Generation Web UI как обычно:

```bash
python server.py
```

Или используйте рабочую конфигурацию:

```bash
python server.py --auto-launch --model Qwen2.5-14B-Instruct-Uncensored.i1-Q5_K_S.gguf --gpu-layers 43
```

### 2. Активация расширения

1. Откройте веб-интерфейс
2. Перейдите на вкладку "Сессия"
3. В разделе "Расширения" найдите "max_system"
4. Поставьте галочку для активации
5. Нажмите "Применить и перезапустить"

### 3. Использование MAX System

После активации появится вкладка "MAX System" в главном меню.

## Примеры задач

### 🔹 Простая задача - Обработка данных

**Задача:**
```
Создай скрипт для чтения CSV файла с данными о продажах, 
подсчитай общую сумму по каждому продукту и сохрани результат в JSON
```

**Что произойдёт:**
1. Система создаст план из 4-5 шагов
2. Сгенерирует код для каждого шага
3. Выполнит и протестирует
4. Исправит ошибки, если появятся
5. Создаст готовый проект в `user_data/max_system/projects/`

### 🔹 Средняя задача - Веб-скрейпинг

**Задача:**
```
Напиши парсер новостей, который:
1. Загружает главную страницу news.ycombinator.com
2. Извлекает заголовки топ-10 новостей
3. Сохраняет результат в SQLite базу данных с timestamp
```

**Ожидаемый результат:**
- Python скрипт с использованием requests/beautifulsoup
- SQLite база с таблицей news
- Обработка ошибок сети
- Документация и комментарии

### 🔹 Сложная задача - Создание API

**Задача:**
```
Создай REST API для системы управления задачами (TODO):
- Модели: Task (id, title, description, status, created_at)
- Эндпоинты: GET /tasks, POST /tasks, PUT /tasks/{id}, DELETE /tasks/{id}
- Хранение в SQLite
- Валидация входных данных
- Документация API
```

**Что получите:**
- Полноценное FastAPI приложение
- SQLite база данных
- CRUD операции
- Валидацию с Pydantic
- README с инструкциями

## Рабочий процесс

### Шаг 1: Описание задачи

В поле "Task Description" опишите задачу максимально конкретно:

❌ **Плохо:** "сделай что-нибудь с файлами"

✅ **Хорошо:** "Создай скрипт, который сканирует директорию, находит все .txt файлы и объединяет их содержимое в один файл output.txt"

### Шаг 2: Запуск

Нажмите кнопку "🚀 Execute Task"

Система начнёт работу:
```
[10:30:15] Starting task: <описание>
[10:30:16] Using model: Qwen2.5-14B-Instruct-Uncensored
[10:30:17] Creating execution plan...
[10:30:20] Step 1/5 - Import necessary libraries
[10:30:25] Step 2/5 - Define file scanning function
...
```

### Шаг 3: Мониторинг

Отслеживайте прогресс в реальном времени:

- **Status** - текущее состояние задачи
- **Execution Log** - пошаговый лог
- **Detailed Results** - полная информация в JSON

### Шаг 4: Результат

После завершения:

1. Статус покажет результат (✅ успех / ⚠️ частичное выполнение)
2. В `user_data/max_system/projects/task_<id>_<timestamp>/` найдёте:
   - `src/` - сгенерированный код
   - `tests/` - тесты (если были созданы)
   - `README.md` - документация
   - `.git/` - история изменений

## Возможности системы

### 🧠 Планирование

MAX System анализирует задачу и создаёт оптимальный план:

```
Задача: Создать систему логирования
↓
План:
1. Import logging module and define configuration
2. Create Logger class with file and console handlers
3. Implement log methods (debug, info, warning, error)
4. Add log rotation functionality
5. Create example usage and tests
```

### 💻 Генерация кода

Код генерируется с:
- ✅ Правильной структурой
- ✅ Docstrings и комментариями
- ✅ Обработкой ошибок
- ✅ Type hints (Python 3.10+)
- ✅ Best practices

### 🔧 Автоисправление

Если код падает с ошибкой:

```
Error: NameError: name 'pd' is not defined
↓
Анализ: Missing import for pandas
↓
Fix: Added 'import pandas as pd' at the top
↓
Retry: Success ✅
```

Система автоматически:
1. Классифицирует ошибку
2. Находит причину
3. Генерирует исправление
4. Применяет и проверяет
5. Повторяет до 3 раз

### 🧠 Память и обучение

Система запоминает:
- ✅ Успешные паттерны решения
- ✅ Типичные ошибки и исправления
- ✅ Используемые библиотеки
- ✅ Эффективные подходы

При повторных похожих задачах:
```
"Создай парсер JSON" (2-я попытка)
↓
Found similar experience: "Создай парсер CSV"
↓
Using successful pattern from previous task
↓
Faster execution with better code
```

### 📦 Git интеграция

Каждый шаг автоматически коммитится:

```bash
git log --oneline
a1b2c3d [MAX] Step 5: Create example usage and tests
b2c3d4e [MAX] Step 4: Add log rotation functionality
c3d4e5f [MAX] Step 3: Implement log methods
...
```

## Продвинутое использование

### Настройка конфигурации

Отредактируйте `extensions/max_system/config.yaml`:

```yaml
# Увеличить количество токенов для больших проектов
llm:
  max_tokens: 8192  # было 4096

# Больше попыток исправления
agents:
  reflex:
    max_fix_attempts: 5  # было 3

# Таймаут для долгих операций
execution:
  timeout: 600  # было 300 (5 минут -> 10 минут)
```

### Работа с зависимостями

Система автоматически определяет нужные библиотеки:

```python
# В коде будет:
import pandas as pd
import requests
```

Для установки зависимостей:
```bash
cd user_data/max_system/projects/task_123_xxx/
pip install -r requirements.txt  # если создан
# или
pip install pandas requests  # вручную
```

### Просмотр истории

#### Через UI
1. Откройте "Recent Tasks"
2. Нажмите "🔄 Refresh Tasks"
3. Введите Task ID в "Task Status" для деталей

#### Через SQLite
```bash
sqlite3 user_data/max_system/memory/tasks.db

.mode column
.headers on

-- Все задачи
SELECT id, description, status, created_at FROM tasks;

-- Детали задачи
SELECT * FROM steps WHERE task_id = 5;

-- Статистика ошибок
SELECT error_type, COUNT(*) as count 
FROM errors 
GROUP BY error_type 
ORDER BY count DESC;
```

### Векторный поиск опыта

ChromaDB хранит семантические эмбеддинги:

```python
from extensions.max_system.agents.agent_memory import MemoryAgent
import yaml

with open('extensions/max_system/config.yaml') as f:
    config = yaml.safe_load(f)

memory = MemoryAgent(config)

# Найти похожие задачи
similar = memory.get_similar_experiences("parse JSON file", limit=5)
for exp in similar:
    print(f"Pattern: {exp['pattern']}")
    print(f"Distance: {exp['distance']}\n")
```

## Troubleshooting

### ❌ "MAX System not initialized"

**Причина:** Ошибка при загрузке расширения

**Решение:**
1. Проверьте логи: `user_data/logs/`
2. Установите зависимости: `pip install -r extensions/max_system/requirements.txt`
3. Перезапустите сервер

### ❌ "No model loaded"

**Причина:** Не загружена LLM модель

**Решение:**
1. Перейдите на вкладку "Модель"
2. Выберите .gguf модель
3. Нажмите "Загрузить"
4. Вернитесь на вкладку MAX System

### ❌ "Safety check failed"

**Причина:** Код содержит потенциально опасные операции

**Решение:**
1. Проверьте, нет ли в задаче требований к `os.system`, `eval`, `exec`
2. Переформулируйте задачу безопасным способом
3. При необходимости отредактируйте `config.yaml` → `safety.restricted_imports`

### ⚠️ Код работает, но медленно

**Оптимизация:**

1. **Уменьшите количество шагов:**
   ```yaml
   agents:
     planner:
       max_steps: 10  # вместо 20
   ```

2. **Используйте более быструю модель:**
   - Загрузите модель меньшего размера (7B вместо 14B)
   - Или используйте квантизацию Q4 вместо Q5

3. **Увеличьте GPU layers:**
   ```bash
   python server.py --gpu-layers 49  # все слои на GPU
   ```

### 📊 Мониторинг производительности

```python
# Статистика выполнения
SELECT 
    COUNT(*) as total_tasks,
    SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) as completed,
    AVG(JULIANDAY(completed_at) - JULIANDAY(created_at)) * 24 * 60 as avg_minutes
FROM tasks;
```

## Best Practices

### ✅ DO

1. **Будьте конкретны:**
   - "Создай парсер для API OpenWeatherMap, который сохраняет температуру в SQLite"
   - vs "сделай парсер погоды"

2. **Разбивайте сложные задачи:**
   - Вместо одной огромной задачи, создайте несколько последовательных
   - "Сначала создай модели данных, потом API endpoints"

3. **Проверяйте результат:**
   - Всегда тестируйте сгенерированный код
   - Читайте логи выполнения

4. **Используйте контекст:**
   - "...как в предыдущей задаче" - система найдёт похожий опыт

### ❌ DON'T

1. **Не давайте расплывчатых описаний:**
   - ❌ "сделай что-то полезное"
   - ❌ "создай программу"

2. **Не требуйте невозможного:**
   - ❌ "Создай полноценный аналог Photoshop"
   - ✅ "Создай утилиту для изменения размера изображений"

3. **Не игнорируйте ошибки:**
   - Если задача фейлится 3 раза подряд - переформулируйте
   - Проверьте зависимости и окружение

## Примеры реальных задач

### 📝 Логирование

```
Создай систему логирования ошибок с записью в SQLite:
- Логи с уровнями (DEBUG, INFO, WARNING, ERROR)
- Автоматическая ротация (1000 записей)
- Фильтрация по дате и уровню
- CLI для просмотра логов
```

### 🌐 API клиент

```
Создай Python клиент для JSONPlaceholder API:
- Методы для получения постов, комментариев, пользователей
- Кэширование запросов
- Обработка ошибок и retry логика
- Типизация с dataclasses
```

### 📊 Анализ данных

```
Создай скрипт для анализа CSV файла с продажами:
- Загрузка данных с pandas
- Группировка по категориям и датам
- Вычисление статистики (сумма, среднее, медиана)
- Визуализация с matplotlib (опционально)
- Сохранение отчёта в Excel
```

## Интеграция с существующим кодом

MAX System может работать с вашим существующим кодом:

```
У меня есть файл parser.py с функцией parse_data(). 
Создай unittest тесты для этой функции с покрытием edge cases.

Контекст: parser.py находится в src/utils/
```

Система учтёт контекст и создаст совместимые тесты.

## Что дальше?

После освоения базового функционала:

1. **Изучите агентов подробнее** - каждый агент можно настроить
2. **Экспериментируйте с промптами** - описывайте задачи по-разному
3. **Анализируйте память** - изучите, что система запомнила
4. **Расширяйте систему** - добавляйте свои агенты и инструменты

---

**MAX System** превращает локальную LLM в полноценного AI-разработчика! 🚀
