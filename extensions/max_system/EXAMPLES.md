# MAX System - Примеры задач

Этот файл содержит готовые примеры задач для тестирования MAX System.

## Уровень 1: Простые задачи (1-3 шага)

### 📝 Пример 1: Hello World с файлом

**Задача:**
```
Создай Python скрипт, который:
1. Выводит "Hello, MAX System!" в консоль
2. Сохраняет это сообщение в файл greeting.txt
3. Читает файл обратно и выводит содержимое
```

**Ожидаемый результат:**
- Файл `hello_world.py` с функциями write и read
- Использование pathlib или os.path
- Обработка ошибок файловых операций

---

### 🔢 Пример 2: Простой калькулятор

**Задача:**
```
Создай модуль калькулятора с функциями:
- add(a, b) - сложение
- subtract(a, b) - вычитание
- multiply(a, b) - умножение
- divide(a, b) - деление с обработкой деления на ноль
Добавь docstrings и type hints
```

**Ожидаемый результат:**
- Чистые функции с документацией
- Обработка ZeroDivisionError
- Type hints для всех параметров

---

### 📋 Пример 3: TODO список в памяти

**Задача:**
```
Создай простой менеджер TODO списка:
- Класс TodoList с методами add, remove, list
- Хранение в списке в памяти (не файл, не БД)
- Каждая задача имеет id, title, completed (bool)
- Метод для вывода всех задач в красивом виде
```

**Ожидаемый результат:**
- Класс с методами CRUD
- Auto-increment ID для задач
- Форматированный вывод

---

## Уровень 2: Средние задачи (4-7 шагов)

### 📊 Пример 4: CSV анализатор

**Задача:**
```
Создай анализатор CSV файлов:
1. Функция load_csv(filename) для загрузки данных
2. Функция analyze(data) для вычисления статистики:
   - Количество строк и столбцов
   - Типы данных в каждой колонке
   - Пропущенные значения (NaN)
3. Функция save_report(stats, output_file) для сохранения в JSON
4. Пример использования с тестовыми данными
```

**Ожидаемый результат:**
- Использование pandas или csv модуля
- Обработка различных типов данных
- JSON отчёт с детальной статистикой

---

### 🌐 Пример 5: URL shortener

**Задача:**
```
Создай простой URL shortener:
1. Функция shorten(long_url) → короткий код (6 символов)
2. Функция expand(short_code) → оригинальный URL
3. Хранение в словаре {short_code: long_url}
4. Функция для генерации уникальных кодов
5. Валидация URL (проверка формата)
6. CLI интерфейс для использования
```

**Ожидаемый результат:**
- Генерация коротких кодов (random или hash)
- Проверка на уникальность
- Валидация URL с regex или urllib
- Простой CLI с argparse

---

### 📖 Пример 6: Простой блокнот

**Задача:**
```
Создай текстовый блокнот с SQLite хранением:
1. База данных notes.db с таблицей notes (id, title, content, created_at)
2. CRUD операции: create_note, read_note, update_note, delete_note
3. Функция list_all_notes для вывода списка
4. Функция search_notes(keyword) для поиска в заголовке и содержимом
5. Примеры использования всех функций
```

**Ожидаемый результат:**
- SQLite база с правильной схемой
- Все CRUD операции
- Поиск с LIKE в SQL
- Форматированный вывод результатов

---

## Уровень 3: Сложные задачи (8-15 шагов)

### 🎯 Пример 7: Task Manager API

**Задача:**
```
Создай REST API для управления задачами:

Модели:
- Task: id, title, description, status (todo/in_progress/done), priority (1-5), created_at, updated_at

Функциональность:
1. Создание базы данных SQLite
2. Модели данных с dataclasses или Pydantic
3. CRUD операции через класс TaskManager
4. Фильтрация задач по status и priority
5. Сортировка задач (по дате, приоритету)
6. Статистика: количество задач по статусам
7. CLI интерфейс для всех операций
8. Документация с примерами использования

Требования:
- Валидация входных данных
- Обработка ошибок
- Type hints везде
- Docstrings для всех функций
```

