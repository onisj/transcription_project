/// Flutter Configuration
/// 
/// This file contains configuration values that should match
/// the backend settings in backend/.env

class AppConfig {
  // Backend API Configuration
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000',
  );
  
  static const String wsBaseUrl = String.fromEnvironment(
    'WS_BASE_URL',
    defaultValue: 'ws://localhost:8000',
  );
  
  // API Endpoints
  static const Map<String, String> endpoints = {
    'websocketTranscribe': '/ws/transcribe',
    'uploadTranscribe': '/api/upload-transcribe',
    'transcriptionHistory': '/api/transcription-history',
    'healthCheck': '/api/health',
  };
  
  // Supported Languages (should match backend settings)
  static const List<Map<String, String>> supportedLanguages = [
    {'value': 'auto', 'label': 'Auto-detect'},
    {'value': 'en', 'label': 'English'},
    {'value': 'yo', 'label': 'Yoruba'},
    {'value': 'ig', 'label': 'Igbo'},
    {'value': 'ha', 'label': 'Hausa'},
  ];
  
  // Audio Configuration
  static const Map<String, dynamic> audio = {
    'sampleRate': 16000,
    'chunkDuration': 2.0,
    'mimeType': 'audio/webm;codecs=opus',
  };
  
  // UI Configuration
  static const Map<String, dynamic> ui = {
    'refreshInterval': 1000, // 1 second
    'maxTranscriptions': 100,
  };
  
  // Get full WebSocket URL
  static String getWebSocketUrl(String language) {
    return '$wsBaseUrl${endpoints['websocketTranscribe']}?language=$language';
  }
  
  // Get full API URL
  static String getApiUrl(String endpoint) {
    return '$apiBaseUrl$endpoint';
  }
}
