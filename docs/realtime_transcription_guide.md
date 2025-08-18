# Real-Time Nigerian Language Transcription - Complete Implementation Guide

## Overview
This guide shows you how to implement **real-time transcription** for your Nigerian language project using **WebSockets**, **streaming audio**, and **live AI processing**.

## Architecture Overview

```
┌─────────────────┐    WebSocket     ┌─────────────────┐    AI Models    ┌─────────────────┐
│   Frontend      │ ◄────────────► │   Backend API   │ ◄─────────────► │   ML Pipeline   │
│ (Web/Mobile)    │   Audio Stream   │  (FastAPI +     │   Whisper/      │ (Whisper, Wav2Vec,│
│                 │                  │   WebSocket)    │   Wav2Vec       │  DeepSpeech)    │
└─────────────────┘                  └─────────────────┘                  └─────────────────┘
        │                                     │                                     │
        │                                     │                                     │
        ▼                                     ▼                                     ▼
┌─────────────────┐                  ┌─────────────────┐                  ┌─────────────────┐
│   Live Audio    │                  │   Real-time     │                  │   MongoDB       │
│   Recording     │                  │   Processing    │                  │   Storage       │
│   (Microphone)  │                  │   Queue         │                  │                 │
└─────────────────┘                  └─────────────────┘                  └─────────────────┘
```

## Prerequisites

### System Requirements
- **Python 3.8+**
- **Node.js 16+** (for React frontend)
- **Flutter 3.0+** (for mobile)
- **MongoDB** (for storing transcriptions)
- **FFmpeg** (for audio processing)

### Hardware Requirements
- **CPU**: 4+ cores (8+ recommended for real-time processing)
- **RAM**: 8GB minimum (16GB+ recommended)
- **GPU**: Optional but recommended (NVIDIA with CUDA for faster Whisper processing)

## Step-by-Step Implementation

### Step 1: Set Up Your Backend API

1. **Install the backend dependencies:**
```bash
cd backend
pip install fastapi uvicorn websockets whisper torch torchaudio pydub pymongo python-multipart
```

2. **Place the backend code** (from the first artifact) in `backend/app/realtime_transcription.py`

3. **Start the backend server:**
```bash
cd backend
python -m uvicorn app.realtime_transcription:app --host 0.0.0.0 --port 8000 --reload
```

4. **Test the WebSocket connection:**
   - Open `http://localhost:8000` in your browser
   - You should see a demo page with real-time transcription

### Step 2: Set Up React Frontend

1. **Create React app** (if not already created):
```bash
cd frontend
npx create-react-app . --template typescript
npm install
```

2. **Add the React component** (from the second artifact) to `frontend/src/components/RealtimeTranscription.js`

3. **Update your main App.js:**
```javascript
import React from 'react';
import RealtimeTranscription from './components/RealtimeTranscription';
import './App.css';

function App() {
  return (
    <div className="App">
      <RealtimeTranscription />
    </div>
  );
}

export default App;
```

4. **Start the React development server:**
```bash
cd frontend
npm start
```

### Step 3: Set Up Flutter Mobile App

1. **Initialize Flutter project** (if not already created):
```bash
cd mobile
flutter create . --org com.yourcompany.transcription
```

2. **Update `pubspec.yaml`** with the dependencies (from the pubspec artifact)

3. **Install dependencies:**
```bash
flutter pub get
```

4. **Add the Flutter screen** (from the third artifact) to `mobile/lib/screens/realtime_transcription_screen.dart`

5. **Update your main.dart:**
```dart
import 'package:flutter/material.dart';
import 'screens/realtime_transcription_screen.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Nigerian Language Transcription',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: RealtimeTranscriptionScreen(),
    );
  }
}
```

6. **Add permissions to Android** (`android/app/src/main/AndroidManifest.xml`):
```xml
<uses-permission android:name="android.permission.RECORD_AUDIO" />
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
```

7. **Add permissions to iOS** (`ios/Runner/Info.plist`):
```xml
<key>NSMicrophoneUsageDescription</key>
<string>This app needs microphone access to record audio for transcription</string>
```

8. **Run the Flutter app:**
```bash
flutter run
```

### Step 4: Configure MongoDB

1. **Install MongoDB** (if not already installed):
```bash
# On macOS
brew install mongodb-community

# On Ubuntu
sudo apt-get install mongodb

# Or use MongoDB Atlas (cloud)
```

2. **Start MongoDB:**
```bash
# Local MongoDB
mongod --dbpath /usr/local/var/mongodb

# Or use MongoDB Atlas connection string in your backend
```

3. **Verify collections are created:**
   - `realtime_transcriptions` - for live transcription storage
   - `batch_transcriptions` - for uploaded file transcriptions

## Advanced Configuration

### Optimize Whisper for Real-Time Processing