**Ожидаемый результат:**
- Полноценная система управления задачами
- SQLite с нормализованной схемой
- Все операции протестированы в примерах
- README с API документацией

---

### 📰 Пример 8: RSS Feed Reader

**Задача:**
```
Создай RSS фид ридер:

Компоненты:
1. Парсер RSS (feedparser или xml.etree)
2. База данных feeds.db:
   - Таблица feeds (id, url, title, last_checked)
   - Таблица articles (id, feed_id, title, link, published, read)
3. Класс FeedManager:
   - add_feed(url) - добавить RSS источник
   - fetch_feed(feed_id) - загрузить новые статьи
   - list_feeds() - список источников
   - list_articles(feed_id, unread_only) - статьи
   - mark_as_read(article_id)
4. Автообновление фидов (с проверкой last_checked)
5. CLI для всех операций
6. Обработка ошибок сети

Дополнительно:
- Дедупликация статей по URL
- Экспорт статей в JSON
- Простая статистика (количество непрочитанных)
```

**Ожидаемый результат:**
- Полноценный RSS ридер
- Надёжная обработка XML
- Периодическая проверка обновлений
- User-friendly CLI

---

### 🎲 Пример 9: Игра "Угадай число" с статистикой

**Задача:**
```
Создай игру "Угадай число" с системой статистики:

Игровая логика:
1. Генерация случайного числа (1-100)
2. Приём попыток от пользователя
3. Подсказки "больше" или "меньше"
4. Подсчёт попыток
5. Вывод результата

Система статистики:
1. База данных game_stats.db
2. Таблица games (id, number, attempts, won, duration, timestamp)
3. Сохранение каждой игры
4. Статистика:
   - Всего игр
   - Win rate
   - Средние попытки
   - Лучшие результаты (top 10)
   - История последних игр

CLI:
- Основная игра
- Команды: play, stats, history, reset
- Красивый вывод результатов

Требования:
- Input validation
- Таймер игры
- Graceful exit (Ctrl+C)
```

**Ожидаемый результат:**
- Рабочая игра с хорошим UX
- Полная статистика в БД
- Аналитика игровых данных
- Понятный CLI интерфейс

---

## Уровень 4: Продвинутые задачи (15+ шагов)

### 🏪 Пример 10: Интернет-магазин (Console версия)

**Задача:**
```
Создай консольную систему интернет-магазина:

База данных (SQLite):
1. products (id, name, description, price, stock, category)
2. customers (id, name, email, password_hash, created_at)
3. orders (id, customer_id, total, status, created_at)
4. order_items (id, order_id, product_id, quantity, price)

Модули:
1. Product Management:
   - add_product, update_product, delete_product
   - list_products(category, in_stock_only)
   - search_products(query)

2. Customer Management:
   - register_customer
   - authenticate_customer (простой hash)
   - view_customer_profile

3. Shopping Cart:
   - add_to_cart, remove_from_cart
   - view_cart
   - calculate_total

4. Order Processing:
   - create_order (из корзины)
   - view_orders(customer_id)
   - update_order_status

5. Admin Panel:
   - view_statistics
   - low_stock_alert
   - best_selling_products

CLI Interface:
- Меню навигация
- Разные роли (customer, admin)
- Корзина в сессии
- Форматированный вывод

Требования:
- Транзакции для заказов
- Валидация данных
- Безопасное хранение паролей (hashlib)
- Обработка всех edge cases
```

**Ожидаемый результат:**
- Полноценная e-commerce система
- Нормализованная БД
- Роли и авторизация
- Корзина и заказы
- Админ панель

---

### 🌤️ Пример 11: Weather Station Dashboard

