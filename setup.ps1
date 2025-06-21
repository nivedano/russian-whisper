# Setup script for the Russian Whisper application
# This script checks for Python 3.11, installs it if missing, and sets up the environment

# Configuration
$pythonVersion = "3.11"
$envDir = ".venv"
$requirementsFile = "requirements.txt"

# Function to check if Python version is installed
function Test-PythonVersion {
    param (
        [string]$Version
    )
    
    try {
        $result = py -$Version --version
        if ($result -match "Python $Version") {
            return $true
        }
    } catch {
        # Python launcher not found or version not available
    }
    
    try {
        $result = python --version
        if ($result -match "Python $Version") {
            return $true
        }
    } catch {
        # Python not found
    }
    
    return $false
}

# Function to install Python using winget
function Install-Python {
    param (
        [string]$Version
    )
    
    Write-Host "Installing Python $Version using winget..."
    
    try {
        # Check if winget is available
        $wingetCheck = winget --version
        if (-not $?) {
            throw "Winget is not available on this system. Please install Python $Version manually from https://www.python.org/downloads/"
        }
        
        # Install Python using winget
        winget install Python.Python.$($Version.Replace('.', ''))
        
        if (-not $?) {
            throw "Failed to install Python using winget"
        }
        
        Write-Host "Python $Version installed successfully. You may need to restart your terminal."
        return $true
    } catch {
        Write-Host "Error: $_"
        Write-Host "Please install Python $Version manually from https://www.python.org/downloads/"
        return $false
    }
}

# Function to create and activate virtual environment
function Setup-VirtualEnv {
    param (
        [string]$Version,
        [string]$EnvDir
    )
    
    Write-Host "Setting up virtual environment in $EnvDir..."
    
    # Create the virtual environment
    py -$Version -m venv $EnvDir
    
    if (-not $?) {
        Write-Host "Failed to create virtual environment. Trying with python command..."
        python -m venv $EnvDir
        
        if (-not $?) {
            Write-Host "Error: Failed to create virtual environment."
            return $false
        }
    }
    
    # Activate the virtual environment
    Write-Host "Activating virtual environment..."
    & "$EnvDir\Scripts\Activate.ps1"
    
    if (-not $?) {
        Write-Host "Error: Failed to activate virtual environment."
        return $false
    }
    
    # Upgrade pip
    python -m pip install --upgrade pip
    
    return $true
}

# Function to modify the requirements file to handle PyTorch correctly
function Update-RequirementsForTorch {
    param (
        [string]$RequirementsPath
    )
    
    $content = Get-Content $RequirementsPath -Raw
    
    # Replace CUDA-specific PyTorch packages with versions that don't specify CUDA
    $updatedContent = $content -replace 'torch==2.5.1\+cu121', 'torch==2.5.1'
    $updatedContent = $updatedContent -replace 'torchaudio==2.5.1\+cu121', 'torchaudio==2.5.1'
    $updatedContent = $updatedContent -replace 'torchvision==0.20.1\+cu121', 'torchvision==0.20.1'
    
    # Create a temporary file with updated content
    $tempFile = "$RequirementsPath.tmp"
    $updatedContent | Out-File -FilePath $tempFile -Encoding utf8
    
    # Replace the original file
    Move-Item -Path $tempFile -Destination $RequirementsPath -Force
    
    Write-Host "Updated requirements file to use standard PyTorch packages."
}

# Function to install PyTorch with CUDA support manually
function Install-PyTorchCUDA {
    param (
        [string]$TorchVersion = "2.5.1",
        [string]$CudaVersion = "12.1"
    )
    
    Write-Host "Installing PyTorch $TorchVersion with CUDA $CudaVersion support..."
    
    $command = "pip3 install torch==$TorchVersion torchvision torchaudio --index-url https://download.pytorch.org/whl/cu$($CudaVersion.Replace('.', ''))"
    Invoke-Expression $command
    
    if (-not $?) {
        Write-Host "Failed to install PyTorch with CUDA support. Falling back to standard PyTorch..."
        pip install torch==$TorchVersion torchvision torchaudio
    }
}

# Function to install requirements
function Install-Requirements {
    param (
        [string]$RequirementsPath
    )
    
    Write-Host "Installing dependencies from $RequirementsPath..."
    
    # First try to install all packages except torch, torchaudio, and torchvision
    $content = Get-Content $RequirementsPath
    $filteredContent = $content | Where-Object { $_ -notmatch "torch|torchaudio|torchvision" }
    $tempFile = "$RequirementsPath.filtered"
    $filteredContent | Out-File -FilePath $tempFile -Encoding utf8
    
    # Install filtered requirements
    pip install -r $tempFile
    
    # Install PyTorch with CUDA
    Install-PyTorchCUDA
    
    # Clean up
    Remove-Item -Path $tempFile -Force
}

# Main script execution
Write-Host "Checking for Python $pythonVersion..."
$pythonInstalled = Test-PythonVersion -Version $pythonVersion

if (-not $pythonInstalled) {
    Write-Host "Python $pythonVersion not found."
    $installed = Install-Python -Version $pythonVersion
    
    if (-not $installed) {
        Write-Host "Please install Python $pythonVersion manually and run this script again."
        exit 1
    }
    
    Write-Host "Please restart your terminal and run this script again to continue setup."
    exit 0
}

Write-Host "Python $pythonVersion found."

$envSetup = Setup-VirtualEnv -Version $pythonVersion -EnvDir $envDir

if (-not $envSetup) {
    Write-Host "Failed to set up virtual environment. Please check the error messages above."
    exit 1
}

Update-RequirementsForTorch -RequirementsPath $requirementsFile
Install-Requirements -RequirementsPath $requirementsFile

Write-Host "`nSetup completed successfully!"
Write-Host "To activate the environment in the future, run: $envDir\Scripts\Activate.ps1"
Write-Host "To run the application, use: python transcribe.py"
