import os
import re
import json
import requests
import zipfile
import shutil
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote
from pymongo import MongoClient
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError, AuthRestartError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Telegram API credentials from .env
API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
PHONE = os.getenv("TELEGRAM_PHONE")

# MongoDB Setup
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "transcription_db"

# Ensure correct base directory
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Directories
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
TEXT_DIR = os.path.join(BASE_DIR, "data", "raw", "text")
EXTRACT_DIR = os.path.join(BASE_DIR, "data", "raw", "extracted_audio")

AUDIO_DIR = os.path.join(BASE_DIR, "data", "raw", "audio")
YORUBA_DIR = os.path.join(AUDIO_DIR, "yoruba", "naijasermons")
HAUSA_DIR = os.path.join(EXTRACT_DIR, "hausa")
IGBO_DIR = os.path.join(EXTRACT_DIR, "igbo")

# Bible Text Directories
HTM_FOLDER = os.path.join(TEXT_DIR, "english", "kjv", "mp3bible", "html")
JSON_FOLDER = os.path.join(TEXT_DIR, "english", "kjv", "mp3bible", "json")
ZIP_FOLDER = os.path.join(TEXT_DIR, "zipped")

# Add these lines to the directory setup section
MP3_BIBLE_ZIP_DIR = os.path.join(AUDIO_DIR, "english", "kjv", "mp3bible", "zipped")
MP3_BIBLE_EXTRACT_DIR = os.path.join(EXTRACT_DIR, "english", "kjv", "mp3bible")

# Ensure directories exist
os.makedirs(YORUBA_DIR, exist_ok=True)
os.makedirs(HAUSA_DIR, exist_ok=True)
os.makedirs(IGBO_DIR, exist_ok=True)
os.makedirs(HTM_FOLDER, exist_ok=True)
os.makedirs(JSON_FOLDER, exist_ok=True)
os.makedirs(ZIP_FOLDER, exist_ok=True)
os.makedirs(MP3_BIBLE_ZIP_DIR, exist_ok=True)
os.makedirs(MP3_BIBLE_EXTRACT_DIR, exist_ok=True)

# Language Subdirectories
LANGUAGES = {
    "english": ["kjv/mp3bible", "kjv/naijasermon"],
    "yoruba": ["kjv/naijasermon"],
    "igbo": [],
    "hausa": []
}

# Ensure directories exist
for lang, subdirs in LANGUAGES.items():
    lang_audio_path = os.path.join(AUDIO_DIR, lang)
    lang_extract_path = os.path.join(EXTRACT_DIR, lang)
    os.makedirs(lang_audio_path, exist_ok=True)
    os.makedirs(lang_extract_path, exist_ok=True)
    for subdir in subdirs:
        os.makedirs(os.path.join(lang_audio_path, subdir), exist_ok=True)
        os.makedirs(os.path.join(lang_extract_path, subdir), exist_ok=True)

# Bible Sources
MP3_BIBLE_URL = "https://www.mp3bible.ca/"
YORUBA_BIBLE_URL = "https://naijasermons.com.ng/download-yoruba-audio-bible-mp3/"
TEXT_BIBLE_URL = "https://www.mp3bible.ca/KJV_text/"

# Telegram Channels and Specific Message IDs
TELEGRAM_CHANNELS = {
    "igbo": ("compiledteachings", [284]),  # (Channel Name, [Message IDs])
    "hausa": ("compiledteachings", [283])
}

