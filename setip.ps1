Write-Host "Starting setup for Windows..."

# Define project name and virtual environment directory
$ProjectName = "transcription_project"
$VenvDir = "$ProjectName\venv"

# Step 1: Create Project Directory Structure
Write-Host "Creating project directory structure..."
New-Item -ItemType Directory -Force -Path "$ProjectName\data\raw", "$ProjectName\data\processed", "$ProjectName\data\annotations", "$ProjectName\data\splits"
New-Item -ItemType Directory -Force -Path "$ProjectName\models\text_to_text", "$ProjectName\models\speech_to_text", "$ProjectName\models\text_to_speech"
New-Item -ItemType Directory -Force -Path "$ProjectName\notebooks", "$ProjectName\backend\app", "$ProjectName\frontend\public", "$ProjectName\frontend\src\components", "$ProjectName\frontend\src\pages"
New-Item -ItemType Directory -Force -Path "$ProjectName\mobile\lib\screens", "$ProjectName\mobile\lib\widgets", "$ProjectName\mobile\lib\services", "$ProjectName\mobile\assets"
New-Item -ItemType Directory -Force -Path "$ProjectName\scripts", "$ProjectName\tests\backend_tests", "$ProjectName\tests\frontend_tests", "$ProjectName\tests\mobile_tests"
New-Item -ItemType Directory -Force -Path "$ProjectName\config", "$ProjectName\docs"

# Create placeholder files
New-Item -ItemType File -Path "$ProjectName\notebooks\data_exploration.ipynb", "$ProjectName\notebooks\model_training.ipynb", "$ProjectName\notebooks\preprocessing.ipynb"
New-Item -ItemType File -Path "$ProjectName\backend\app\__init__.py", "$ProjectName\backend\app\routes.py", "$ProjectName\backend\app\models.py", "$ProjectName\backend\app\utils.py"
New-Item -ItemType File -Path "$ProjectName\backend\requirements.txt", "$ProjectName\backend\Dockerfile", "$ProjectName\backend\run.py"
New-Item -ItemType File -Path "$ProjectName\frontend\src\App.js", "$ProjectName\frontend\src\index.js", "$ProjectName\frontend\src\styles.css"
New-Item -ItemType File -Path "$ProjectName\frontend\package.json", "$ProjectName\frontend\README.md"
New-Item -ItemType File -Path "$ProjectName\mobile\lib\main.dart", "$ProjectName\mobile\lib\App.js"
New-Item -ItemType File -Path "$ProjectName\mobile\pubspec.yaml", "$ProjectName\mobile\package.json", "$ProjectName\mobile\README.md"
New-Item -ItemType File -Path "$ProjectName\scripts\preprocess_data.py", "$ProjectName\scripts\train_model.py", "$ProjectName\scripts\evaluate_model.py"
New-Item -ItemType File -Path "$ProjectName\config\config.yaml", "$ProjectName\config\model_config.yaml", "$ProjectName\config\deployment_config.yaml"
New-Item -ItemType File -Path "$ProjectName\docs\project_overview.md", "$ProjectName\docs\api_documentation.md", "$ProjectName\docs\user_manual.md"
New-Item -ItemType File -Path "$ProjectName\.gitignore", "$ProjectName\README.md", "$ProjectName\requirements.txt"

Write-Host "Project structure created successfully!"

# Step 2: Install System Dependencies
if (-Not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Host "Installing FFmpeg..."
    choco install ffmpeg -y
}

if (-Not (Get-Command yt-dlp -ErrorAction SilentlyContinue)) {
    Write-Host "Installing yt-dlp..."
    choco install yt-dlp -y
}

# Step 3: Set Up Virtual Environment
Write-Host "Setting up Python virtual environment..."
python -m venv $VenvDir

# Activate Virtual Environment
Write-Host "Activating virtual environment..."
& "$VenvDir\Scripts\Activate.ps1"

# Step 4: Install Python Dependencies
Write-Host "Installing Python dependencies..."
pip install --upgrade pip
pip install -r "$ProjectName\requirements.txt"

Write-Host "Setup complete! 🎉 Virtual environment is activated."
Write-Host "To activate later, run: & '$VenvDir\Scripts\Activate.ps1'"
