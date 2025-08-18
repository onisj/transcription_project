// Real-Time Transcription React Component

import React, { useCallback, useEffect, useRef, useState } from 'react';
import config from '../config';

const RealtimeTranscription = () => {
    const [isConnected, setIsConnected] = useState(false);
    const [isRecording, setIsRecording] = useState(false);
    const [transcriptions, setTranscriptions] = useState([]);
    const [selectedLanguage, setSelectedLanguage] = useState('auto');
    const [sessionId, setSessionId] = useState(null);
    const [error, setError] = useState(null);
    const [connectionStatus, setConnectionStatus] = useState('disconnected');

    const websocketRef = useRef(null);
    const mediaRecorderRef = useRef(null);
    const audioStreamRef = useRef(null);
    const transcriptionsEndRef = useRef(null);

    const languages = config.SUPPORTED_LANGUAGES;

    // Scroll to bottom when new transcriptions arrive
    useEffect(() => {
        transcriptionsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [transcriptions]);

    const connectWebSocket = useCallback(() => {
        const wsUrl = `${config.WS_BASE_URL}${config.ENDPOINTS.WEBSOCKET_TRANSCRIBE}?language=${selectedLanguage}`;

        try {
            websocketRef.current = new WebSocket(wsUrl);
            setConnectionStatus('connecting');

            websocketRef.current.onopen = () => {
                setIsConnected(true);
                setConnectionStatus('connected');
                setError(null);
                console.log('WebSocket connected');
            };

            websocketRef.current.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);

                    switch (data.type) {
                        case 'connected':
                            setSessionId(data.session_id);
                            console.log('Session started:', data.session_id);
                            break;

                        case 'transcription':
                            setTranscriptions(prev => [...prev, {
                                id: Date.now(),
                                text: data.text,
                                confidence: data.confidence,
                                language: data.language,
                                timestamp: new Date(data.timestamp * 1000).toLocaleTimeString()
                            }]);
                            break;

                        case 'language_changed':
                            console.log('Language changed to:', data.language);
                            break;

                        case 'error':
                            setError(data.message);
                            console.error('WebSocket error:', data.message);
                            break;

                        default:
                            console.log('Unknown message type:', data.type);
                    }
                } catch (err) {
                    console.error('Error parsing WebSocket message:', err);
                }
            };

            websocketRef.current.onclose = () => {
                setIsConnected(false);
                setConnectionStatus('disconnected');
                console.log('WebSocket disconnected');
            };

            websocketRef.current.onerror = (err) => {
                setError('WebSocket connection failed');
                setConnectionStatus('error');
                console.error('WebSocket error:', err);
            };

        } catch (err) {
            setError('Failed to create WebSocket connection');
            setConnectionStatus('error');
            console.error('WebSocket creation error:', err);
        }
    }, [selectedLanguage]);

    const disconnectWebSocket = useCallback(() => {
        if (websocketRef.current) {
            websocketRef.current.close();
            websocketRef.current = null;
        }
    }, []);

    const startRecording = useCallback(async () => {
        try {
            // First connect WebSocket
            connectWebSocket();

            // Wait a bit for WebSocket to connect
            await new Promise(resolve => setTimeout(resolve, 1000));

            // Get user media
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    sampleRate: config.AUDIO.SAMPLE_RATE,
                    channelCount: 1,
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            });

            audioStreamRef.current = stream;

            // Create MediaRecorder
            const mimeType = MediaRecorder.isTypeSupported(config.AUDIO.MIME_TYPE)
                ? config.AUDIO.MIME_TYPE
                : 'audio/webm';

            mediaRecorderRef.current = new MediaRecorder(stream, {
                mimeType: mimeType
            });

            mediaRecorderRef.current.ondataavailable = (event) => {
                if (event.data.size > 0 && websocketRef.current?.readyState === WebSocket.OPEN) {
                    // Send audio chunk to WebSocket
                    websocketRef.current.send(event.data);
                }
            };

            mediaRecorderRef.current.onerror = (event) => {
                console.error('MediaRecorder error:', event.error);
                setError('Recording error: ' + event.error.message);
            };

            // Start recording with chunks every configured interval
            mediaRecorderRef.current.start(config.UI.REFRESH_INTERVAL);
            setIsRecording(true);
            setError(null);

        } catch (err) {
            setError('Failed to start recording: ' + err.message);
            console.error('Recording start error:', err);
        }
    }, [connectWebSocket]);

    const stopRecording = useCallback(() => {
        // Stop media recorder
        if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
            mediaRecorderRef.current.stop();
        }

        // Stop audio stream
        if (audioStreamRef.current) {
            audioStreamRef.current.getTracks().forEach(track => track.stop());
            audioStreamRef.current = null;
        }

        // Disconnect WebSocket
        disconnectWebSocket();

        setIsRecording(false);
    }, [disconnectWebSocket]);

    const changeLanguage = useCallback((newLanguage) => {
        setSelectedLanguage(newLanguage);

        if (websocketRef.current?.readyState === WebSocket.OPEN) {
            websocketRef.current.send(JSON.stringify({
                type: 'change_language',
                language: newLanguage
            }));
        }
    }, []);

    const clearTranscriptions = useCallback(() => {
        setTranscriptions([]);
    }, []);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            stopRecording();
        };
    }, [stopRecording]);

    const getStatusColor = () => {
        switch (connectionStatus) {
            case 'connected': return '#28a745';
            case 'connecting': return '#ffc107';
            case 'error': return '#dc3545';
            default: return '#6c757d';
        }
    };

    const getStatusText = () => {
        switch (connectionStatus) {
            case 'connected': return 'Connected';
            case 'connecting': return 'Connecting...';
            case 'error': return 'Connection Error';
            default: return 'Disconnected';
        }
    };

    return (
        <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px', fontFamily: 'Arial, sans-serif' }}>
            <h1 style={{ textAlign: 'center', color: '#333' }}>
                Real-Time Nigerian Language Transcription
            </h1>

            {/* Status Display */}
            <div style={{
                padding: '15px',
                backgroundColor: getStatusColor(),
                color: 'white',
                borderRadius: '8px',
                marginBottom: '20px',
                textAlign: 'center',
                fontWeight: 'bold'
            }}>
                Status: {getStatusText()}
                {sessionId && ` | Session: ${sessionId}`}
            </div>

            {/* Error Display */}
            {error && (
                <div style={{
                    padding: '15px',
                    backgroundColor: '#f8d7da',
                    color: '#721c24',
                    borderRadius: '8px',
                    marginBottom: '20px',
                    border: '1px solid #f5c6cb'
                }}>
                    Error: {error}
                </div>
            )}

            {/* Controls */}
            <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '15px',
                marginBottom: '20px',
                flexWrap: 'wrap'
            }}>
                <label>
                    Language:
                    <select
                        value={selectedLanguage}
                        onChange={(e) => changeLanguage(e.target.value)}
                        disabled={isRecording}
                        style={{
                            marginLeft: '8px',
                            padding: '8px',
                            borderRadius: '4px',
                            border: '1px solid #ccc'
                        }}
                    >
                        {languages.map(lang => (
                            <option key={lang.code} value={lang.code}>
                                {lang.name}
                            </option>
                        ))}
                    </select>
                </label>

                <button
                    onClick={startRecording}
                    disabled={isRecording}
                    style={{
                        padding: '10px 20px',
                        backgroundColor: isRecording ? '#6c757d' : '#28a745',
                        color: 'white',
                        border: 'none',
                        borderRadius: '5px',
                        cursor: isRecording ? 'not-allowed' : 'pointer',
                        fontSize: '16px'
                    }}
                >
                    {isRecording ? 'Recording...' : 'Start Recording'}
                </button>

                <button
                    onClick={stopRecording}
                    disabled={!isRecording}
                    style={{
                        padding: '10px 20px',
                        backgroundColor: !isRecording ? '#6c757d' : '#dc3545',
                        color: 'white',
                        border: 'none',
                        borderRadius: '5px',
                        cursor: !isRecording ? 'not-allowed' : 'pointer',
                        fontSize: '16px'
                    }}
                >
                    Stop Recording
                </button>

                <button
                    onClick={clearTranscriptions}
                    style={{
                        padding: '10px 20px',
                        backgroundColor: '#17a2b8',
                        color: 'white',
                        border: 'none',
                        borderRadius: '5px',
                        cursor: 'pointer',
                        fontSize: '16px'
                    }}
                >
                    Clear
                </button>
            </div>

            {/* Recording Indicator */}
            {isRecording && (
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px',
                    marginBottom: '20px',
                    padding: '10px',
                    backgroundColor: '#d1ecf1',
                    borderRadius: '5px',
                    border: '1px solid #bee5eb'
                }}>
                    <div style={{
                        width: '12px',
                        height: '12px',
                        borderRadius: '50%',
                        backgroundColor: '#dc3545',
                        animation: 'pulse 1.5s infinite'
                    }}></div>
                    <span style={{ color: '#0c5460', fontWeight: 'bold' }}>
                        Recording in progress... Speak now!
                    </span>
                </div>
            )}

            {/* Transcriptions */}
            <div style={{
                border: '1px solid #ddd',
                borderRadius: '8px',
                height: '400px',
                overflowY: 'auto',
                padding: '15px',
                backgroundColor: '#f8f9fa'
            }}>
                <h3 style={{ marginTop: 0, color: '#495057' }}>Live Transcriptions</h3>

                {transcriptions.length === 0 ? (
                    <p style={{ color: '#6c757d', fontStyle: 'italic' }}>
                        No transcriptions yet. Start recording to see live transcriptions appear here.
                    </p>
                ) : (
                    transcriptions.map((transcription) => (
                        <div
                            key={transcription.id}
                            style={{
                                backgroundColor: 'white',
                                padding: '12px',
                                marginBottom: '10px',
                                borderRadius: '6px',
                                border: '1px solid #e9ecef',
                                boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
                            }}
                        >
                            <div style={{
                                display: 'flex',
                                justifyContent: 'space-between',
                                alignItems: 'center',
                                marginBottom: '8px'
                            }}>
                                <span style={{
                                    backgroundColor: '#007bff',
                                    color: 'white',
                                    padding: '2px 8px',
                                    borderRadius: '12px',
                                    fontSize: '12px',
                                    fontWeight: 'bold'
                                }}>
                                    {transcription.language.toUpperCase()}
                                </span>
                                <div style={{ display: 'flex', gap: '10px', fontSize: '12px', color: '#6c757d' }}>
                                    <span>Confidence: {(transcription.confidence * 100).toFixed(1)}%</span>
                                    <span>{transcription.timestamp}</span>
                                </div>
                            </div>
                            <p style={{
                                margin: 0,
                                fontSize: '16px',
                                lineHeight: '1.5',
                                color: '#343a40'
                            }}>
                                {transcription.text}
                            </p>
                        </div>
                    ))
                )}
                <div ref={transcriptionsEndRef} />
            </div>

            {/* Instructions */}
            <div style={{
                marginTop: '20px',
                padding: '15px',
                backgroundColor: '#e7f3ff',
                borderRadius: '8px',
                border: '1px solid #b3d9ff'
            }}>
                <h4 style={{ marginTop: 0, color: '#004085' }}>How to use:</h4>
                <ul style={{ color: '#004085', marginBottom: 0 }}>
                    <li>Select your preferred language or use "Auto-detect"</li>
                    <li>Click "Start Recording" and allow microphone access</li>
                    <li>Speak clearly in English, Yoruba, Igbo, or Hausa</li>
                    <li>Watch live transcriptions appear in real-time</li>
                    <li>Click "Stop Recording" when finished</li>
                </ul>
            </div>

            {/* CSS for pulse animation */}
            <style>{`
        @keyframes pulse {
          0% {
            transform: scale(0.95);
            box-shadow: 0 0 0 0 rgba(220, 53, 69, 0.7);
          }
          
          70% {
            transform: scale(1);
            box-shadow: 0 0 0 10px rgba(220, 53, 69, 0);
          }
          
          100% {
            transform: scale(0.95);
            box-shadow: 0 0 0 0 rgba(220, 53, 69, 0);
          }
        }
      `}</style>
        </div>
    );
};

export default RealtimeTranscription;