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

    def find_audio_files(self, directory: Path):
        supported_extensions = ['*.mp3', '*.wav', '*.flac', '*.m4a', '*.aac', '*.ogg', '*.wma']
        audio_files = []
        if not directory.exists():
            print(f'Ошибка: Папка {directory} не существует')
            return []
        for ext in supported_extensions:
            pattern = directory / ext
            files = glob.glob(str(pattern), recursive=False)
            audio_files.extend(files)
            pattern_recursive = directory / '**' / ext
            files_recursive = glob.glob(str(pattern_recursive), recursive=True)
            audio_files.extend(files_recursive)
        # Convert all paths to Path objects and remove duplicates
        audio_files = sorted(list(set([Path(file) for file in audio_files])))
        print(f'Найдено аудиофайлов: {len(audio_files)}')
        for file in audio_files:
            print(f'  - {file.name}')
        return audio_files

    def transcribe_russian_audio(self, 
            audio_file: Path, 
            output_file: Path | None = None, 
            print_segments: bool = False, 
            echo: bool = True, 
            dry_run: bool = False,
            resume_time: int | None = None):
        if output_file is None:
            output_file = audio_file.with_suffix('.txt')
        
        if dry_run:
            print(f'  [симуляция] Было бы сохранено в: {output_file}')
            return []
        
        print(f'  Сохраняем в {output_file.name}')
        start_time = time.time()
        segments, info = self.model.transcribe(
            str(audio_file),  # Convert Path to string for the model
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
        print(f'  Обнаружен язык: \033[92m{info.language}\033[0m (уверенность: \033[92m{info.language_probability:.2f}\033[0m)')
        print(f'  Длительность: \033[92m{info.duration:.2f}\033[0m секунд')
        transcription_lines = []
        # If resume_time is set, append to file, else overwrite
        file_mode = 'a' if resume_time is not None else 'w'
        f = open(output_file, file_mode, encoding='utf-8')
        try:
            for segment in segments:
                if resume_time is not None and segment.start < resume_time:
                    continue
                if print_segments:
                    line = f'[{segment.start:.2f} -> {segment.end:.2f}] {segment.text.strip()}'
                else:
                    line = segment.text.strip()
                transcription_lines.append(line)
                if echo:
                    print(f'\033[90m {segment.end / info.duration * 100:6.2f}%\033[0m {int(segment.end):3}c | {line}')
                f.write(line + '\n')
                f.flush()
            end_time = time.time()
            print(f'\nРаспознавание завершено за {end_time - start_time:.2f} секунд')
        finally:
            f.close()

    def batch_transcribe_directory(self, 
            directory_path: Path, 
            output_dir: Path | None = None, 
            print_segments: bool = False, 
            dry_run: bool = False):
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
            print(f'\033[92mОбработка файла {i}/{total_files}: {audio_file.name}\033[0m')
            try:
                audio_path = Path(audio_file)
                base_name = audio_path.stem
                output_file = output_path / f'{base_name}.txt'
                self.transcribe_russian_audio(audio_path, output_file, print_segments=print_segments, dry_run=dry_run)
                successful += 1
            except Exception as e:
                print(f'Ошибка при обработке {audio_file}: {str(e)}')
                failed += 1
        print(f'Пакетная обработка завершена')
        print(f'Успешно обработано: {successful} файлов')
        print(f'Ошибок в файлах: {failed}')
        print(f'Всего файлов: {total_files}')
        print(f'Результаты сохранены в: {output_path}')

    def batch_transcribe(self, audio_files, print_segments=False, dry_run: bool = False):
        for audio_file in audio_files:
            print(f'\n{"="*50}')
            self.transcribe_russian_audio(audio_file, print_segments=print_segments, dry_run=dry_run)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Использование:')
        print('  Один файл: python transcribe.py <аудиофайл> [файл_результата] [--segments] [--dry-run] [--resume-time <секунды>]')
        print('  Папка:     python transcribe.py <папка_аудио> [папка_результата] [--segments] [--dry-run] [--resume-time <секунды>]')
        print()
        print('Примеры:')
        print('  python transcribe.py speech.mp3 transcript.txt')
        print('  python transcribe.py /path/to/audio/files')
        print('  python transcribe.py /path/to/audio/files /path/to/output')
        print('  python transcribe.py /path/to/audio/files /path/to/output --segments')
        print('  python transcribe.py /path/to/audio/files /path/to/output --dry-run')
        print('  python transcribe.py /path/to/audio/files /path/to/output --resume-time 120')
        sys.exit(1)
    input_path = sys.argv[1]
    print_segments = '--segments' in sys.argv
    dry_run = '--dry-run' in sys.argv
    resume_time = None
    if '--resume-time' in sys.argv:
        idx = sys.argv.index('--resume-time')
        if idx + 1 < len(sys.argv):
            try:
                resume_time = int(sys.argv[idx + 1])
            except ValueError:
                print('Ошибка: --resume-time требует целое число (секунды)')
                sys.exit(1)
        else:
            print('Ошибка: --resume-time требует значение (секунды)')
            sys.exit(1)
    try:
        transcriber = RussianWhisperTranscriber(dry_run=dry_run)
        # Check if input is a directory or file
        input_path = Path(input_path)
        if input_path.is_dir():
            if resume_time is not None:
                print('Ошибка: --resume-time можно использовать только для одного файла, а не для папки!')
                sys.exit(1)
            output_dir = None
            for arg in sys.argv[2:]:
                if not arg.startswith('--'):
                    output_dir = Path(arg)
                    break
            print(f'Обработка папки: \033[92m{input_path}\033[0m')
            transcriber.batch_transcribe_directory(input_path, output_dir, print_segments=print_segments, dry_run=dry_run)
        elif input_path.is_file():
            output_file = None
            for arg in sys.argv[2:]:
                if not arg.startswith('--'):
                    output_file = Path(arg)
                    break
            print(f'Обработка одного файла: {input_path}')
            transcriber.transcribe_russian_audio(input_path, output_file, print_segments=print_segments, dry_run=dry_run, resume_time=resume_time)
        else:
            print(f'Ошибка: {input_path} не является файлом или папкой')
            sys.exit(1)
    except KeyboardInterrupt:
        print('\nПрерывание пользователем. Завершение работы.')
        sys.exit(0)