1. **Use smaller Whisper models for faster processing:**
```python
# In your backend code, change this line:
whisper_model = whisper.load_model("tiny")  # Fastest, less accurate
# whisper_model = whisper.load_model("base")  # Balanced
# whisper_model = whisper.load_model("small") # Current default
```

2. **Enable GPU acceleration** (if available):
```python
# In your backend code, add GPU detection:
import torch

# Check if CUDA is available
device = "cuda" if torch.cuda.is_available() else "cpu"
whisper_model = whisper.load_model("small", device=device)

# Enable FP16 for faster processing
result = whisper_model.transcribe(
    audio_data,
    language=None if self.language == "auto" else self.language,
    fp16=torch.cuda.is_available()  # Use FP16 on GPU
)
```

3. **Optimize audio chunk processing:**
```python
# Adjust these parameters in your backend for better performance:
CHUNK_DURATION = 1.5  # Reduce for lower latency (but more processing)
SAMPLE_RATE = 16000   # Keep at 16kHz for Whisper
BUFFER_SIZE = 3       # Number of chunks to keep in buffer
```

### Multi-Language Model Support

1. **Add Wav2Vec2 for better Nigerian language support:**
```bash
pip install transformers accelerate
```

2. **Create a model manager class:**
```python
class MultiModelTranscriber:
    def __init__(self):
        self.whisper_model = whisper.load_model("small")
        self.wav2vec_processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-large-960h")
        self.wav2vec_model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-large-960h")
    
    def transcribe(self, audio_data, language="auto", model_preference="whisper"):
        if model_preference == "whisper":
            return self._transcribe_whisper(audio_data, language)
        elif model_preference == "wav2vec":
            return self._transcribe_wav2vec(audio_data)
```

### Production Deployment

#### Option 1: Docker Deployment

1. **Create Dockerfile for backend:**
```dockerfile
# backend/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.realtime_transcription:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. **Create docker-compose.yml:**
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URI=mongodb://mongo:27017/
    depends_on:
      - mongo
    volumes:
      - ./data:/app/data

  mongo:
    image: mongo:5.0
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  mongo_data:
```

3. **Deploy with Docker:**
```bash
docker-compose up -d
```

#### Option 2: Cloud Deployment (AWS/GCP/Azure)

1. **Backend on AWS EC2:**
```bash
# Launch EC2 instance (t3.large or larger recommended)
# Install dependencies
sudo apt update
sudo apt install -y python3-pip ffmpeg mongodb

# Deploy your backend
git clone your-repo
cd your-repo/backend
pip3 install -r requirements.txt
python3 -m uvicorn app.realtime_transcription:app --host 0.0.0.0 --port 8000
```

2. **Frontend on Vercel/Netlify:**
```bash
# Build and deploy React app
cd frontend
npm run build

# Deploy to Vercel
npx vercel --prod

# Or deploy to Netlify
npx netlify deploy --prod --dir=build
```

3. **Mobile app deployment:**
```bash
# Build Android APK
cd mobile
flutter build apk --release

# Build iOS (requires macOS and Xcode)
flutter build ios --release
```

## Performance Optimization

### 1. Audio Processing Optimization

```python
# Optimize audio buffer management
class OptimizedAudioBuffer:
    def __init__(self, max_chunks=5):
        self.chunks = deque(maxlen=max_chunks)
        self.lock = threading.Lock()
        self.total_duration = 0
    
    def add_chunk(self, audio_data, duration):
        with self.lock:
            self.chunks.append(audio_data)
            self.total_duration += duration
            
            # Only process if we have enough audio (3+ seconds)
            if self.total_duration >= 3.0:
                return self.get_combined_audio()
        return None
```

### 2. WebSocket Connection Optimization

```python
# Add connection pooling and reconnection logic
class RobustWebSocketManager:
    def __init__(self, max_retries=3):
        self.max_retries = max_retries
        self.retry_count = 0
        
    async def connect_with_retry(self, websocket):
        while self.retry_count < self.max_retries:
            try:
                await self.establish_connection(websocket)
                self.retry_count = 0  # Reset on successful connection
                break
            except Exception as e:
                self.retry_count += 1
                await asyncio.sleep(2 ** self.retry_count)  # Exponential backoff
```

### 3. Model Caching and Warm-up

```python
# Pre-warm models for faster first transcription
class ModelWarmer:
    def __init__(self):
        self.models_warmed = False
    
    def warm_up_models(self):
        if not self.models_warmed:
            # Create dummy audio for warm-up
            dummy_audio = np.random.randn(16000 * 2).astype(np.float32)
            
            # Warm up Whisper
            whisper_model.transcribe(dummy_audio)
            
            self.models_warmed = True
            logger.info("Models warmed up successfully")
```

## Monitoring and Debugging

### 1. Add Comprehensive Logging

