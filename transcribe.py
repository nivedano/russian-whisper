#!/usr/bin/env python3
'''
Russian audio transcription using faster-whisper
Optimized for best performance with Russian language audio
Supports processing individual files or entire directories
'''
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='ctranslate2')
from faster_whisper import WhisperModel
import time
import sys
import os
import glob
from pathlib import Path

class RussianWhisperTranscriber:
    def __init__(self, model_name='large-v3', device_preference='cuda', cpu_threads=4, dry_run=False):
        self.model_name = model_name
        self.device_preference = device_preference
        self.cpu_threads = cpu_threads
        if not dry_run:
            self.model = self._init_model()

    def _init_model(self):
        try:
            model = WhisperModel(self.model_name, device=self.device_preference, compute_type='float16')
            print(f'Используется ускорение {self.device_preference.upper()}')
        except Exception:
            model = WhisperModel(self.model_name, device='cpu', compute_type='int8', cpu_threads=self.cpu_threads)
            print(f'Используется CPU с {self.cpu_threads} потоками')
        return model

    def find_audio_files(self, directory_path):
        supported_extensions = ['*.mp3', '*.wav', '*.flac', '*.m4a', '*.aac', '*.ogg', '*.wma']
        audio_files = []
        directory = Path(directory_path)
        if not directory.exists():
            print(f'Ошибка: Папка {directory_path} не существует')
            return []
        for ext in supported_extensions:
            pattern = directory / ext
            files = glob.glob(str(pattern), recursive=False)
            audio_files.extend(files)
            pattern_recursive = directory / '**' / ext
            files_recursive = glob.glob(str(pattern_recursive), recursive=True)
            audio_files.extend(files_recursive)
        audio_files = sorted(list(set(audio_files)))
        print(f'Найдено {len(audio_files)} аудиофайлов в {directory_path}:')
        for file in audio_files:
            print(f'  - {os.path.basename(file)}')
        return audio_files

    def transcribe_russian_audio(self, audio_file, output_file=None, print_segments=False, echo: bool = True, dry_run: bool = False):
        print(f'Распознавание: {audio_file}')
        if output_file is None:
            output_file = str(Path(audio_file).with_suffix('.txt'))
        if dry_run:
            print(f'[симуляция] Было бы сохранено в: {output_file}')
            return []
        start_time = time.time()
        segments, info = self.model.transcribe(
            audio_file,
            language='ru',
            beam_size=5,
            best_of=5,
            temperature=0.0,
            word_timestamps=True,
            vad_filter=True,
            vad_parameters=dict(
                min_silence_duration_ms=500,
                threshold=0.5,
                min_speech_duration_ms=250
            ),
            initial_prompt='Русская речь, четкое произношение'
        )
        print(f'Обнаружен язык: {info.language} (уверенность: {info.language_probability:.2f})')
        print(f'Длительность: {info.duration:.2f} секунд')
        transcription_lines = []
        for segment in segments:
            segment_desc = f'[{segment.start:.2f}с -> {segment.end:.2f}с]' if print_segments else ''
            line = f'{segment_desc} {segment.text.strip()}'
            transcription_lines.append(line)
            if echo:
                print(line)
        end_time = time.time()
        print(f'\nРаспознавание завершено за {end_time - start_time:.2f} секунд')
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                for line in transcription_lines:
                    f.write(line + '\n')
            print(f'Результат сохранён в: {output_file}')
        return transcription_lines

    def batch_transcribe_directory(self, directory_path, output_dir=None, print_segments=False, dry_run: bool = False):
        audio_files = self.find_audio_files(directory_path)
        if not audio_files:
            print('Аудиофайлы не найдены!')
            return
        if output_dir is None:
            output_dir = directory_path
        output_path = Path(output_dir)
        if not dry_run:
            output_path.mkdir(parents=True, exist_ok=True)
        total_files = len(audio_files)
        successful = 0
        failed = 0
        for i, audio_file in enumerate(audio_files, 1):
            # Light green color for header
            print(f'\033[92mОбработка файла {i}/{total_files}: {os.path.basename(audio_file)}\033[0m')
            try:
                base_name = Path(audio_file).stem
                output_file = output_path / f'{base_name}.txt'
                self.transcribe_russian_audio(audio_file, str(output_file), print_segments=print_segments, dry_run=dry_run)
                successful += 1
            except Exception as e:
                print(f'Ошибка при обработке {audio_file}: {str(e)}')
                failed += 1
        print(f'Пакетная обработка завершена')
        print(f'Успешно обработано: {successful} файлов')
        print(f'Ошибок: {failed} файлов')
        print(f'Всего файлов: {total_files}')
        print(f'Результаты сохранены в: {output_path}')

    def batch_transcribe(self, audio_files, print_segments=False, dry_run: bool = False):
        for audio_file in audio_files:
            print(f'\n{"="*50}')
            self.transcribe_russian_audio(audio_file, print_segments=print_segments, dry_run=dry_run)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Использование:')
        print('  Один файл: python transcribe.py <аудиофайл> [файл_результата] [--segments] [--dry-run]')
        print('  Папка:     python transcribe.py <папка_аудио> [папка_результата] [--segments] [--dry-run]')
        print()
        print('Примеры:')
        print('  python transcribe.py speech.mp3 transcript.txt')
        print('  python transcribe.py /path/to/audio/files')
        print('  python transcribe.py /path/to/audio/files /path/to/output')
        print('  python transcribe.py /path/to/audio/files /path/to/output --segments')
        print('  python transcribe.py /path/to/audio/files /path/to/output --dry-run')
        sys.exit(1)
    input_path = sys.argv[1]
    print_segments = '--segments' in sys.argv
    dry_run = '--dry-run' in sys.argv
    transcriber = RussianWhisperTranscriber(dry_run=dry_run)
    # Check if input is a directory or file
    if os.path.isdir(input_path):
        output_dir = None
        for arg in sys.argv[2:]:
            if not arg.startswith('--'):
                output_dir = arg
                break
        print(f'Обработка папки: {input_path}')
        transcriber.batch_transcribe_directory(input_path, output_dir, print_segments=print_segments, dry_run=dry_run)
    elif os.path.isfile(input_path):
        output_file = None
        for arg in sys.argv[2:]:
            if not arg.startswith('--'):
                output_file = arg
                break
        print(f'Обработка одного файла: {input_path}')
        transcriber.transcribe_russian_audio(input_path, output_file, print_segments=print_segments, dry_run=dry_run)
    else:
        print(f'Ошибка: {input_path} не является файлом или папкой')
        sys.exit(1)