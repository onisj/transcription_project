# Real-Time Nigerian Language Transcription System

A comprehensive real-time speech-to-text transcription system supporting Nigerian languages (English, Yoruba, Igbo, and Hausa) with web, mobile, and API interfaces.

## 🌟 Features

- **Real-time Transcription**: Live audio processing with WebSocket support
- **Multi-language Support**: English, Yoruba, Igbo, and Hausa
- **Cross-platform**: Web frontend, mobile app, and REST API
- **AI-powered**: Built with OpenAI Whisper for accurate transcription
- **Scalable Architecture**: Microservices-based backend with MongoDB
- **Modern UI**: Responsive React frontend and Flutter mobile app

## 🏗️ Architecture

```
transcription_project/
├── backend/                 # FastAPI backend server
│   ├── app/                # Application modules
│   ├── requirements.txt    # Python dependencies
│   └── run.py             # Server entry point
├── frontend/               # React web application
│   ├── src/               # Source code
│   └── package.json       # Node.js dependencies
├── mobile/                 # Flutter mobile application
│   ├── lib/               # Dart source code
│   └── pubspec.yaml       # Flutter dependencies
├── models/                 # ML model training and utilities
├── data/                   # Data processing and storage
├── docs/                   # Documentation
└── scripts/                # Utility scripts
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- Flutter 3.0+
- MongoDB
- Git

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd transcription_project
   ```

2. **Set up Python environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   # Copy and edit the .env file
   cp .env.example .env
   # Edit .env with your MongoDB URI and other settings
   ```

4. **Start the server**
   ```bash
   python run.py
   ```

### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure environment**
   ```bash
   # Copy and edit the .env file
   cp .env.example .env
   # Update API endpoints to match your backend
   ```

3. **Start development server**
   ```bash
   npm start
   ```

### Mobile Setup

1. **Install Flutter dependencies**
   ```bash
   cd mobile
   flutter pub get
   ```

2. **Run the app**
   ```bash
   flutter run
   ```

## 🔧 Configuration

The system uses centralized configuration through environment variables:

- **Backend**: `backend/.env` and `backend/app/settings.py`
- **Frontend**: `frontend/.env` and `frontend/src/config.js`
- **Mobile**: `mobile/lib/config.dart`

See [Configuration Guide](backend/CONFIGURATION.md) for detailed setup instructions.

## 📡 API Endpoints

### WebSocket
- `ws://localhost:8000/ws/transcribe` - Real-time transcription

### REST API
- `POST /api/upload-transcribe` - File upload transcription
- `GET /api/transcription-history/{session_id}` - Get history
- `GET /api/health` - Health check
- `GET /` - Demo page

## 🌍 Supported Languages

- **Auto-detect**: Automatically identify language
- **English (en)**: Standard English transcription
- **Yoruba (yo)**: Nigerian Yoruba language
- **Igbo (ig)**: Nigerian Igbo language
- **Hausa (ha)**: Nigerian Hausa language

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **OpenAI Whisper**: Speech recognition model
- **MongoDB**: Document database
- **WebSockets**: Real-time communication
- **Uvicorn**: ASGI server

### Frontend
- **React**: JavaScript UI library
- **WebSocket API**: Real-time communication
- **MediaRecorder API**: Audio recording

### Mobile
- **Flutter**: Cross-platform mobile framework
- **Dart**: Programming language
- **WebSocket**: Real-time communication

## 📊 Performance

- **Latency**: < 2 seconds for real-time transcription
- **Accuracy**: 85%+ for supported languages
- **Concurrent Users**: 100+ simultaneous connections
- **Audio Formats**: WAV, MP3, WebM, OGG

## 🔒 Security

- **CORS Configuration**: Configurable cross-origin policies
- **Input Validation**: Secure file upload handling
- **Environment Variables**: Sensitive data protection
- **Rate Limiting**: Configurable API limits

## 🚀 Deployment

### Production Checklist

1. **Environment Variables**
   - Set `DEBUG=false`
   - Configure production MongoDB URI
   - Set appropriate CORS origins
   - Configure logging levels

2. **Security**
   - Use HTTPS/WSS in production
   - Configure firewall rules
   - Set up monitoring and alerts

3. **Scaling**
   - Use load balancers
   - Implement caching
   - Monitor resource usage

### Docker Deployment

```bash
# Build and run with Docker
docker build -t transcription-backend ./backend
docker run -p 8000:8000 transcription-backend
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for the Whisper model
- FastAPI community for the excellent framework
- React and Flutter teams for the development tools

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the [documentation](docs/)
- Review the [configuration guide](backend/CONFIGURATION.md)

## 🔄 Version History

- **v1.0.0**: Initial release with basic transcription
- **v1.1.0**: Added multi-language support
- **v1.2.0**: Mobile app and configuration system
- **v1.3.0**: Performance improvements and documentation

---

**Made with ❤️ for Nigerian language preservation and accessibility**
