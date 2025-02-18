import os
import json
import whisper
import torch
import torchaudio
import librosa
import wave
from vosk import Model, KaldiRecognizer
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC

# Define directories
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
AUDIO_DIR = os.path.join(BASE_DIR, "data", "processed", "audio", "converted_audio")
TRANSCRIPT_DIR = os.path.join(BASE_DIR, "data", "processed", "text", "transcriptions")

# Ensure output directory exists
os.makedirs(TRANSCRIPT_DIR, exist_ok=True)

# Load models
print("🔹 Loading models...")
whisper_model = whisper.load_model("small")
wav2vec_processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-large-960h")
wav2vec_model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-large-960h")

vosk_model_path = os.path.join(BASE_DIR, "data", "raw", "models", "vosk-model")
vosk_model = Model(vosk_model_path)

# Function to transcribe using Whisper
def transcribe_whisper(audio_path):
    print(f"🎤 Whisper Processing: {audio_path}")
    result = whisper_model.transcribe(audio_path)
    return result["text"]

# Function to transcribe using Wav2Vec 2.0
def transcribe_wav2vec(audio_path):
    print(f"🎤 Wav2Vec 2.0 Processing: {audio_path}")
    audio, rate = librosa.load(audio_path, sr=16000)
    input_values = wav2vec_processor(audio, sampling_rate=16000, return_tensors="pt").input_values
    with torch.no_grad():
        logits = wav2vec_model(input_values).logits
    predicted_ids = torch.argmax(logits, dim=-1)
    return wav2vec_processor.batch_decode(predicted_ids)[0]

# Function to transcribe using Vosk
def transcribe_vosk(audio_path):
    print(f"🎤 Vosk Processing: {audio_path}")
    wf = wave.open(audio_path, "rb")
    recognizer = KaldiRecognizer(vosk_model, wf.getframerate())
    recognizer.SetWords(True)
    transcription = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            transcription.append(result.get("text", ""))
    final_result = json.loads(recognizer.FinalResult())
    transcription.append(final_result.get("text", ""))
    return " ".join(transcription)

# Process all .wav files in the directory
def process_all_audio():
    print(f"🔍 Scanning directory: {AUDIO_DIR}")
    for root, _, files in os.walk(AUDIO_DIR):
        for file in files:
            if file.endswith(".wav"):
                audio_path = os.path.join(root, file)
                file_name = os.path.splitext(file)[0]  # Remove extension
                
                transcript_data = {
                    "file_name": file,
                    "whisper": transcribe_whisper(audio_path),
                    "wav2vec": transcribe_wav2vec(audio_path),
                    "vosk": transcribe_vosk(audio_path),
                }

                # Save transcript as JSON
                output_path = os.path.join(TRANSCRIPT_DIR, f"{file_name}.json")
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(transcript_data, f, indent=4, ensure_ascii=False)

                print(f"✅ Saved: {output_path}")

if __name__ == "__main__":
    process_all_audio()
