# PowerShell transcribe script for Russian Whisper
# Usage: transcribe <аудиофайл | папка_аудио> [файл_результата | папка_результата] [--segments] [--dry-run]
# Examples:
#   transcribe speech.mp3 transcript.txt
#   transcribe /path/to/audio/files
#   transcribe /path/to/audio/files /path/to/output
#   transcribe /path/to/audio/files /path/to/output --segments

# Find the actual location of this script, even when symlinked
$scriptPath = $MyInvocation.MyCommand.Path
$scriptDir = Split-Path -Parent $scriptPath

# Configuration - find project directory even when script is symlinked
$projectDir = $scriptDir
if (-not (Test-Path -Path "$projectDir\.venv")) {
    # If we're symlinked from another directory, try to find the project dir
    $projectDir = Split-Path -Parent $scriptDir
    if (-not (Test-Path -Path "$projectDir\.venv")) {
        # One more try - maybe we're in a bin subdirectory?
        $projectDir = Split-Path -Parent $projectDir
    }
}

$envDir = "$projectDir\.venv"
$appScript = "$projectDir\transcribe.py"

# Get all arguments passed to this script
$scriptArgs = $args

# Check if virtual environment exists
if (-not (Test-Path -Path "$envDir\Scripts\python.exe")) {
    Write-Host "Virtual environment not found. Please run setup.ps1 in the project directory first."
    exit 1
}

# Use Python directly from the virtual environment without activating it
& "$envDir\Scripts\python.exe" $appScript $scriptArgs

# Exit with the same exit code as the Python script
exit $LASTEXITCODE
