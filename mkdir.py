import os

# Define the full project directory structure
project_structure = {
    "transcription_project": {
        "data": {
            "raw": {},
            "processed": {},
            "annotations": {},
            "splits": {},
        },
        "models": {
            "text_to_text": {},
            "speech_to_text": {},
            "text_to_speech": {},
        },
        "notebooks": {
            "data_exploration.ipynb": "",
            "model_training.ipynb": "",
            "preprocessing.ipynb": "",
        },
        "backend": {
            "app": {
                "__init__.py": "",
                "routes.py": "",
                "models.py": "",
                "utils.py": "",
            },
            "requirements.txt": "",
            "Dockerfile": "",
            "run.py": "",
        },
        "frontend": {
            "public": {},
            "src": {
                "components": {},
                "pages": {},
                "App.js": "",
                "index.js": "",
                "styles.css": "",
            },
            "package.json": "",
            "README.md": "",
        },
        "mobile": {
            "lib": {
                "screens": {},
                "widgets": {},
                "services": {},
                "main.dart": "",
                "App.js": "",
            },
            "assets": {},
            "pubspec.yaml": "",
            "package.json": "",
            "README.md": "",
        },
        "scripts": {
            "preprocess_data.py": "",
            "train_model.py": "",
            "evaluate_model.py": "",
        },
        "tests": {
            "backend_tests": {},
            "frontend_tests": {},
            "mobile_tests": {},
        },
        "config": {
            "config.yaml": "",
            "model_config.yaml": "",
            "deployment_config.yaml": "",
        },
        "docs": {
            "project_overview.md": "",
            "api_documentation.md": "",
            "user_manual.md": "",
        },
        ".gitignore": "",
        "README.md": "",
        "requirements.txt": "",
    }
}

# Function to create directories and files
def create_structure(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            # Create directory and recurse
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            # Create an empty file
            with open(path, "w") as f:
                pass

# Main function
def main():
    project_name = "transcription_project"
    base_path = os.path.join(os.getcwd(), project_name)
    create_structure(base_path, project_structure[project_name])
    print(f"Project directory structure created at: {base_path}")

if __name__ == "__main__":
    main()