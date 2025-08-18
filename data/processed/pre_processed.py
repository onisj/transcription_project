import os
import sys
import shutil
import json
from pydub import AudioSegment
from pymongo import MongoClient
from datetime import datetime

# Ensure Python recognizes this directory as a package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# Import DataCrawler
from data.raw.data_crawler import DataCrawler

# MongoDB Setup
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "transcription_db"

# Directories (Ensure they match the crawler output)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Raw Directories (Source)
RAW_AUDIO_DIR = os.path.join(BASE_DIR, "data", "raw", "extracted_audio")
RAW_TEXT_DIR = os.path.join(BASE_DIR, "data", "raw", "text")

# Processed Directories (Destination)
PROCESSED_AUDIO_DIR = os.path.join(BASE_DIR, "data", "processed", "audio")
PROCESSED_TEXT_DIR = os.path.join(BASE_DIR, "data", "processed", "text")
PROCESSED_JSON_DIR = os.path.join(PROCESSED_TEXT_DIR, "json")
PROCESSED_HTM_DIR = os.path.join(PROCESSED_TEXT_DIR, "html")

# Converted Audio Directory
CONVERTED_AUDIO_DIR = os.path.join(PROCESSED_AUDIO_DIR, "converted_audio")

# Ensure Output Directories Exist
os.makedirs(PROCESSED_AUDIO_DIR, exist_ok=True)
os.makedirs(PROCESSED_TEXT_DIR, exist_ok=True)
os.makedirs(PROCESSED_JSON_DIR, exist_ok=True)
os.makedirs(PROCESSED_HTM_DIR, exist_ok=True)
os.makedirs(CONVERTED_AUDIO_DIR, exist_ok=True)


class DataPreprocessor:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.log_collection = self.db.process_logs  # Store only process metadata

    def log_process(self, action, status, details):
        """Log metadata of the process in MongoDB."""
        self.log_collection.insert_one({
            "action": action,
            "status": status,
            "details": details,
            "timestamp": datetime.utcnow()
        })

    def ensure_directory_exists(self, file_path):
        """Ensure that the output directory exists before writing the file."""
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"Created directory: {directory}")

    def ensure_audio_folder_structure(self):
        """Ensure all folders in /raw/extracted_audio/ exist in /processed/audio/converted_audio/."""
        for root, dirs, _ in os.walk(RAW_AUDIO_DIR):
            for dir_name in dirs:
                raw_subdir = os.path.join(root, dir_name)
                relative_path = os.path.relpath(raw_subdir, RAW_AUDIO_DIR)
                processed_subdir = os.path.join(CONVERTED_AUDIO_DIR, relative_path)

                os.makedirs(processed_subdir, exist_ok=True)
                print(f"Ensured folder exists: {processed_subdir}")

    def run_crawler_if_needed(self):
        """Runs DataCrawler only if raw data is missing for ANY language."""
        required_dirs = {
            "english_json": os.path.join(RAW_TEXT_DIR, "english", "kjv", "mp3bible", "json"),
            "hausa_audio": os.path.join(RAW_AUDIO_DIR, "hausa"),
            "igbo_audio": os.path.join(RAW_AUDIO_DIR, "igbo"),
            "yoruba_audio": os.path.join(RAW_AUDIO_DIR, "yoruba", "naijasermons"),
        }

        missing_data = [lang for lang, path in required_dirs.items() if not os.path.exists(path) or not os.listdir(path)]

        if not missing_data:
            print("All raw data found. Skipping DataCrawler.")
        else:
            print(f"Missing raw data for: {', '.join(missing_data)}. Running DataCrawler...")
            crawler = DataCrawler()
            crawler.run_all_crawlers()
            self.log_process("run_crawler", "completed", {"missing_data": missing_data})

    def convert_audio(self, input_path, output_path):
        """Convert audio to 16kHz mono WAV and save to output directory."""
        try:
            # Skip conversion if the file already exists in MongoDB or filesystem
            if os.path.exists(output_path):
                print(f"Skipping conversion (file already exists): {output_path}")
                return

            # Check MongoDB logs to see if file was already converted
            if self.db.process_logs.find_one({"action": "convert_audio", "converted": output_path}):
                print(f"Skipping conversion (file already logged in MongoDB): {output_path}")
                return

            self.ensure_directory_exists(output_path)
            audio = AudioSegment.from_file(input_path)
            audio = audio.set_frame_rate(16000).set_channels(1)
            audio.export(output_path, format="wav")
            print(f"🎵 Converted: {output_path}")

            # Log the successful conversion in MongoDB
            self.log_process("convert_audio", "success", {
                "original": input_path,
                "converted": output_path
            })

        except Exception as e:
            print(f"Error processing {input_path}: {e}")
            self.log_process("convert_audio", "failed", {
                "original": input_path,
                "error": str(e)
            })


    def process_audio_files(self):
        """Convert raw audio files to 16kHz WAV and save to the correct processed directory."""
        print("Converting audio files...")

        # Ensure we are processing only KJV MP3 Bible files
        audio_source_dirs = [
            os.path.join(RAW_AUDIO_DIR, "english", "kjv", "mp3bible"),  # Correct KJV directory
        ]

        for audio_source_dir in audio_source_dirs:
            for root, _, files in os.walk(audio_source_dir):
                for file in files:
                    if file.endswith(".mp3") or file.endswith(".wav"):
                        input_path = os.path.join(root, file)

                        # Maintain correct relative path from `mp3bible/`
                        relative_path = os.path.relpath(input_path, audio_source_dir)
                        output_path = os.path.join(CONVERTED_AUDIO_DIR, "english", "kjv", "mp3bible", relative_path).replace(".mp3", ".wav")

                        # Ensure correct directory exists
                        self.ensure_directory_exists(output_path)

                        # Convert and save
                        self.convert_audio(input_path, output_path)


    def process_json_files(self):
        """Move JSON files to processed directory if they can be validated."""
        print("Processing JSON files...")

        json_source_dirs = [
            os.path.join(RAW_TEXT_DIR, "english", "kjv", "mp3bible", "json"),
        ]

        for json_source_dir in json_source_dirs:
            for root, _, files in os.walk(json_source_dir):
                for file in files:
                    if file.endswith(".json"):
                        input_path = os.path.join(root, file)
                        relative_path = os.path.relpath(input_path, json_source_dir)
                        output_path = os.path.join(PROCESSED_JSON_DIR, relative_path)

                        try:
                            with open(input_path, "r", encoding="utf-8") as f:
                                json.load(f)

                            print(f"Valid JSON: {input_path}")
                            self.ensure_directory_exists(output_path)
                            shutil.move(input_path, output_path)
                            print(f"Moved: {input_path} → {output_path}")

                            # Log process
                            self.log_process("process_json", "success", {
                                "original": input_path,
                                "processed": output_path
                            })

                        except json.JSONDecodeError as e:
                            print(f"Invalid JSON: {input_path} - {e}")
                            self.log_process("process_json", "failed", {
                                "original": input_path,
                                "error": str(e)
                            })

    def run_pipeline(self):
        """Run full preprocessing pipeline."""
        self.ensure_audio_folder_structure()
        self.run_crawler_if_needed()
        self.process_audio_files()
        self.process_json_files()
        self.log_process("run_pipeline", "completed", {"message": "Data processing pipeline finished"})
        print("Data processing pipeline completed!")

if __name__ == "__main__":
    processor = DataPreprocessor()
    processor.run_pipeline()
