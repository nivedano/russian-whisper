# russian-whisper

Скрипт для транскрибирования русской речи через fast-whisper

## Описание

Этот проект предоставляет скрипт `transcribe.py` для распознавания русской речи из аудиофайлов с помощью модели fast-whisper. Поддерживаются популярные форматы аудио, автоматическое определение языка и сохранение результата в текстовый файл.

## Установка

1. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/nivedano/russian-whisper.git
   cd russian-whisper
   ```

   Могут быть проблемы совместимости с python >=3.12.
   Точно работает на python 3.11

1. Установите `uv` (пакетный менеджер/раннер Python):

   Инструкции установки: [docs.astral.sh/uv](https://docs.astral.sh/uv/)

1. Установите зависимости через `uv` (создаст `.venv` и поставит пакеты по `uv.lock`):

   ```bash
   uv sync
   ```

1. (Опционально) Установите ffmpeg, если он ещё не установлен (для поддержки большинства аудиоформатов):
   - Windows:
      - `winget install -e --id Gyan.FFmpeg`
      - [ffmpeg.org/download.html](https://ffmpeg.org/download.html)
   - Linux: `sudo apt install ffmpeg`
   - MacOS: `brew install ffmpeg`

## Быстрый старт

Один файл:

```bash
uv run python transcribe.py <аудиофайл> [файл_результата] [--segments] [--dry-run]
```

Папка:

```bash
uv run python transcribe.py <папка_аудио> [папка_результата] [--segments] [--dry-run]
```

Примеры:

```bash
uv run python transcribe.py speech.mp3 transcript.txt
uv run python transcribe.py /path/to/audio/files
uv run python transcribe.py /path/to/audio/files /path/to/output
uv run python transcribe.py /path/to/audio/files /path/to/output --segments
uv run python transcribe.py /path/to/audio/files /path/to/output --dry-run
```

На Windows можно запускать и напрямую файл скрипта:

```powershell
uv run .\transcribe.py "C:\\path\\to\\audio.m4a"
```

## Лицензия

MIT License

## Контакты

По вопросам и предложениям: [issues на GitHub](https://github.com/nivedano/russian-whisper/issues)
