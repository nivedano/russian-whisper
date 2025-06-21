#!/bin/bash
# Setup script for the Russian Whisper application
# This script checks for Python 3.11, installs it if missing, and sets up the environment

# Configuration
PYTHON_VERSION="3.11"
ENV_DIR=".venv"
REQUIREMENTS_FILE="requirements.txt"

# Function to check if Python version is installed
check_python_version() {
    local version=$1
    if command -v python$version &> /dev/null; then
        return 0
    elif command -v python3.$version &> /dev/null; then
        return 0
    elif command -v python3 &> /dev/null && [[ $(python3 --version | grep -oP '(?<=Python )\d+\.\d+') == $version ]]; then
        return 0
    fi
    return 1
}

# Function to suggest Python installation based on OS
suggest_python_installation() {
    local version=$1
    echo "Python $version is not installed."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get &> /dev/null; then
            echo "Try installing with: sudo apt-get update && sudo apt-get install python${version}"
        elif command -v dnf &> /dev/null; then
            echo "Try installing with: sudo dnf install python${version}"
        elif command -v yum &> /dev/null; then
            echo "Try installing with: sudo yum install python${version}"
        elif command -v pacman &> /dev/null; then
            echo "Try installing with: sudo pacman -S python${version}"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &> /dev/null; then
            echo "Try installing with: brew install python@${version}"
        else
            echo "Try installing Homebrew first (https://brew.sh), then run: brew install python@${version}"
        fi
    fi
    
    echo "Alternatively, download Python $version from https://www.python.org/downloads/"
    echo "After installing Python $version, run this script again."
    exit 1
}

# Function to create and activate virtual environment
setup_virtual_env() {
    local version=$1
    local env_dir=$2
    
    echo "Setting up virtual environment in $env_dir..."
    
    # Find the correct Python executable
    PYTHON_CMD=""
    if command -v python$version &> /dev/null; then
        PYTHON_CMD="python$version"
    elif command -v python3.$version &> /dev/null; then
        PYTHON_CMD="python3.$version"
    elif command -v python3 &> /dev/null && [[ $(python3 --version | grep -oP '(?<=Python )\d+\.\d+') == $version ]]; then
        PYTHON_CMD="python3"
    else
        echo "Error: Python $version not found even though it was checked earlier."
        exit 1
    fi
    
    # Create the virtual environment
    $PYTHON_CMD -m venv $env_dir
    
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment."
        exit 1
    fi
    
    # Activate the virtual environment
    source "$env_dir/bin/activate"
    
    if [ $? -ne 0 ]; then
        echo "Error: Failed to activate virtual environment."
        exit 1
    fi
    
    # Upgrade pip
    pip install --upgrade pip
}

# Function to modify the requirements file to handle PyTorch correctly
update_requirements_for_torch() {
    local requirements_path=$1
    
    # Create a backup
    cp "$requirements_path" "${requirements_path}.bak"
    
    # Replace CUDA-specific PyTorch packages with versions that don't specify CUDA
    sed -i'' -e 's/torch==2.5.1+cu121/torch==2.5.1/g' "$requirements_path"
    sed -i'' -e 's/torchaudio==2.5.1+cu121/torchaudio==2.5.1/g' "$requirements_path"
    sed -i'' -e 's/torchvision==0.20.1+cu121/torchvision==0.20.1/g' "$requirements_path"
    
    echo "Updated requirements file to use standard PyTorch packages."
}

# Function to install PyTorch with CUDA support manually
install_pytorch_cuda() {
    local torch_version=${1:-"2.5.1"}
    local cuda_version=${2:-"12.1"}
    
    echo "Installing PyTorch $torch_version with CUDA $cuda_version support..."
    
    local cuda_ver_no_dot=${cuda_version//./}
    pip install torch==$torch_version torchvision torchaudio --index-url https://download.pytorch.org/whl/cu$cuda_ver_no_dot
    
    if [ $? -ne 0 ]; then
        echo "Failed to install PyTorch with CUDA support. Falling back to standard PyTorch..."
        pip install torch==$torch_version torchvision torchaudio
    fi
}

# Function to install requirements
install_requirements() {
    local requirements_path=$1
    
    echo "Installing dependencies from $requirements_path..."
    
    # First try to install all packages except torch, torchaudio, and torchvision
    grep -v -E "torch|torchaudio|torchvision" "$requirements_path" > "${requirements_path}.filtered"
    
    # Install filtered requirements
    pip install -r "${requirements_path}.filtered"
    
    # Install PyTorch with CUDA
    install_pytorch_cuda
    
    # Clean up
    rm "${requirements_path}.filtered"
}

# Main script execution
echo "Checking for Python $PYTHON_VERSION..."
if check_python_version $PYTHON_VERSION; then
    echo "Python $PYTHON_VERSION found."
else
    suggest_python_installation $PYTHON_VERSION
fi

setup_virtual_env $PYTHON_VERSION $ENV_DIR
update_requirements_for_torch $REQUIREMENTS_FILE
install_requirements $REQUIREMENTS_FILE

echo -e "\nSetup completed successfully!"
echo "To activate the environment in the future, run: source $ENV_DIR/bin/activate"
echo "To run the application, use: python transcribe.py"
