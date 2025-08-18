# Configuration Guide

This document explains how to configure the transcription backend application using environment variables and the centralized settings system.

## Environment Variables (.env file)

The application uses a `.env` file in the backend directory to store configuration values. Create or modify this file to customize your setup.

### Database Configuration
```env
MONGO_URI=mongodb://localhost:27017/
DB_NAME=transcription_db
```

### Server Configuration
```env
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

### Whisper Model Configuration
```env
WHISPER_MODEL_SIZE=small
SAMPLE_RATE=16000
CHUNK_DURATION=2.0
```

**Available Whisper Models:**
- `tiny`: Fastest, least accurate
- `base`: Good balance of speed and accuracy
- `small`: Better accuracy, slower (default)
- `medium`: High accuracy, slower
- `large`: Best accuracy, slowest

### Audio Processing
```env
MAX_AUDIO_BUFFER_SIZE=10
MIN_CHUNKS_FOR_TRANSCRIPTION=2
```

### CORS Configuration
```env
ALLOWED_ORIGINS=["*"]
ALLOW_CREDENTIALS=true
```

**Production CORS Settings:**
```env
ALLOWED_ORIGINS=["https://yourdomain.com", "https://app.yourdomain.com"]
ALLOW_CREDENTIALS=false
```

### Logging
```env
LOG_LEVEL=INFO
```

**Available Log Levels:**
- `DEBUG`: Detailed information
- `INFO`: General information (default)
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical errors

### Supported Languages
```env
SUPPORTED_LANGUAGES=["auto", "en", "yo", "ig", "ha"]
```

**Available Languages:**
- `auto`: Auto-detect language
- `en`: English
- `yo`: Yoruba
- `ig`: Igbo
- `ha`: Hausa

## Settings Module (settings.py)

The `app/settings.py` module automatically loads environment variables and provides:

- **Type-safe configuration values**
- **Default values for missing environment variables**
- **Computed properties** (e.g., `CHUNK_SIZE` calculated from `SAMPLE_RATE` and `CHUNK_DURATION`)
- **Centralized configuration management**

### Usage in Code

```python
from app.settings import HOST, PORT, WHISPER_MODEL_SIZE

# Use configuration values
whisper_model = whisper.load_model(WHISPER_MODEL_SIZE)
```

### Available Settings

```python
# Database
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "transcription_db"
DATABASE_URL = "mongodb://localhost:27017/transcription_db"

# Server
HOST = "0.0.0.0"
PORT = 8000
DEBUG = True

# Whisper
WHISPER_MODEL_SIZE = "small"
SAMPLE_RATE = 16000
CHUNK_DURATION = 2.0
CHUNK_SIZE = 32000  # Computed: SAMPLE_RATE * CHUNK_DURATION

# Audio Processing
MAX_AUDIO_BUFFER_SIZE = 10
MIN_CHUNKS_FOR_TRANSCRIPTION = 2

# CORS
ALLOWED_ORIGINS = ["*"]
ALLOW_CREDENTIALS = True

# Logging
LOG_LEVEL = "INFO"

# Languages
SUPPORTED_LANGUAGES = ["auto", "en", "yo", "ig", "ha"]
```

## Frontend Configuration

The frontend React app has its own `.env` file that should reference the backend configuration:

```env
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_WS_BASE_URL=ws://localhost:8000
```

## Mobile Configuration

The Flutter mobile app uses `lib/config.dart` with environment variable support:

```bash
flutter run --dart-define=API_BASE_URL=http://your-backend-url
flutter run --dart-define=WS_BASE_URL=ws://your-backend-url
```

## Running with Custom Configuration

### Using Environment Variables
```bash
export MONGO_URI="mongodb://your-mongo-server:27017/"
export WHISPER_MODEL_SIZE="medium"
python -m uvicorn app.realtime_transcription:app --host 0.0.0.0 --port 8000
```

### Using .env File
```bash
# Modify backend/.env file
# Then run normally
python -m uvicorn app.realtime_transcription:app --host 0.0.0.0 --port 8000
```

### Using run.py
```bash
# Uses settings from .env automatically
python run.py
```

## Production Deployment

For production deployment:

1. **Set `DEBUG=false`**
2. **Configure specific `ALLOWED_ORIGINS`**
3. **Use production MongoDB URI**
4. **Set appropriate `LOG_LEVEL`**
5. **Consider using `WHISPER_MODEL_SIZE=medium` for better accuracy**

```env
DEBUG=false
ALLOWED_ORIGINS=["https://yourdomain.com"]
MONGO_URI=mongodb://your-production-mongo:27017/
LOG_LEVEL=WARNING
WHISPER_MODEL_SIZE=medium
```

## Troubleshooting

### Common Issues

1. **Configuration not loading**: Ensure `.env` file is in the backend directory
2. **Import errors**: Check that `python-dotenv` is installed
3. **Type errors**: Verify environment variable values match expected types
4. **CORS issues**: Check `ALLOWED_ORIGINS` configuration

### Validation

The settings module automatically validates and converts environment variables. Check the logs for any configuration warnings or errors.

