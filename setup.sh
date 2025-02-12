#!/bin/bash

echo "Starting setup for macOS/Linux..."

# Detect OS
OS="$(uname -s)"
case "$OS" in
    Darwin*)  OS="macOS" ;;
    Linux*)   OS="Linux" ;;
    *)        OS="Unknown" ;;
esac

echo "Detected OS: $OS"

# Define project name and virtual environment directory
PROJECT_NAME="transcription_project"
VENV_DIR="$PROJECT_NAME/venv"

# Step 1: Create Project Directory Structure
echo "Creating project directory structure..."
mkdir -p ${PROJECT_NAME}/{data/{raw,processed,annotations,splits},models/{text_to_text,speech_to_text,text_to_speech},notebooks,backend/app,frontend/{public,src/{components,pages}},mobile/{lib/{screens,widgets,services},assets},scripts,tests/{backend_tests,frontend_tests,mobile_tests},config,docs}

# Create placeholder files
touch ${PROJECT_NAME}/notebooks/{data_exploration.ipynb,model_training.ipynb,preprocessing.ipynb}
touch ${PROJECT_NAME}/backend/app/{__init__.py,routes.py,models.py,utils.py}
touch ${PROJECT_NAME}/backend/{requirements.txt,Dockerfile,run.py}
touch ${PROJECT_NAME}/frontend/src/{App.js,index.js,styles.css}
touch ${PROJECT_NAME}/frontend/{package.json,README.md}
touch ${PROJECT_NAME}/mobile/lib/{main.dart,App.js}
touch ${PROJECT_NAME}/mobile/{pubspec.yaml,package.json,README.md}
touch ${PROJECT_NAME}/scripts/{preprocess_data.py,train_model.py,evaluate_model.py}
touch ${PROJECT_NAME}/config/{config.yaml,model_config.yaml,deployment_config.yaml}
touch ${PROJECT_NAME}/docs/{project_overview.md,api_documentation.md,user_manual.md}
touch ${PROJECT_NAME}/.gitignore
touch ${PROJECT_NAME}/README.md
touch ${PROJECT_NAME}/requirements.txt

echo "Project structure created successfully!"

# Step 2: Install System Dependencies (FFmpeg, yt-dlp)
if [[ "$OS" == "macOS" ]]; then
    if ! command -v brew &>/dev/null; then
        echo "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    echo "Installing FFmpeg and yt-dlp..."
    brew install ffmpeg yt-dlp
elif [[ "$OS" == "Linux" ]]; then
    if command -v apt &>/dev/null; then
        echo "Installing FFmpeg and yt-dlp (Debian/Ubuntu)..."
        sudo apt update && sudo apt install -y ffmpeg yt-dlp
    elif command -v dnf &>/dev/null; then
        echo "Installing FFmpeg and yt-dlp (Fedora)..."
        sudo dnf install -y ffmpeg yt-dlp
    elif command -v pacman &>/dev/null; then
        echo "Installing FFmpeg and yt-dlp (Arch Linux)..."
        sudo pacman -S --noconfirm ffmpeg yt-dlp
    else
        echo "Unsupported Linux distribution. Install FFmpeg and yt-dlp manually."
    fi
fi

# Step 3: Set Up Virtual Environment
echo "Setting up Python virtual environment..."
python3 -m venv "$VENV_DIR"

# Activate Virtual Environment
source "$VENV_DIR/bin/activate"

# Step 4: Install Python Dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r ${PROJECT_NAME}/requirements.txt

echo "Setup complete! 🎉 Virtual environment is activated."
echo "To activate later, run: source $VENV_DIR/bin/activate"
