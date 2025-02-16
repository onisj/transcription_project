from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["transcription_db"]

# Fetch all stored ZIP files
zip_files = db.raw_audio.find()

print("\n📂 ZIP Files in MongoDB:")
for file in zip_files:
    print(f"📌 Full Document: {file}")  # Print entire document to see actual keys


# Find the zip file in MongoDB
record = db.raw_text.find_one({"file_name": "bible_text_htm.zip"})

if record:
    zip_path = "retrieved_bible_text_htm.zip"
    with open(zip_path, "wb") as f:
        f.write(record["data"])  # Save the binary data as a zip file

    print(f"✅ Retrieved and saved: {zip_path}")

    # Extract the zip
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        extract_path = "extracted_htm_files"
        zip_ref.extractall(extract_path)
        print(f"📂 Extracted to: {extract_path}")