# russian-whisper

Скрипт для транскрибирования русской речи через fast-whisper

## Описание

Этот проект предоставляет скрипт `transcribe.py` для автоматической транскрибации русской речи из аудиофайлов с помощью модели fast-whisper. Поддерживаются популярные форматы аудио, автоматическое определение языка и сохранение результата в текстовый файл.

## Установка

1. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/nivedano/russian-whisper.git
   cd russian-whisper
   ```

2. Установите зависимости:
  
   ```bash
   pip install -r requirements.txt
   ```

3. (Опционально) Установите ffmpeg, если он ещё не установлен (для поддержки большинства аудиоформатов):
   - Windows: скачайте с [ffmpeg.org/download.html](https://ffmpeg.org/download.html)
   - Linux: `sudo apt install ffmpeg`
   - MacOS: `brew install ffmpeg`

## Быстрый старт

Один файл: python transcribe.py <аудиофайл> [файл_результата] [--segments] [--dry-run]
Папка:     python transcribe.py <папка_аудио> [папка_результата] [--segments] [--dry-run]

Примеры:
  python transcribe.py speech.mp3 transcript.txt
  python transcribe.py /path/to/audio/files
  python transcribe.py /path/to/audio/files /path/to/output
  python transcribe.py /path/to/audio/files /path/to/output --segments
  python transcribe.py /path/to/audio/files /path/to/output --dry-run

## Лицензия

MIT License

## Контакты

По вопросам и предложениям: [issues на GitHub](https://github.com/nivedano/russian-whisper/issues)
