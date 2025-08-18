"""
Main entry point for the transcription backend server

This script uses the centralized settings configuration to start the server.
"""

import uvicorn
from app.settings import HOST, PORT, DEBUG, LOG_LEVEL

if __name__ == "__main__":
    uvicorn.run(
        "app.realtime_transcription:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
        log_level=LOG_LEVEL.lower()
    )