```python
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('transcription.log'),
        logging.StreamHandler()
    ]
)

# Add performance monitoring
class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            'total_sessions': 0,
            'active_connections': 0,
            'avg_transcription_time': 0,
            'total_audio_processed': 0
        }
    
    def log_transcription_time(self, duration):
        self.metrics['avg_transcription_time'] = (
            self.metrics['avg_transcription_time'] + duration
        ) / 2
```

### 2. Health Check Endpoints

```python
@app.get("/api/metrics")
async def get_metrics():
    return {
        "active_connections": len(active_connections),
        "model_status": "loaded" if whisper_model else "not_loaded",
        "mongodb_status": "connected" if client.admin.command('ping') else "disconnected",
        "system_memory": psutil.virtual_memory().percent,
        "cpu_usage": psutil.cpu_percent()
    }
```

## Scaling for Production

### 1. Horizontal Scaling

```python
# Use Redis for session management across multiple servers
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

class DistributedSessionManager:
    def store_session(self, session_id, data):
        redis_client.setex(f"session:{session_id}", 3600, json.dumps(data))
    
    def get_session(self, session_id):
        data = redis_client.get(f"session:{session_id}")
        return json.loads(data) if data else None
```

### 2. Load Balancing

```nginx
# nginx.conf for load balancing
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    listen 80;
    
    location /ws/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
    
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
    }
}
```

## Mobile-Specific Optimizations

### 1. Audio Format Optimization

```dart
// Optimize recording settings for mobile
await _audioRecord.start(
  path: _audioPath,
  encoder: AudioEncoder.wav,
  bitRate: 64000,        // Lower bitrate for mobile
  samplingRate: 16000,   // Standard for speech recognition
  numChannels: 1,        // Mono audio
  autoGain: true,        // Enable auto gain control
  echoCancel: true,      // Enable echo cancellation
  noiseSuppress: true,   // Enable noise suppression
);
```

### 2. Battery Optimization

```dart
class BatteryOptimizedRecorder {
  Timer? _batteryCheckTimer;
  
  void startBatteryAwareRecording() {
    _batteryCheckTimer = Timer.periodic(Duration(seconds: 30), (timer) {
      _checkBatteryLevel();
    });
  }
  
  void _checkBatteryLevel() async {
    // Reduce processing frequency on low battery
    if (await Battery().batteryLevel < 20) {
      _reduceProcessingFrequency();
    }
  }
}
```

## Security Considerations

### 1. WebSocket Authentication

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.websocket("/ws/transcribe")
async def websocket_transcription(
    websocket: WebSocket,
    token: str = Depends(security)
):
    # Verify token before accepting WebSocket connection
    if not verify_token(token):
        await websocket.close(code=1008)  # Policy violation
        return
    
    await websocket.accept()
    # ... rest of WebSocket logic
```

### 2. Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/upload-transcribe")
@limiter.limit("10/minute")  # Limit uploads to 10 per minute
async def upload_and_transcribe(request: Request, file: UploadFile):
    # ... transcription logic
```

## Testing the Real-Time System

### 1. Load Testing

```python
# test_websocket_load.py
import asyncio
import websockets
import json

async def test_client(client_id):
    uri = "ws://localhost:8000/ws/transcribe"
    async with websockets.connect(uri) as websocket:
        # Simulate audio streaming
        for i in range(100):
            await websocket.send(b"dummy_audio_data")
            await asyncio.sleep(0.1)

# Run 10 concurrent clients
async def load_test():
    tasks = [test_client(i) for i in range(10)]
    await asyncio.gather(*tasks)

asyncio.run(load_test())
```

### 2. Audio Quality Testing

```python
# Test different audio qualities and formats
test_files = [
    "test_16khz_mono.wav",
    "test_44khz_stereo.mp3",
    "test_noisy_audio.wav",
    "test_multiple_speakers.wav"
]

for test_file in test_files:
    result = test_transcription_accuracy(test_file)
    print(f"{test_file}: {result['accuracy']}% accuracy")
```

## Next Steps

1. **Deploy your system** using the Docker setup
2. **Test with real Nigerian language audio** (Yoruba, Igbo, Hausa)
3. **Monitor performance** using the metrics endpoints
4. **Scale horizontally** as your user base grows
5. **Fine-tune models** with your specific datasets
6. **Add more features** like speaker diarization, translation, etc.

## Troubleshooting

### Common Issues and Solutions

1. **High latency**: Reduce chunk duration, use smaller Whisper model
2. **WebSocket disconnections**: Implement reconnection logic with exponential backoff
3. **Audio quality issues**: Check microphone permissions, use noise suppression
4. **Memory leaks**: Monitor audio buffer size, implement proper cleanup
5. **Model loading errors**: Ensure sufficient RAM, check CUDA compatibility

Your real-time transcription system is now ready for production!