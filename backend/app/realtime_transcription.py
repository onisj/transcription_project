"""
Real-Time Transcription Backend

"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import asyncio
import json
import base64
import numpy as np
import io
import wave
import threading
import queue
from collections import deque
import time
import whisper
import torch
import torchaudio
from pydub import AudioSegment
from pymongo import MongoClient
import os
from typing import Dict, List
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="Real-Time Nigerian Language Transcription API")

# Enable CORS for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  
    allow_credentials=ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import settings
from .settings import (
    MONGO_URI, DB_NAME, WHISPER_MODEL_SIZE, SAMPLE_RATE, 
    CHUNK_DURATION, CHUNK_SIZE, MAX_AUDIO_BUFFER_SIZE, 
    MIN_CHUNKS_FOR_TRANSCRIPTION, ALLOWED_ORIGINS, 
    ALLOW_CREDENTIALS, SUPPORTED_LANGUAGES
)

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Load Whisper model (you can switch to wav2vec or other models)
logger.info("Loading Whisper model...")
whisper_model = whisper.load_model(WHISPER_MODEL_SIZE)  # Change to "medium" or "large" for better accuracy
logger.info("Whisper model loaded successfully")

# Audio processing configuration
# SAMPLE_RATE, CHUNK_DURATION, and CHUNK_SIZE are now imported from settings

class AudioBuffer:
    """Manages audio chunks for real-time processing"""
    def __init__(self, max_size=MAX_AUDIO_BUFFER_SIZE):
        self.buffer = deque(maxlen=max_size)
        self.lock = threading.Lock()
    
    def add_chunk(self, audio_data):
        with self.lock:
            self.buffer.append(audio_data)
    
    def get_audio_for_transcription(self):
        with self.lock:
            if len(self.buffer) >= MIN_CHUNKS_FOR_TRANSCRIPTION:  
                # Combine last few chunks for context
                combined = np.concatenate(list(self.buffer)[-3:])
                return combined
            return None

class TranscriptionSession:
    """Manages a single transcription session"""
    def __init__(self, websocket: WebSocket, language: str = "auto"):
        self.websocket = websocket
        self.language = language
        self.audio_buffer = AudioBuffer()
        self.transcription_queue = queue.Queue()
        self.is_active = True
        self.session_id = str(int(time.time()))
        
    async def process_audio_chunk(self, audio_data: bytes):
        """Process incoming audio chunk"""
        try:
            # Convert audio bytes to numpy array
            audio_array = self._bytes_to_audio_array(audio_data)
            
            if audio_array is not None:
                self.audio_buffer.add_chunk(audio_array)
                
                # Get audio for transcription (non-blocking)
                audio_for_transcription = self.audio_buffer.get_audio_for_transcription()
                
                if audio_for_transcription is not None:
                    # Run transcription in background thread to avoid blocking
                    threading.Thread(
                        target=self._transcribe_audio_async,
                        args=(audio_for_transcription,),
                        daemon=True
                    ).start()
                    
        except Exception as e:
            logger.error(f"Error processing audio chunk: {e}")
            await self.websocket.send_text(json.dumps({
                "type": "error",
                "message": f"Audio processing error: {str(e)}"
            }))
    
    def _bytes_to_audio_array(self, audio_data: bytes) -> np.ndarray:
        """Convert audio bytes to numpy array"""
        try:
            # Try to parse as WAV first
            audio_io = io.BytesIO(audio_data)
            
            # Check if it's base64 encoded
            if isinstance(audio_data, str):
                audio_data = base64.b64decode(audio_data)
                audio_io = io.BytesIO(audio_data)
            
            # Use pydub to handle various audio formats
            audio_segment = AudioSegment.from_file(audio_io)
            
            # Convert to mono 16kHz
            audio_segment = audio_segment.set_channels(1).set_frame_rate(SAMPLE_RATE)
            
            # Convert to numpy array
            audio_array = np.array(audio_segment.get_array_of_samples(), dtype=np.float32)
            audio_array = audio_array / 32768.0  # Normalize to [-1, 1]
            
            return audio_array
            
        except Exception as e:
            logger.error(f"Error converting audio bytes: {e}")
            return None
    
    def _transcribe_audio_async(self, audio_data: np.ndarray):
        """Transcribe audio in background thread"""
        try:
            # Use Whisper for transcription
            result = whisper_model.transcribe(
                audio_data,
                language=None if self.language == "auto" else self.language,
                fp16=torch.cuda.is_available()
            )
            
            transcription = result["text"].strip()
            confidence = result.get("segments", [{}])
            avg_confidence = np.mean([seg.get("confidence", 0.5) for seg in confidence]) if confidence else 0.5
            
            if transcription:  # Only send non-empty transcriptions
                # Send transcription via WebSocket
                asyncio.create_task(self._send_transcription(transcription, avg_confidence))
                
                # Store in MongoDB
                self._store_transcription(transcription, avg_confidence)
                
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            asyncio.create_task(self._send_error(f"Transcription error: {str(e)}"))
    
    async def _send_transcription(self, text: str, confidence: float):
        """Send transcription result to client"""
        try:
            message = {
                "type": "transcription",
                "text": text,
                "confidence": confidence,
                "timestamp": time.time(),
                "language": self.language,
                "session_id": self.session_id
            }
            await self.websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending transcription: {e}")
    
    async def _send_error(self, error_message: str):
        """Send error message to client"""
        try:
            message = {
                "type": "error",
                "message": error_message,
                "timestamp": time.time()
            }
            await self.websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending error message: {e}")
    
    def _store_transcription(self, text: str, confidence: float):
        """Store transcription in MongoDB"""
        try:
            db.realtime_transcriptions.insert_one({
                "session_id": self.session_id,
                "text": text,
                "confidence": confidence,
                "language": self.language,
                "timestamp": time.time(),
                "created_at": time.time()
            })
        except Exception as e:
            logger.error(f"Error storing transcription: {e}")

# Store active WebSocket connections
active_connections: Dict[str, TranscriptionSession] = {}

@app.websocket("/ws/transcribe")
async def websocket_transcription(websocket: WebSocket):
    """WebSocket endpoint for real-time transcription"""
    await websocket.accept()
    
    # Get language preference from query params
    language = websocket.query_params.get("language", "auto")
    session = TranscriptionSession(websocket, language)
    
    # Store connection
    connection_id = f"{id(websocket)}_{int(time.time())}"
    active_connections[connection_id] = session
    
    logger.info(f"New WebSocket connection: {connection_id}, language: {language}")
    
    try:
        # Send connection confirmation
        await websocket.send_text(json.dumps({
            "type": "connected",
            "session_id": session.session_id,
            "message": "Real-time transcription started",
            "supported_languages": SUPPORTED_LANGUAGES  
        }))
        
        while True:
            # Wait for audio data
            data = await websocket.receive()
            
            if data.get("type") == "websocket.receive":
                if "bytes" in data:
                    # Binary audio data
                    audio_data = data["bytes"]
                    await session.process_audio_chunk(audio_data)
                    
                elif "text" in data:
                    # JSON message (could be control commands)
                    try:
                        message = json.loads(data["text"])
                        
                        if message.get("type") == "audio_chunk":
                            # Base64 encoded audio
                            audio_data = base64.b64decode(message["data"])
                            await session.process_audio_chunk(audio_data)
                            
                        elif message.get("type") == "change_language":
                            # Change transcription language
                            session.language = message.get("language", "auto")
                            await websocket.send_text(json.dumps({
                                "type": "language_changed",
                                "language": session.language
                            }))
                            
                        elif message.get("type") == "ping":
                            # Heartbeat
                            await websocket.send_text(json.dumps({
                                "type": "pong",
                                "timestamp": time.time()
                            }))
                            
                    except json.JSONDecodeError:
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "message": "Invalid JSON message"
                        }))
                        
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {connection_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        # Clean up
        if connection_id in active_connections:
            del active_connections[connection_id]
        session.is_active = False

@app.post("/api/upload-transcribe")
async def upload_and_transcribe(file: UploadFile = File(...), language: str = "auto"):
    """Upload audio file for batch transcription"""
    try:
        # Read audio file
        audio_data = await file.read()
        
        # Process with whisper
        audio_io = io.BytesIO(audio_data)
        audio_segment = AudioSegment.from_file(audio_io)
        audio_segment = audio_segment.set_channels(1).set_frame_rate(SAMPLE_RATE)
        audio_array = np.array(audio_segment.get_array_of_samples(), dtype=np.float32)
        audio_array = audio_array / 32768.0
        
        # Transcribe
        result = whisper_model.transcribe(
            audio_array,
            language=None if language == "auto" else language
        )
        
        transcription = result["text"]
        detected_language = result.get("language", "unknown")
        
        # Store in MongoDB
        db.batch_transcriptions.insert_one({
            "filename": file.filename,
            "transcription": transcription,
            "language": detected_language,
            "requested_language": language,
            "timestamp": time.time(),
            "file_size": len(audio_data)
        })
        
        return {
            "transcription": transcription,
            "detected_language": detected_language,
            "confidence": "high",  # Whisper doesn't return word-level confidence easily
            "filename": file.filename
        }
        
    except Exception as e:
        logger.error(f"Upload transcription error: {e}")
        return {"error": str(e)}, 500

@app.get("/api/transcription-history/{session_id}")
async def get_transcription_history(session_id: str):
    """Get transcription history for a session"""
    try:
        transcriptions = list(db.realtime_transcriptions.find(
            {"session_id": session_id},
            {"_id": 0}
        ).sort("timestamp", 1))
        
        return {"transcriptions": transcriptions}
    except Exception as e:
        return {"error": str(e)}, 500

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": whisper_model is not None,
        "active_connections": len(active_connections),
        "timestamp": time.time()
    }

@app.get("/")
async def get_demo_page():
    """Serve a simple demo page for testing"""
    
    # Generate language options dynamically from settings
    language_options = ""
    for lang in SUPPORTED_LANGUAGES:
        if lang == "auto":
            language_options += '<option value="auto">Auto-detect</option>'
        elif lang == "en":
            language_options += '<option value="en">English</option>'
        elif lang == "yo":
            language_options += '<option value="yo">Yoruba</option>'
        elif lang == "ig":
            language_options += '<option value="ig">Igbo</option>'
        elif lang == "ha":
            language_options += '<option value="ha">Hausa</option>'
        else:
            language_options += f'<option value="{lang}">{lang.upper()}</option>'
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Real-Time Nigerian Language Transcription</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
            .status {{ padding: 10px; margin: 10px 0; border-radius: 5px; }}
            .connected {{ background-color: #d4edda; color: #155724; }}
            .disconnected {{ background-color: #f8d7da; color: #721c24; }}
            .transcription {{ background-color: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }}
            button {{ padding: 10px 20px; margin: 5px; font-size: 16px; }}
            select {{ padding: 8px; margin: 5px; }}
        </style>
    </head>
    <body>
        <h1>Real-Time Nigerian Language Transcription</h1>
        <div id="status" class="status disconnected">Disconnected</div>
        
        <div>
            <label>Language: </label>
            <select id="language">
                {language_options}
            </select>
            <button id="startBtn" onclick="startRecording()">Start Recording</button>
            <button id="stopBtn" onclick="stopRecording()" disabled>Stop Recording</button>
        </div>
        
        <div id="transcriptions"></div>
        
        <script>
            let mediaRecorder;
            let websocket;
            let audioChunks = [];
            
            function startRecording() {{
                const language = document.getElementById('language').value;
                
                // Connect WebSocket
                const wsUrl = `ws://localhost:{PORT}/ws/transcribe?language=${{language}}`;
                websocket = new WebSocket(wsUrl);
                
                websocket.onopen = function() {{
                    document.getElementById('status').textContent = 'Connected';
                    document.getElementById('status').className = 'status connected';
                    document.getElementById('startBtn').disabled = true;
                    document.getElementById('stopBtn').disabled = false;
                }};
                
                websocket.onmessage = function(event) {{
                    const data = JSON.parse(event.data);
                    if (data.type === 'transcription') {{
                        addTranscription(data.text, data.confidence, data.language);
                    }}
                }};
                
                websocket.onclose = function() {{
                    document.getElementById('status').textContent = 'Disconnected';
                    document.getElementById('status').className = 'status disconnected';
                    document.getElementById('startBtn').disabled = false;
                    document.getElementById('stopBtn').disabled = true;
                }};
                
                // Start audio recording
                navigator.mediaDevices.getUserMedia({{ audio: true }})
                    .then(stream => {{
                        mediaRecorder = new MediaRecorder(stream, {{
                            mimeType: 'audio/webm;codecs=opus'
                        }});
                        
                        mediaRecorder.addEventListener('dataavailable', function(event) {{
                            if (event.data.size > 0 && websocket.readyState === WebSocket.OPEN) {{
                                // Send audio chunk to WebSocket
                                websocket.send(event.data);
                            }}
                        }});
                        
                        // Send audio chunks every 1 second
                        mediaRecorder.start(1000);
                    }})
                    .catch(err => {{
                        console.error('Error accessing microphone:', err);
                        alert('Could not access microphone');
                    }});
            }}
            
            function stopRecording() {{
                if (mediaRecorder && mediaRecorder.state !== 'inactive') {{
                    mediaRecorder.stop();
                    mediaRecorder.stream.getTracks().forEach(track => track.stop());
                }}
                
                if (websocket) {{
                    websocket.close();
                }}
            }}
            
            function addTranscription(text, confidence, language) {{
                const div = document.createElement('div');
                div.className = 'transcription';
                div.innerHTML = `
                    <strong>${{language.toUpperCase()}}:</strong> ${{text}}
                    <small style="float: right;">Confidence: ${{(confidence * 100).toFixed(1)}}%</small>
                `;
                document.getElementById('transcriptions').appendChild(div);
                div.scrollIntoView({{ behavior: 'smooth' }});
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT, log_level=LOG_LEVEL.lower())