class DataCrawler:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.telegram_client = TelegramClient("telegram_session", API_ID, API_HASH)

        # Ensure the database and collections exist
        self._ensure_database_and_collections()

    def _ensure_database_and_collections(self):
        """Ensure the database and required collections exist."""
        # List of required collections
        required_collections = ["raw_audio", "raw_text"]

        # Get existing collections in the database
        existing_collections = self.db.list_collection_names()

        # Create collections if they don't exist
        for collection in required_collections:
            if collection not in existing_collections:
                print(f"Creating collection: {collection}")
                self.db.create_collection(collection)

        print("Database and collections are ready.")

    def extract_zip(self, file_path, extract_path, language):
        """ Extract ZIP files if valid and store metadata in MongoDB, but skip if already extracted. """
        print(f"Attempting to extract {file_path} to {extract_path}...")

        # Check if extraction directory already contains files
        if os.path.exists(extract_path) and os.listdir(extract_path):
            print(f"Skipping extraction: {extract_path} already contains extracted files.")
            return  # Skip extraction

        if not os.path.exists(file_path):
            print(f"ZIP file not found: {file_path}")
            return

        if not zipfile.is_zipfile(file_path):
            print(f"Not a valid ZIP file: {file_path}")
            return

        try:
            os.makedirs(extract_path, exist_ok=True)
            with zipfile.ZipFile(file_path, "r") as zip_ref:
                zip_ref.extractall(extract_path)
                print(f"Extracted: {file_path} to {extract_path}")

            # Update status in MongoDB
            self.db.raw_audio.update_one(
                {"file_path": file_path},
                {"$set": {"status": "extracted", "extracted_path": extract_path}}
            )
            print(f"Stored extraction metadata in MongoDB for: {file_path}")

        except Exception as e:
            print(f"Extraction failed for {file_path}: {e}")

    def fetch_telegram_audio(self):
        """ Download ZIP files from Telegram channels and store metadata in MongoDB. """
        print("Fetching large audio files from Telegram...")

        # Start the Telegram client session
        self.telegram_client.connect()

        if not self.telegram_client.is_user_authorized():
            try:
                self.telegram_client.send_code_request(PHONE)
                code = input("Enter the code you received: ")
                self.telegram_client.sign_in(PHONE, code)

            except AuthRestartError:
                print("Telegram requires re-authentication. Restarting process...")
                self.telegram_client.send_code_request(PHONE)
                code = input("Enter the new code you received: ")
                self.telegram_client.sign_in(PHONE, code)

            except SessionPasswordNeededError:
                password = input("Enter your Telegram password: ")
                self.telegram_client.sign_in(password=password)

        print("Logged into Telegram.")

        for lang, (channel, message_ids) in TELEGRAM_CHANNELS.items():
            extract_path = os.path.join(EXTRACT_DIR, lang)
            os.makedirs(extract_path, exist_ok=True)

            print(f"Fetching ZIP files from {channel} for {lang}...")

            for message_id in message_ids:
                message = self.telegram_client.get_messages(channel, ids=message_id)

                if message and message.file and message.file.name.endswith(".zip"):
                    save_path = os.path.join(AUDIO_DIR, lang, message.file.name)

                    if os.path.exists(save_path):
                        print(f"Skipping {message.file.name}, already downloaded.")
                    else:
                        print(f"Downloading {message.file.name} ({message.file.size / 1024 / 1024:.2f} MB)...")
                        message.download_media(file=save_path)

                        # Store metadata in MongoDB
                        self.db.raw_audio.insert_one({
                            "source": "telegram",
                            "language": lang,
                            "file_name": message.file.name,
                            "file_path": save_path,
                            "status": "downloaded"
                        })
                        print(f"Stored metadata in MongoDB: {save_path}")

                    # **LOGGING ADDED**
                    print(f"Extracting {save_path} to {extract_path}...")
                    
                    # Call extraction
                    self.extract_zip(save_path, extract_path, lang)

        self.telegram_client.disconnect()
        print("Telegram audio download completed.")


    def fetch_mp3_bible_audio(self):
        """Fetch and extract MP3 Bible audio files from MP3_BIBLE_URL."""
        print("Fetching MP3 Bible audio files...")

        # Fetch all ZIP file links
        response = requests.get(MP3_BIBLE_URL)
        soup = BeautifulSoup(response.text, "html.parser")
        zip_links = [
            urljoin(MP3_BIBLE_URL, tag["href"])
            for tag in soup.find_all("a", href=True)
            if tag["href"].endswith(".zip") and "-KJV_Bible" in tag["href"] and "LARGE" not in tag["href"]
        ]

        print(f"Found {len(zip_links)} ZIP files to download.")

        for link in zip_links:
            file_name = os.path.basename(link)
            save_path = os.path.join(MP3_BIBLE_ZIP_DIR, file_name)

            # Download the ZIP file if it doesn't already exist
            if os.path.exists(save_path):
                print(f"Skipping download (already exists): {save_path}")
            else:
                print(f"Downloading {file_name}...")
                with requests.get(link, stream=True) as r:
                    r.raise_for_status()
                    with open(save_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)

            # Extract the ZIP file
            print(f"Extracting {file_name}...")
            self.extract_zip(save_path, MP3_BIBLE_EXTRACT_DIR, "english")

            # Store metadata in MongoDB
            self.db.raw_audio.insert_one({
                "source": "mp3_bible",
                "language": "english",
                "file_name": file_name,
                "file_path": save_path,
                "status": "extracted",
                "extracted_path": MP3_BIBLE_EXTRACT_DIR
            })
            print(f"Stored metadata in MongoDB: {save_path}")

        print("MP3 Bible audio download and extraction completed.")


    def get_html_links(self, url):
        """Fetches all .HTM file links from the given URL."""
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        links = []
        for link in soup.find_all("a", href=True):
            file_url = urljoin(url, link["href"])
            if file_url.endswith(".HTM") or file_url.endswith(".htm"):
                links.append(file_url)

        print(f"Found {len(links)} HTM files to download: {links}")
        return links

    def download_file(self, url, save_path):
        """Downloads and saves a file from a URL if it does not already exist."""
        if os.path.exists(save_path):
            print(f"Skipping download, file already exists: {save_path}")
            return False  # Indicate that no download occurred

        response = requests.get(url)
        response.raise_for_status()
        with open(save_path, "wb") as file:
            file.write(response.content)

        print(f"Downloaded: {save_path}")
        return True  # Indicate that a new file was downloaded

    def fetch_bible_text(self):
        """Fetches HTM Bible files and converts them to JSON, skipping existing files."""
        print("Fetching Bible text files...")

        html_links = self.get_html_links(TEXT_BIBLE_URL)
        if not html_links:
            print("No HTM files found. Check the source URL.")
            return

        for link in html_links:
            file_name = os.path.basename(link)
            htm_path = os.path.join(HTM_FOLDER, file_name)
            json_filename = file_name.replace(".HTM", ".json").replace(".htm", ".json")
            json_path = os.path.join(JSON_FOLDER, json_filename)

            # Skip download if the file already exists
            if not self.download_file(link, htm_path):
                print(f"Skipping conversion, file already exists: {json_path}")
                continue  # Skip conversion since the file was not newly downloaded

            # Convert to JSON
            self.convert_htm_to_json(htm_path, json_path)

        print("All HTM files successfully processed.")

    def convert_htm_to_json(self, htm_file, json_file):
        """Converts a single .HTM Bible file into JSON format if it does not already exist."""
        if os.path.exists(json_file):
            print(f"Skipping conversion, JSON already exists: {json_file}")
            return  # Skip conversion

        with open(htm_file, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")

        # Extract book title
        title_tag = soup.find("title")
        book_title = title_tag.text.strip() if title_tag else "Unknown Book"

        # Extract verses
        verses = []
        for row in soup.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) >= 2:
                verse_id = cols[0].text.strip()
                verse_text = cols[1].text.strip()
                verses.append({"verse": verse_id, "text": verse_text})

        print(f"Extracted {len(verses)} verses from {htm_file}")

        # Create JSON structure
        bible_data = {"book": book_title, "verses": verses}

        # Write to JSON
        with open(json_file, "w", encoding="utf-8") as json_out:
            json.dump(bible_data, json_out, indent=4, ensure_ascii=False)

        print(f"Converted {htm_file} -> {json_file}")

    def zip_htm_files(self):
        """Zips the HTM files folder and stores metadata in MongoDB."""
        zip_path = os.path.join(ZIP_FOLDER, "bible_text_htm.zip")

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(HTM_FOLDER):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, HTM_FOLDER))

        print(f"Zipped HTM files: {zip_path}")

        # Store metadata in MongoDB
        self.db.raw_text.insert_one({
            "source": "bible_htm",
            "file_name": "bible_text_htm.zip",
            "file_path": zip_path,
            "status": "backup_saved"
        })
        print("Stored metadata in MongoDB.")


    def rename_file(self, file_url):
        """ Rename Yoruba Bible filenames for consistency. """
        basename = os.path.basename(file_url)
        decoded_name = unquote(basename)
        decoded_name = decoded_name.replace(" Audio Bible (Yoruba)", "").replace(".mp3", "")
        
        match = re.match(r"^(\d+)\.\s*(.+)$", decoded_name)
        if match:
            num = match.group(1)
            book_name = match.group(2).replace(" ", "_")
            return f"{num}.{book_name}.mp3"
        return basename
    
    
    def fetch_yoruba_audio(self):
        """Scrape and download Yoruba audio from NaijaSermon, storing metadata in MongoDB."""
        print("Fetching Yoruba audio from NaijaSermon...")
        download_folder = os.path.join(EXTRACT_DIR, "yoruba", "kjv", "naijasermon")
        os.makedirs(download_folder, exist_ok=True)

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/115.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(YORUBA_BIBLE_URL, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")

        mp3_links = [
            urljoin(YORUBA_BIBLE_URL, tag["href"])
            for tag in soup.find_all("a", href=True)
            if re.search(r'\.mp3$', tag["href"], re.IGNORECASE)
        ]

        print(f"Found {len(mp3_links)} Yoruba MP3 files.")

        for link in mp3_links:
            new_filename = self.rename_file(link)
            local_filename = os.path.join(download_folder, new_filename)

            if os.path.exists(local_filename):
                print(f"Skipping {new_filename}, file already exists.")
                continue

            print(f"Downloading {new_filename}...")
            with requests.get(link, headers=headers, stream=True) as r:
                r.raise_for_status()
                with open(local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

            # Store metadata in MongoDB
            self.db.raw_audio.insert_one({
                "source": "yoruba_audio",
                "file_name": new_filename,
                "file_path": local_filename,
                "status": "downloaded"
            })
            print(f"Stored metadata in MongoDB: {new_filename}")
    

    def run_all_crawlers(self):
        """Run all crawlers."""
        self.fetch_telegram_audio()
        self.fetch_yoruba_audio()
        self.fetch_mp3_bible_audio()
        self.fetch_bible_text()
        self.zip_htm_files()
        print("All data crawlers executed successfully!")

if __name__ == "__main__":
    crawler = DataCrawler()
    crawler.run_all_crawlers()