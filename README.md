# Textgen Assistant

Проект для локального LLM агента с WebUI и FastAPI, использующий Qwen2.5-14B-Instruct.

## Структура проекта
 * webui/ — Text-generation-webui
 * fastapi/ — FastAPI сервер и память (ChromaDB)
 * scripts/ — Скрипты запуска
 * copilot-prompts.txt — Промты для GitHub Copilot

## Установка
 * Клонируйте репозиторий:
   ```bash
   git clone https://github.com/yourusername/textgen-assistant.git
   cd textgen-assistant
   ```

 * Установите mamba и создайте окружение:
   ```
   mamba env create -f environment.yml
   mamba activate textgen
   ```

 * Запустите WebUI:
   ```
   scripts/start_webui.bat
   ```

 * Запустите FastAPI:
   ```
   scripts/start_fastapi.bat
   ```

## Модель
Скачайте Qwen2.5-14B-Instruct-Uncensored.i1-Q5_K_S.gguf и положите в webui/models/.