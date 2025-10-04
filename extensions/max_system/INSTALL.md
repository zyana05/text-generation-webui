# MAX System - Руководство по установке

## Быстрая установка

MAX System поставляется готовым к использованию в составе text-generation-webui.

### Шаг 1: Убедитесь, что Web UI работает

```bash
# Запустите веб-интерфейс
python server.py --auto-launch
```

Откройте браузер и убедитесь, что интерфейс загружается.

### Шаг 2: Загрузите модель

MAX System требует загруженную .gguf модель для работы.

**Рекомендуемые модели:**
- Qwen2.5-14B-Instruct-Uncensored (Q5_K_S или Q5_K_M)
- Mistral-7B-Instruct
- Llama-3-8B-Instruct
- DeepSeek-Coder-6.7B (для задач программирования)

**Где скачать:**
- HuggingFace: https://huggingface.co/models?search=gguf
- TheBloke: https://huggingface.co/TheBloke

**Размещение модели:**
```bash
# Скопируйте .gguf файл в
user_data/models/your-model.gguf
```

**Загрузка в интерфейсе:**
1. Вкладка "Модель" / "Model"
2. Выберите модель из списка
3. Настройте параметры (GPU layers, context size)
4. Нажмите "Загрузить" / "Load"

### Шаг 3: Установите зависимости (опционально)

MAX System работает с минимальными зависимостями, но для полного функционала установите:

```bash
# Перейдите в директорию проекта
cd /path/to/text-generation-webui

# Установите дополнительные пакеты
pip install -r extensions/max_system/requirements.txt
```

**Что устанавливается:**
- `chromadb` - для векторного поиска похожих задач (опционально)
- `pylint`, `flake8`, `black` - для проверки качества кода (опционально)
- `pytest` - для запуска тестов (опционально)

**Примечание:** Система будет работать и без этих пакетов, но с ограниченной функциональностью.

### Шаг 4: Активируйте расширение

1. Откройте веб-интерфейс
2. Перейдите на вкладку "Сессия" / "Session"
3. В разделе "Расширения" / "Extensions" найдите `max_system`
4. Поставьте галочку для активации
5. Нажмите "Применить и перезапустить" / "Apply and restart"

### Шаг 5: Проверьте работу

После перезапуска:
1. Найдите вкладку "MAX System" в главном меню
2. Введите простую задачу: "Создай функцию для сложения двух чисел"
3. Нажмите "🚀 Execute Task"
4. Наблюдайте за выполнением в логах

## Детальная установка

### Системные требования

**Минимальные:**
- Python 3.10+
- 8GB RAM
- GPU с 6GB+ VRAM (для .gguf моделей)

**Рекомендуемые:**
- Python 3.11+
- 16GB+ RAM
- GPU с 12GB+ VRAM (NVIDIA RTX 3060 или выше)
- 50GB свободного места на диске

### Проверка установки

#### Проверка Python версии
```bash
python --version
# Должно быть: Python 3.10.x или выше
```

#### Проверка GPU
```bash
# Для NVIDIA
nvidia-smi

# Для AMD (Linux)
rocm-smi
```

#### Проверка зависимостей
```bash
python -c "import gradio; print('Gradio:', gradio.__version__)"
python -c "import yaml; print('PyYAML: OK')"
```

### Установка в разных окружениях

#### Windows

```batch
REM Активируйте виртуальное окружение, если используется
call installer_files\env\Scripts\activate

REM Установите зависимости
pip install -r extensions\max_system\requirements.txt

REM Запустите
python server.py --auto-launch
```

#### Linux / macOS

```bash
# Активируйте виртуальное окружение, если используется
source installer_files/env/bin/activate

# Установите зависимости
pip install -r extensions/max_system/requirements.txt

# Запустите
python server.py --auto-launch
```

#### Docker

```bash
# Если используете Docker версию text-generation-webui
docker exec -it textgen bash
pip install -r extensions/max_system/requirements.txt
exit

# Перезапустите контейнер
docker restart textgen
```

### Конфигурация

#### Базовая конфигурация

Откройте `extensions/max_system/config.yaml` и настройте:

```yaml
# Настройки LLM
llm:
  max_tokens: 4096      # Максимум токенов для генерации
  temperature: 0.7      # Креативность (0.0-1.0)
  top_p: 0.9           # Nucleus sampling
  top_k: 40            # Top-K sampling

# Настройки выполнения
execution:
  timeout: 300         # Таймаут выполнения кода (секунды)
  max_retries: 3       # Попытки исправления ошибок

# Настройки агентов
agents:
  planner:
    max_steps: 20      # Максимум шагов в плане
  reflex:
    max_fix_attempts: 3  # Попытки исправить ошибку
```

