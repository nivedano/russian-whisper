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

   Могут быть проблемы совместимости с python 3.13.
   Точно работает на python 3.12.3.

2. Установите зависимости:
  
   ```bash
   pip install -r requirements.txt
   ```

   Опционально создайте venv:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

   ```powershell
   python -m venv .venv
   .venv\Scripts\activate.ps1
   ```

3. (Опционально) Установите ffmpeg, если он ещё не установлен (для поддержки большинства аудиоформатов):
   - Windows: скачайте с [ffmpeg.org/download.html](https://ffmpeg.org/download.html)
   - Linux: `sudo apt install ffmpeg`
   - MacOS: `brew install ffmpeg`

## Быстрый старт

Один файл:

```bash
python transcribe.py <аудиофайл> [файл_результата] [--segments] [--dry-run]
```

Папка:

```bash
python transcribe.py <папка_аудио> [папка_результата] [--segments] [--dry-run]
```

Примеры:

```bash
python transcribe.py speech.mp3 transcript.txt
python transcribe.py /path/to/audio/files
python transcribe.py /path/to/audio/files /path/to/output
python transcribe.py /path/to/audio/files /path/to/output --segments
python transcribe.py /path/to/audio/files /path/to/output --dry-run
```

## Лицензия

MIT License

## Контакты

По вопросам и предложениям: [issues на GitHub](https://github.com/nivedano/russian-whisper/issues)
