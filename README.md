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

```bash
python transcribe.py --input path/to/audio.wav --output result.txt
```

## Примеры использования

1. Транскрибировать аудиофайл и вывести результат в консоль:
   ```bash
   python transcribe.py --input sample.wav
   ```
2. Транскрибировать и сохранить результат в файл:
   ```bash
   python transcribe.py --input sample.wav --output transcript.txt
   ```
3. Использовать конкретную модель (например, medium):
   ```bash
   python transcribe.py --input sample.wav --model medium
   ```
4. Принудительно указать язык (например, русский):
   ```bash
   python transcribe.py --input sample.wav --language ru
   ```

## Параметры

- `--input` (обязательный): путь к аудиофайлу для транскрибации
- `--output`: путь для сохранения результата (по умолчанию вывод в консоль)
- `--model`: название модели fast-whisper (`tiny`, `base`, `small`, `medium`, `large`)
- `--language`: язык аудио (например, `ru` для русского, `en` для английского). Если не указан, определяется автоматически

## Возможные проблемы

- Если скрипт не видит ffmpeg, убедитесь, что он установлен и добавлен в PATH
- Для больших моделей требуется больше оперативной памяти
- Если возникают ошибки с зависимостями, попробуйте обновить pip и переустановить зависимости

## Лицензия

MIT License

## Контакты

По вопросам и предложениям: [issues на GitHub](https://github.com/nivedano/russian-whisper/issues)
