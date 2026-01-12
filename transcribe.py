#!/usr/bin/env python3
'''
Russian audio transcription using faster-whisper
Optimized for best performance with Russian language audio
Supports processing individual files or entire directories
'''
from typing import Iterable, Tuple
import warnings
import subprocess
import shutil
import tempfile
import hashlib

warnings.filterwarnings('ignore', category=UserWarning, module='ctranslate2')
from faster_whisper import WhisperModel
import time
import sys
import os
import glob
import soundfile as sf
from pathlib import Path


class UnsupportedAudioFormatError(RuntimeError):
    pass


class AdjustedSegment:
    def __init__(self, original, time_offset):
        self.start = original.start + time_offset
        self.end = original.end + time_offset
        self.text = original.text

class RussianWhisperTranscriber:
    def __init__(self, model_name='turbo', device_preference='cuda', cpu_threads=4, dry_run=False):
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
            resume_time: int = 0,
            use_ffmpeg: bool = True):
        if output_file is None:
            output_file = audio_file.with_suffix('.txt')
        
        if dry_run:
            print(f'  [симуляция] Было бы сохранено в: {output_file}')
            return []
        
        print(f'  Сохраняем в \033[92m{output_file.name}\033[0m')

        readable_path, info = self._get_readable_audio_path_and_info(audio_file, output_file=output_file, use_ffmpeg=use_ffmpeg)
        print(f'  Длительность: \033[92m{info.duration:.2f}\033[0m секунд')
        start_time = time.time()
        segments, _ = self._transcribe_audio_with_duration_strategy(str(readable_path), info.duration, resume_time)
        file_mode = 'a' if resume_time else 'w'
        with open(output_file, file_mode, encoding='utf-8') as f:
            self._process_segments(f, segments, info.duration, print_segments, echo)
            end_time = time.time()
            print(f'\nРаспознавание завершено за {end_time - start_time:.2f} секунд')

    def _get_readable_audio_path_and_info(self, audio_file: Path, output_file: Path, use_ffmpeg: bool) -> tuple[Path, sf._SoundFileInfo]:
        try:
            return audio_file, sf.info(str(audio_file))
        except sf.LibsndfileError as e:
            if not use_ffmpeg:
                raise UnsupportedAudioFormatError(self._humanize_soundfile_error(audio_file, e, ffmpeg_enabled=False)) from None

            ffmpeg_path = shutil.which('ffmpeg')
            if not ffmpeg_path:
                raise UnsupportedAudioFormatError(self._humanize_soundfile_error(audio_file, e, ffmpeg_enabled=True, ffmpeg_found=False)) from None

            converted = self._ffmpeg_convert_to_wav(audio_file, output_file=output_file, ffmpeg_path=ffmpeg_path)
            try:
                info = sf.info(str(converted))
            except sf.LibsndfileError as e2:
                raise UnsupportedAudioFormatError(self._humanize_soundfile_error(audio_file, e2, ffmpeg_enabled=True, ffmpeg_found=True)) from None
            return converted, info

    def _ffmpeg_convert_to_wav(self, audio_file: Path, output_file: Path, ffmpeg_path: str) -> Path:
        cache_dir = output_file.parent / '.russian-whisper-cache'
        try:
            cache_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            cache_dir = Path(tempfile.gettempdir()) / 'russian-whisper-cache'
            cache_dir.mkdir(parents=True, exist_ok=True)

        try:
            stat = audio_file.stat()
            key = f'{audio_file.resolve()}|{stat.st_size}|{stat.st_mtime_ns}'.encode('utf-8', errors='ignore')
        except Exception:
            key = str(audio_file).encode('utf-8', errors='ignore')

        digest = hashlib.sha1(key).hexdigest()[:12]
        out_path = cache_dir / f'{audio_file.stem}.{digest}.wav'
        if out_path.exists():
            print(f'  Используем кэш WAV: \033[90m{out_path.name}\033[0m')
            return out_path

        print('  Формат не поддерживается soundfile — пробуем декодировать через ffmpeg...')
        cmd = [
            ffmpeg_path,
            '-hide_banner',
            '-loglevel', 'error',
            '-y',
            '-i', str(audio_file),
            '-ac', '1',
            '-ar', '16000',
            '-vn',
            str(out_path),
        ]
        completed = subprocess.run(cmd, capture_output=True, text=True)
        if completed.returncode != 0 or not out_path.exists():
            details = (completed.stderr or completed.stdout or '').strip()
            if details:
                details = '\n' + details
            raise UnsupportedAudioFormatError(
                'ffmpeg не смог декодировать файл.\n'
                f'Файл: {audio_file}\n'
                f'Команда: {" ".join(cmd)}{details}'
            )
        return out_path

    def _humanize_soundfile_error(self, audio_file: Path, err: Exception, ffmpeg_enabled: bool = True, ffmpeg_found: bool = True) -> str:
        suffix = audio_file.suffix.lower()
        path_str = str(audio_file)
        format_hint = ''
        if suffix in {'.m4a', '.aac', '.wma', '.mp4'}:
            format_hint = (
                'Похоже, это контейнер/кодек, который libsndfile (пакет soundfile) не умеет читать на вашей системе.\n'
            )

        ffmpeg_note = ''
        if not ffmpeg_enabled:
            ffmpeg_note = 'Авто-конвертация через ffmpeg отключена (флаг --no-ffmpeg).\n'
        elif not ffmpeg_found:
            ffmpeg_note = 'ffmpeg не найден в PATH. Установите ffmpeg или сконвертируйте файл вручную.\n'
        else:
            ffmpeg_note = 'Если установлен ffmpeg, скрипт обычно может конвертировать такие файлы автоматически.\n'

        quoted_in = f'"{path_str}"'
        quoted_out = f'"{audio_file.with_suffix(".wav")}"'

        return (
            'Не удалось открыть аудиофайл (soundfile/libsndfile): формат не распознан.\n'
            f'Файл: {path_str}\n'
            f'Формат: {suffix or "(без расширения)"}\n'
            f'{format_hint}'
            f'{ffmpeg_note}'
            'Что делать:\n'
            '1) Самый простой путь — конвертировать в WAV (моно, 16 kHz) и запустить снова:\n'
            f'   ffmpeg -hide_banner -y -i {quoted_in} -ac 1 -ar 16000 {quoted_out}\n'
            '2) Или конвертировать в MP3:\n'
            f'   ffmpeg -hide_banner -y -i {quoted_in} -codec:a libmp3lame -q:a 2 "{audio_file.with_suffix(".mp3")}"\n'
            'Если после конвертации всё равно ошибка — попробуйте WAV/FLAC и убедитесь, что файл не повреждён.\n'
            f'Техническая причина: {err}'
        )
    
    def _transcribe_audio_with_duration_strategy(self, audio_file_path: str, duration: float, resume_time: int = 0):
        """Transcribe audio with parameters adapted to file duration"""
        
        base_params = {
            'language': 'ru',
            'word_timestamps': True,
            'vad_filter': True,
            'vad_parameters': dict(
                min_silence_duration_ms=500,
                threshold=0.5,
                min_speech_duration_ms=250
            ),
            'initial_prompt': 'Русская речь, четкое произношение'
        }

        params = self._get_transcription_params(duration, resume_time)
        final_params = {**base_params, **params}        
        return self.model.transcribe(audio_file_path, **final_params)
    
    def _get_transcription_params(self, duration: float, resume_time: int = 0):
        """Get transcription parameters based on audio duration and resume status"""
        base_params = {
            'beam_size': 5,
            'best_of': 5
        }

        if resume_time >= duration:
            raise ValueError('Время возобновления выходит за длину аудиофайла.')
        if resume_time > 0:
            print(f'  Возобновление с {resume_time}с')
            base_params['clip_timestamps'] = resume_time

        # Always use prevention settings for resume points
        if resume_time or duration > 3600:  # > 1 hour
            base_params.update({
                'condition_on_previous_text': False,
                # 'temperature': [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
                # 'compression_ratio_threshold': 1.35,
                # 'no_speech_threshold': 0.3,
                'repetition_penalty': 1.2,
                # 'no_repeat_ngram_size': 3
            }) # type: ignore
        elif duration > 1800:  # 30-60 minutes
            base_params.update({
                'condition_on_previous_text': True,
                # 'temperature': [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
                # 'compression_ratio_threshold': 1.8,
                # 'no_speech_threshold': 0.45,
                'repetition_penalty': 1.1,
                # 'no_repeat_ngram_size': 2
            }) # type: ignore
        else:  # < 30 minutes
            base_params.update({
                'condition_on_previous_text': True,
                # 'temperature': 0.0,
                # 'compression_ratio_threshold': 2.4,
                # 'no_speech_threshold': 0.6,
                'repetition_penalty': 1.0
            }) # type: ignore
        
        return base_params
        
    def _process_segments(self, f, segments, total_duration: float, print_segments: bool, echo: bool):
        for segment in segments:
            if print_segments:
                line = f'[{segment.start:.2f} -> {segment.end:.2f}] {segment.text.strip()}'
            else:
                line = segment.text.strip()
            if echo:
                print(f'\033[90m {segment.end / total_duration * 100:6.2f}%\033[0m {int(segment.end):3}c | {line}')
            if f:
                f.write(line + '\n')
                f.flush()
        

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
    if sys.argv[1] in ('-d', '--diagnostics'):
        import torch
        print(f"PyTorch version: {torch.__version__}")
        print(f"CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"CUDA version: {torch.version.cuda}") # type: ignore
            print(f"GPU count: {torch.cuda.device_count()}")
            current_device = torch.cuda.current_device()
            print(f"Current GPU: {current_device} ({torch.cuda.get_device_name(current_device)})")
            gpu_memory_gb = torch.cuda.get_device_properties(current_device).total_memory / (1024**3)
            gpu_free_memory_gb = (torch.cuda.get_device_properties(current_device).total_memory - torch.cuda.memory_allocated(current_device)) / (1024**3)
            print(f"Total GPU memory: {gpu_memory_gb:.1f} GB")
            print(f"Free GPU memory: {gpu_free_memory_gb:.1f} GB")
            print(""" Model memory requirements:
    tiny: 0.5
    base: 1.0
    small: 2.0
    medium: 5.0
    large: 10.0
    large:2': 10.0
    large:3': 10.0
    turbo: 3.0
""")
        sys.exit(0)
    input_path = sys.argv[1]
    print_segments = '--segments' in sys.argv
    dry_run = '--dry-run' in sys.argv
    use_ffmpeg = '--no-ffmpeg' not in sys.argv
    resume_time = None
    if '--resume-time' in sys.argv:
        idx = sys.argv.index('--resume-time')
        if idx + 1 < len(sys.argv):
            try:
                resume_time = int(sys.argv[idx + 1])
                if resume_time < 0:
                    print('Ошибка: --resume-time должно быть неотрицательным числом')
                    sys.exit(1)
                # Remove --resume-time and its value from sys.argv
                del sys.argv[idx:idx+2]
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
            transcriber.transcribe_russian_audio(
                input_path,
                output_file,
                print_segments=print_segments,
                dry_run=dry_run,
                resume_time=resume_time or 0,
                use_ffmpeg=use_ffmpeg,
            )
        else:
            print(f'Ошибка: {input_path} не является файлом или папкой')
            sys.exit(1)
    except UnsupportedAudioFormatError as e:
        print(str(e))
        sys.exit(2)
    except KeyboardInterrupt:
        print('\nПрерывание пользователем. Завершение работы.')
        sys.exit(0)