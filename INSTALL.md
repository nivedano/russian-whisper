# Russian Whisper: Installation and Usage

## Installation

This project requires **Python 3.11**. We've provided setup scripts for both Windows and Linux/macOS to make installation straightforward.

### Windows

```powershell
.\setup.ps1
```

### Linux/macOS

```bash
chmod +x setup.sh
./setup.sh
```

These scripts will:

1. Check if Python 3.11 is installed (and help you install it if needed)
2. Create a virtual environment in `.venv`
3. Install all dependencies, including PyTorch with CUDA support if available

## Running the Application

You can run the application in multiple ways:

### Option 1: Using the transcribe scripts (recommended)

We've provided convenient scripts that use Python directly from the virtual environment:

#### Windows

```powershell
.\transcribe.ps1 [arguments]
```

#### Linux/macOS

```bash
chmod +x transcribe.sh
./transcribe.sh [arguments]
```

Example with arguments:

```bash
./transcribe.sh speech.mp3 transcript.txt
./transcribe.sh /path/to/audio/files /path/to/output --segments
```

### Option 2: Making the script accessible from anywhere

You can add the script to your PATH or create a symbolic link in a directory that's already in your PATH:

#### Windows (PowerShell)

```powershell
# Create a directory for scripts if needed
mkdir -Force ~/bin
# Create a hard link to the script
New-Item -ItemType HardLink -Path ~/bin/transcribe.ps1 -Value $PWD/transcribe.ps1
# Add ~/bin to PATH if not already there
if ($env:PATH -notlike "*$HOME\bin*") { 
    [Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";$HOME\bin", "User")
    Write-Host "Added ~/bin to PATH. You may need to restart your terminal."
}
```

#### Linux/macOS

```bash
# Create a directory for scripts if needed
mkdir -p ~/bin
# Create a hard link to the script
ln -f transcribe ~/bin/transcribe
# Make it executable
chmod +x ~/bin/transcribe
# Add ~/bin to PATH if not already there
if [[ ":$PATH:" != *":$HOME/bin:"* ]]; then
    echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
    echo "Added ~/bin to PATH. Run 'source ~/.bashrc' or restart your terminal."
fi
```

After adding to your PATH, you can run the script from anywhere:

```bash
transcribe speech.mp3 transcript.txt
transcribe /path/to/audio/folder /path/to/output/folder --segments
```

### Option 3: Manually activating the environment

First, activate the environment:

#### Windows

```powershell
.\.venv\Scripts\Activate.ps1
```

#### Linux/macOS

```bash
source .venv/bin/activate
```

Then run the application:

```bash
python transcribe.py [arguments]
```

## Manual Installation

If you prefer to install manually:

1. Install Python 3.11 from [python.org](https://www.python.org/downloads/)
2. Create a virtual environment: `python -m venv .venv`
3. Activate it:
   - Windows: `.\.venv\Scripts\activate`
   - Linux/macOS: `source .venv/bin/activate`
4. Install the standard dependencies: `pip install -r requirements.txt`  
   (Note: This may fail with the PyTorch CUDA packages)
5. For PyTorch with CUDA support:

   ```bash
   pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu121
   ```