**Задача:**
```
Создай систему мониторинга погоды:

Компоненты:

1. Weather API Client:
   - Интеграция с OpenWeatherMap API
   - get_current_weather(city)
   - get_forecast(city, days)
   - Кэширование запросов (10 минут)

2. Database (SQLite):
   - cities (id, name, country, lat, lon)
   - weather_logs (id, city_id, temp, humidity, pressure, conditions, timestamp)
   - Автоматическая очистка старых данных (>30 дней)

3. Data Collection:
   - Фоновый сборщик (каждые 15 минут)
   - Сбор данных для всех городов в списке
   - Обработка ошибок API

4. Analytics:
   - Температурные тренды (за день, неделю, месяц)
   - Сравнение городов
   - Экстремальные значения
   - Средние показатели

5. Console Dashboard:
   - Текущая погода
   - График изменений (ASCII art)
   - Alerts (экстремальная погода)
   - Интерактивные команды

6. Reports:
   - Ежедневные отчёты (JSON)
   - CSV экспорт для аналитики
   - Markdown summary

Требования:
- Async requests (asyncio + aiohttp)
- Graceful shutdown
- Config file для API keys
- Comprehensive error handling
- Logs для всех операций
```

**Ожидаемый результат:**
- Профессиональный weather monitoring
- Real-time data collection
- Аналитика и визуализация
- Экспорт данных

---

## Специализированные задачи

### 🧪 Пример 12: Unit Test Generator

**Задача:**
```
Создай генератор unit tests:

Вход: Python файл с функциями
Выход: pytest тесты

Функциональность:
1. Парсинг Python кода (ast модуль)
2. Извлечение функций и их сигнатур
3. Генерация тестов:
   - Normal cases
   - Edge cases
   - Error cases
4. Fixtures для зависимостей
5. Parametrized tests где возможно

Пример:
def calculate_discount(price, discount_percent):
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("Invalid discount")
    return price * (1 - discount_percent / 100)

Сгенерирует:
- test_calculate_discount_normal
- test_calculate_discount_zero
- test_calculate_discount_max
- test_calculate_discount_invalid_negative
- test_calculate_discount_invalid_over_100
```

**Ожидаемый результат:**
- Автоматическая генерация тестов
- Покрытие разных сценариев
- Готовые к запуску pytest тесты

---

### 🔐 Пример 13: Password Manager

**Задача:**
```
Создай консольный менеджер паролей:

Безопасность:
1. Master password (bcrypt hash)
2. Шифрование паролей (cryptography.fernet)
3. Автоблокировка после неактивности

База данных:
- accounts (id, service, username, encrypted_password, url, notes, created_at)
- master_password (hash)

Функции:
1. Инициализация (первый запуск)
2. Аутентификация
3. Добавление аккаунта
4. Поиск/просмотр аккаунтов
5. Обновление пароля
6. Удаление аккаунта
7. Генератор надёжных паролей
8. Экспорт (зашифрованный)
9. Импорт из файла

CLI:
- Secure input (getpass)
- Автокопирование в буфер
- Таймер автоблокировки
- История действий

Требования:
- Криптографически безопасно
- Защита от brute force (rate limit)
- Backup функциональность
```

**Ожидаемый результат:**
- Безопасный password manager
- Сильное шифрование
- Удобный CLI
- Backup и restore

---

## Тестирование MAX System

### Рекомендуемый порядок тестирования:

1. **Начните с Уровня 1** - проверьте базовую работу
2. **Переходите к Уровню 2** - тестируйте планирование
3. **Попробуйте Уровень 3** - проверьте автофикс ошибок
4. **Уровень 4 опционально** - для полной проверки системы

### Метрики успеха:

- ✅ **90%+** задач Уровня 1 должны выполняться без ошибок
- ✅ **70%+** задач Уровня 2 должны выполняться успешно
- ✅ **50%+** задач Уровня 3 с учётом автофиксов
- ✅ **30%+** задач Уровня 4 (сложные проекты)

### Что делать, если задача не выполнилась:

1. Проверьте логи выполнения
2. Упростите задачу или разбейте на части
3. Уточните описание задачи
4. Проверьте, хватает ли контекста модели (ctx_size)

---

**Удачи в тестировании MAX System!** 🚀