#### Продвинутая конфигурация

**Увеличить производительность:**
```yaml
llm:
  max_tokens: 8192     # Больше токенов для сложных задач

execution:
  timeout: 600         # Больше времени на выполнение
```

**Усилить безопасность:**
```yaml
safety:
  sandbox_enabled: true
  restricted_imports:
    - os.system
    - subprocess.Popen
    - eval
    - exec
    - __import__
  max_file_operations: 50
```

**Настроить память:**
```yaml
memory:
  max_history_items: 2000        # Больше истории
  embedding_model: "sentence-transformers/all-mpnet-base-v2"
```

### Устранение проблем при установке

#### Проблема: "No module named 'chromadb'"

**Решение:**
```bash
pip install chromadb
# Или используйте без ChromaDB (векторный поиск отключится)
```

#### Проблема: "No module named 'gradio'"

**Решение:**
```bash
# Убедитесь, что используете правильное виртуальное окружение
pip install gradio
```

#### Проблема: "SQLite3 not found"

**Решение (Linux):**
```bash
sudo apt-get install sqlite3 libsqlite3-dev
```

**Решение (macOS):**
```bash
brew install sqlite3
```

#### Проблема: "Permission denied" при создании директорий

**Решение:**
```bash
# Убедитесь, что user_data доступна для записи
chmod -R 755 user_data/
```

#### Проблема: Расширение не появляется в списке

**Решение:**
1. Проверьте, что файлы на месте:
   ```bash
   ls -la extensions/max_system/script.py
   ```
2. Проверьте логи:
   ```bash
   tail -f user_data/logs/*.log
   ```
3. Перезапустите сервер с verbose:
   ```bash
   python server.py --verbose
   ```

### Обновление MAX System

Когда выходят обновления:

```bash
# Сохраните свою конфигурацию
cp extensions/max_system/config.yaml config_backup.yaml

# Обновите репозиторий
git pull origin main

# Восстановите конфигурацию, если нужно
cp config_backup.yaml extensions/max_system/config.yaml

# Установите новые зависимости, если есть
pip install -r extensions/max_system/requirements.txt --upgrade
```

### Удаление MAX System

Если нужно удалить:

```bash
# Деактивируйте расширение в UI
# Затем удалите файлы
rm -rf extensions/max_system/

# Очистите данные (опционально)
rm -rf user_data/max_system/
```

## Проверка установки

### Тест 1: Базовая проверка

```python
# Запустите в Python консоли (после загрузки модели)
from extensions.max_system.agents.agent_core import CoreAgent

core = CoreAgent()
print("✅ MAX System initialized successfully")
```

### Тест 2: Проверка памяти

```python
from extensions.max_system.agents.agent_memory import MemoryAgent
import yaml

with open('extensions/max_system/config.yaml') as f:
    config = yaml.safe_load(f)

memory = MemoryAgent(config)
task_id = memory.create_task("Test task")
print(f"✅ Created task {task_id}")
memory.close()
```

### Тест 3: Проверка через UI

1. Откройте вкладку "MAX System"
2. Введите: "Создай функцию hello_world() которая возвращает строку 'Hello, MAX!'"
3. Нажмите "Execute Task"
4. Проверьте логи и результат

## Настройка для продакшена

Для использования в продакшене:

### 1. Безопасность

```yaml
# config.yaml
safety:
  sandbox_enabled: true
  restricted_imports:
    - os.system
    - subprocess
    - eval
    - exec
```

### 2. Логирование

```yaml
logging:
  log_level: "INFO"
  save_prompts: true
  save_responses: true
```

### 3. Backup базы данных

```bash
# Создайте cron job для backup
0 2 * * * cp /path/to/user_data/max_system/memory/tasks.db /path/to/backups/tasks_$(date +\%Y\%m\%d).db
```

### 4. Мониторинг

```bash
# Проверяйте размер БД
du -h user_data/max_system/memory/tasks.db

# Проверяйте логи
tail -f user_data/max_system/logs/max_system.log
```

## Следующие шаги

После установки:

1. **Прочитайте USAGE.md** - узнайте как использовать систему
2. **Попробуйте EXAMPLES.md** - готовые примеры задач
3. **Изучите README.md** - полная документация
4. **Экспериментируйте** - пробуйте свои задачи

## Поддержка

Если возникли проблемы:

1. Проверьте логи: `user_data/logs/` и `user_data/max_system/logs/`
2. Запустите с `--verbose` флагом
3. Проверьте системные требования
4. Обратитесь к документации

---

**Готово! MAX System установлен и готов к работе!** 🚀
