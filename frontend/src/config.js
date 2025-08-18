/**
 * Frontend Configuration
 * 
 * This file contains configuration values that should match
 * the backend settings in backend/.env
 */

const config = {
  // Backend API Configuration
  API_BASE_URL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000',
  WS_BASE_URL: process.env.REACT_APP_WS_BASE_URL || 'ws://localhost:8000',
  
  // API Endpoints
  ENDPOINTS: {
    WEBSOCKET_TRANSCRIBE: '/ws/transcribe',
    UPLOAD_TRANSCRIBE: '/api/upload-transcribe',
    TRANSCRIPTION_HISTORY: '/api/transcription-history',
    HEALTH_CHECK: '/api/health',
  },
  
  // Supported Languages (should match backend settings)
  SUPPORTED_LANGUAGES: [
    { value: 'auto', label: 'Auto-detect' },
    { value: 'en', label: 'English' },
    { value: 'yo', label: 'Yoruba' },
    { value: 'ig', label: 'Igbo' },
    { value: 'ha', label: 'Hausa' },
  ],
  
  // Audio Configuration
  AUDIO: {
    SAMPLE_RATE: 16000,
    CHUNK_DURATION: 2.0,
    MIME_TYPE: 'audio/webm;codecs=opus',
  },
  
  // UI Configuration
  UI: {
    REFRESH_INTERVAL: 1000, // 1 second
    MAX_TRANSCRIPTIONS: 100,
  }
};

export default config;
