# Russian Whisper: Installation and Usage (uv)

## Installation

This project is managed with **uv** and is known to work on **Python 3.11**.

Note: The current dependency set targets **Windows/Linux** (CUDA wheels). If you need macOS support, you’ll likely need to adjust the Torch dependencies in `pyproject.toml`.

### 1) Install uv

Follow the official instructions: [docs.astral.sh/uv](https://docs.astral.sh/uv/)

### 2) Create the environment and install dependencies

From the repository root:

```bash
uv sync
```

This will create a `.venv` and install dependencies using `uv.lock`.

If you want to force Python 3.11 explicitly (optional):

```bash
uv python install 3.11
uv sync --python 3.11
```

### 3) Optional: install ffmpeg

`ffmpeg` helps with broad audio format support.

- Windows: download from [ffmpeg.org/download.html](https://ffmpeg.org/download.html)
- Linux: `sudo apt install ffmpeg`
- macOS: `brew install ffmpeg`

## Running the Application

### Option 1: Run with uv (default)

```bash
uv run python transcribe.py [arguments]
```

Windows example:

```powershell
uv run .\transcribe.py "C:\\path\\to\\audio.m4a"
```

### Option 2: Use the provided helper scripts

These scripts run the project’s `.venv` Python directly (no activation needed). They assume you already ran `uv sync`.

#### Windows

```powershell
.\transcribe.ps1 [arguments]
```

#### Linux/macOS

```bash
chmod +x ./transcribe.sh
./transcribe.sh [arguments]
```

### Option 3: Make a "transcribe" command on your PATH

#### Windows (PowerShell)

```powershell
mkdir -Force ~/bin
New-Item -ItemType HardLink -Path ~/bin/transcribe.ps1 -Value $PWD/transcribe.ps1
if ($env:PATH -notlike "*$HOME\bin*") {
   [Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";$HOME\bin", "User")
   Write-Host "Added ~/bin to PATH. Restart your terminal to pick it up."
}
```

#### Linux/macOS

```bash
mkdir -p ~/bin
ln -f "$PWD/transcribe.sh" ~/bin/transcribe
chmod +x ~/bin/transcribe
if [[ ":$PATH:" != *":$HOME/bin:"* ]]; then
   echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
   echo "Added ~/bin to PATH. Run 'source ~/.bashrc' or restart your terminal."
fi
```

Then:

```bash
transcribe speech.mp3 transcript.txt
transcribe /path/to/audio/folder /path/to/output/folder --segments
```
