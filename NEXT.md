### **🚀 How to Continue This Project**
Your project is already well-structured. The next steps depend on what you want to accomplish next. Here are **clear milestones** to move forward efficiently.

---
<strike>
## **🔹 1. Ensure Your Data Pipeline is Working**
Your current focus is on **data preprocessing and ensuring correct file placements**.

✅ **Fix the KJV Bible Audio Processing Path:**
- Right now, KJV Bible `.wav` files are **saved in `english/kjv/` instead of `english/kjv/mp3bible/`**.
- To fix this, update `process_audio_files()` to **ensure the correct directory structure**.

**🔧 Fix in `process_audio_files()`**
```python
def process_audio_files(self):
    """Convert raw audio files to 16kHz WAV and save to the correct processed directory."""
    print("📌 Converting audio files...")

    # 🔥 Ensure we are processing only KJV MP3 Bible files
    audio_source_dirs = [
        os.path.join(RAW_AUDIO_DIR, "english", "kjv", "mp3bible"),  # ✅ Correct KJV directory
    ]

    for audio_source_dir in audio_source_dirs:
        for root, _, files in os.walk(audio_source_dir):
            for file in files:
                if file.endswith(".mp3") or file.endswith(".wav"):
                    input_path = os.path.join(root, file)

                    # 🔥 Maintain correct relative path from `mp3bible/`
                    relative_path = os.path.relpath(input_path, audio_source_dir)
                    output_path = os.path.join(CONVERTED_AUDIO_DIR, "english", "kjv", "mp3bible", relative_path).replace(".mp3", ".wav")

                    # 🔥 Ensure correct directory exists
                    self.ensure_directory_exists(output_path)

                    # 🔥 Convert and save
                    self.convert_audio(input_path, output_path)
```
✔️ **Now, converted KJV Bible `.wav` files will always be stored in `english/kjv/mp3bible/`**.
</strike>
---

## **🔹 2. Implement the Backend API**
Now that you have **data crawling and preprocessing working**, you need an **API** that allows:
1. Uploading and processing new audio files.
2. Querying transcriptions for different languages.
3. Accessing metadata from MongoDB.

### **🛠 Steps to Implement the Backend**
1. **Use FastAPI (or Flask/Django)** to serve your transcription pipeline.
2. **Create routes for processing new audio** (`/transcribe`, `/upload`).
3. **Connect to MongoDB** to log transcription results.
4. **Enable WebSocket for real-time transcription updates** (optional).

---

## **🔹 3. Train and Integrate the Speech-to-Text Model**
### **Your Current Model Choices**
You can train or fine-tune a model like:
1. **Whisper by OpenAI** (Best accuracy for low-resource languages)
2. **Wav2Vec 2.0 by Facebook AI** (Fine-tunable for specific languages)
3. **DeepSpeech by Mozilla** (Older but usable)

**📌 Example: Using Whisper for Transcription**
```python
import whisper

def transcribe_audio(audio_path):
    model = whisper.load_model("small")  # Use "base", "small", or "large"
    result = model.transcribe(audio_path)
    return result["text"]

# Example usage
print(transcribe_audio("data/processed/audio/converted_audio/english/kjv/mp3bible/01_Genesis.wav"))
```

✔️ **This will transcribe audio files into text automatically.**
🔹 **You can now store this in MongoDB or serve it via an API!**

---

<br>

### **🔹 Developing a Full Speech-to-Text Pipeline**
This guide will walk you through **developing, training, and integrating a Speech-to-Text (STT) model** into your **Nigerian language transcription project**.

---

## **🔹 1. Choose a Speech-to-Text Model**
There are three strong options:
| **Model** | **Pros** | **Cons** | **Use Case** |
|-----------|---------|---------|--------------|
| **Whisper (OpenAI)** | Best accuracy, multilingual, handles accents well | High GPU usage, no fine-tuning | Best for out-of-the-box transcription |
| **Wav2Vec 2.0 (Facebook AI)** | Fine-tunable, great for low-resource languages | Needs training on large Nigerian datasets | Best for **custom model training** |
| **DeepSpeech (Mozilla)** | Offline use, fast, open-source | Lower accuracy, harder to fine-tune | Best for **edge devices** or offline transcription |

---

## **🔹 2. Install Dependencies**
Before using any model, install the necessary libraries:

```bash
pip install torch torchaudio transformers whisper openai ffmpeg librosa numpy pydub
```

If using **DeepSpeech**, install additional dependencies:
```bash
pip install deepspeech scipy numpy
```

---

## **🔹 3. Using Whisper (Easiest and Best for Immediate Results)**
### **🔹 Load and Transcribe Audio Using Whisper**
```python
import whisper

def transcribe_audio(audio_path):
    """Transcribe audio using OpenAI's Whisper model"""
    model = whisper.load_model("small")  # Choose "tiny", "base", "small", "medium", or "large"
    result = model.transcribe(audio_path)
    return result["text"]

# Example usage
audio_file = "data/processed/audio/converted_audio/english/kjv/mp3bible/01_Genesis.wav"
transcription = transcribe_audio(audio_file)
print("Transcription:", transcription)
```

✔️ **Why Use Whisper?**
- Works **out-of-the-box** without training.
- Handles **Nigerian accents and noisy environments** well.
- Works for **English, Yoruba, Hausa, and Igbo**.

🚀 **Next Step:** Store results in **MongoDB** or serve via an API.

---

## **🔹 4. Using Wav2Vec 2.0 (Best for Custom Training)**
If Whisper **doesn't support a dialect well**, use **Wav2Vec 2.0** and fine-tune it.

### **📌 Step 1: Load a Pre-Trained Model**
```python
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import torch
import librosa

# Load model and tokenizer
processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-large-960h")
model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-large-960h")

def transcribe_wav2vec(audio_path):
    """Transcribe audio using Wav2Vec 2.0"""
    audio, _ = librosa.load(audio_path, sr=16000)
    input_values = processor(audio, return_tensors="pt", sampling_rate=16000).input_values
    with torch.no_grad():
        logits = model(input_values).logits
    predicted_ids = torch.argmax(logits, dim=-1)
    return processor.batch_decode(predicted_ids)[0]

# Example usage
transcription = transcribe_wav2vec(audio_file)
print("Transcription:", transcription)
```
✔️ **Why Use Wav2Vec 2.0?**
- Works **offline**, unlike Whisper.
- **Fine-tunable** for Nigerian languages.
- **Better performance in low-resource languages**.

🚀 **Next Step:** Train it on **Nigerian language datasets**.

---

### **🔹 5. Fine-Tuning Wav2Vec 2.0 for Nigerian Languages**
If Wav2Vec **doesn't recognize Hausa, Igbo, or Yoruba well**, train it on Nigerian datasets.

---

### **📌 Step 1: Get Nigerian Language Speech Datasets**
Some available **datasets**:
1. **Common Voice (Mozilla)** – Open-source **Yoruba, Hausa, Igbo**.
2. **African Speech Dataset** – Contains **multiple Nigerian dialects**.
3. **Custom Collected Data** – You can **record and label** your own dataset.

---

### **📌 Step 2: Preprocess the Data**
We need **transcribed audio pairs (speech → text)**.

```python
import torchaudio
from datasets import load_dataset

dataset = load_dataset("mozilla-foundation/common_voice_11_0", "yo")  # Yoruba dataset

# Convert to Wav2Vec format
def prepare_sample(batch):
    speech_array, _ = torchaudio.load(batch["path"])
    batch["input_values"] = processor(speech_array.squeeze().numpy(), return_tensors="pt").input_values
    batch["labels"] = processor.tokenizer(batch["sentence"]).input_ids
    return batch

dataset = dataset.map(prepare_sample)
```

---

### **📌 Step 3: Fine-Tune Wav2Vec 2.0**
```python
from transformers import TrainingArguments, Trainer

training_args = TrainingArguments(
    output_dir="./wav2vec2_nigerian",
    evaluation_strategy="steps",
    save_steps=400,
    save_total_limit=2,
    learning_rate=3e-4,
    per_device_train_batch_size=8,
    gradient_accumulation_steps=2,
    per_device_eval_batch_size=8,
    num_train_epochs=5,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["test"],
)

trainer.train()
```
✔️ **After training, your model will understand Nigerian languages better!**
🚀 **Next Step:** Save and deploy the model.

---

## **🔹 6. Using DeepSpeech (For Offline & Lightweight Applications)**
DeepSpeech is **smaller** and can run on **mobile devices**.

### **📌 Step 1: Install DeepSpeech**
```bash
pip install deepspeech
```

### **📌 Step 2: Run DeepSpeech Model**
```python
import deepspeech
import numpy as np
import wave

model_path = "deepspeech-0.9.3-models.pbmm"
scorer_path = "deepspeech-0.9.3-models.scorer"

model = deepspeech.Model(model_path)
model.enableExternalScorer(scorer_path)

def transcribe_deepspeech(audio_path):
    with wave.open(audio_path, "rb") as wf:
        audio = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
    return model.stt(audio)

print(transcribe_deepspeech("audio_sample.wav"))
```
✔️ **Why Use DeepSpeech?**
- **Works completely offline**.
- **Fast** and lightweight.
- **Less accurate** than Whisper/Wav2Vec.

🚀 **Next Step:** Fine-tune it on Nigerian speech.

---

## **🔹 7. Deploying Your Speech-to-Text API**
After choosing **Whisper, Wav2Vec, or DeepSpeech**, you should serve it **via an API**.

### **📌 Step 1: Create a FastAPI Endpoint**
```python
from fastapi import FastAPI, UploadFile
import whisper
import tempfile

app = FastAPI()
model = whisper.load_model("small")

@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile):
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.write(await file.read())
    temp.close()
    
    result = model.transcribe(temp.name)
    return {"transcription": result["text"]}
```

### **📌 Step 2: Run the API**
```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

✔️ **Your API is now live at `http://localhost:8000/transcribe/`!**  
✔️ Send an **MP3 file** to transcribe it.

---

## **🔹 Conclusion**
| **Model** | **Best For** | **Training Required?** | **Works Offline?** |
|-----------|-------------|----------------------|------------------|
| **Whisper** | Best accuracy, ready-to-use | ❌ No | ❌ No |
| **Wav2Vec 2.0** | Custom language support | ✅ Yes | ✅ Yes |
| **DeepSpeech** | Fast, offline speech-to-text | ✅ Yes | ✅ Yes |

### **🚀 Next Steps**
✅ **Decide on a model** (Whisper for quick results, Wav2Vec for fine-tuning).  
✅ **Train Wav2Vec 2.0 if you need Nigerian language support.**  
✅ **Deploy your model using FastAPI or Flask.**  
✅ **Integrate it into your web/mobile app.**  

Would you like help **training Wav2Vec 2.0** on custom Nigerian datasets? 🚀

<br>

---
---
---

### **Where to Put the Speech-to-Text Code in Your Project?**  

Your project already has a well-organized **directory structure**, so let's place the **Speech-to-Text (STT) code** in the **right locations** for maximum modularity and ease of use.

---

### **📌 1. Where to Put the STT Model Code?**
Since the **speech-to-text model** is a critical **component of your AI pipeline**, it should go into the **models/** directory.

📂 **Recommended location:**
```
transcription_project/
├── models/
│   ├── speech_to_text/
│   │   ├── __init__.py
│   │   ├── whisper_stt.py      # (For Whisper model)
│   │   ├── wav2vec_stt.py      # (For Wav2Vec 2.0 model)
│   │   ├── deepspeech_stt.py   # (For DeepSpeech model)
│   │   ├── train_wav2vec.py    # (Fine-tuning Wav2Vec 2.0)
│   │   ├── utils.py            # (Helper functions)
│   ├── text_to_text/           # (Text translation models)
│   ├── text_to_speech/         # (Text-to-speech models)
```

📌 **Why?**  
- **Modular**: Each model has a separate script (`whisper_stt.py`, `wav2vec_stt.py`, etc.).
- **Scalable**: You can add more models later without cluttering your project.
- **Easy integration**: Other scripts can import these models like:
  ```python
  from models.speech_to_text.whisper_stt import transcribe_audio
  ```

---

### **📌 2. Where to Put the STT API Code?**
To serve transcriptions via an **API**, place the **FastAPI backend code** in the **backend/app/** directory.

📂 **Recommended location:**
```
transcription_project/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── routes.py       # (API Routes)
│   │   ├── models.py       # (Database models)
│   │   ├── utils.py        # (Helper functions)
│   │   ├── stt_api.py      # (Speech-to-text API)
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── run.py
```

📌 **Why?**  
- **Separation of concerns**: The API logic is separate from model code.
- **RESTful design**: The API will handle requests from your **web/mobile frontend**.

🔹 **How to call the API from your frontend?**
```javascript
fetch("http://localhost:8000/transcribe/", {
    method: "POST",
    body: formData  // Uploads the audio file
})
.then(response => response.json())
.then(data => console.log("Transcription:", data.transcription));
```

---

### **📌 3. Where to Put Training Scripts?**
If you plan to **train Wav2Vec 2.0**, store **training scripts** in the **scripts/** directory.

📂 **Recommended location:**
```
transcription_project/
├── scripts/
│   ├── preprocess_data.py   # (Prepares data for training)
│   ├── train_wav2vec.py     # (Fine-tunes Wav2Vec 2.0)
│   ├── evaluate_model.py    # (Evaluates the trained model)
```

📌 **Why?**  
- **Keeps scripts separate from model inference.**
- **Makes it easy to retrain your models later.**
- **Reusability**: You can modify and re-run training scripts independently.

---

### **📌 4. Where to Save Transcriptions?**
To **store transcriptions** in **MongoDB**, modify your **processed text directory**.

📂 **Recommended location:**
```
transcription_project/
├── data/
│   ├── processed/
│   │   ├── text/
│   │   │   ├── json/          # (Final transcriptions stored here)
│   │   │   ├── transcriptions.py  # (Code for saving transcripts)
```

📌 **How to Save Transcriptions to MongoDB?**
```python
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["transcription_db"]
collection = db["transcriptions"]

def save_transcription(audio_file, text):
    collection.insert_one({"audio_file": audio_file, "transcription": text})

save_transcription("english/kjv/mp3bible/01_Genesis.wav", "In the beginning God created the heavens and the earth.")
```

---

### **📌 Final Summary**
| **Component** | **Directory** | **File Name** |
|--------------|-------------|--------------|
| Whisper STT Model | `models/speech_to_text/` | `whisper_stt.py` |
| Wav2Vec 2.0 Model | `models/speech_to_text/` | `wav2vec_stt.py` |
| DeepSpeech Model | `models/speech_to_text/` | `deepspeech_stt.py` |
| STT API | `backend/app/` | `stt_api.py` |
| Training Script | `scripts/` | `train_wav2vec.py` |
| Transcription Storage | `data/processed/text/` | `transcriptions.py` |

---

## **🚀 Next Steps**
✅ **Implement Whisper in `whisper_stt.py`**  
✅ **Train Wav2Vec 2.0 with `train_wav2vec.py`**  
✅ **Deploy the STT API via FastAPI in `stt_api.py`**  
✅ **Store transcriptions in `data/processed/text/json/`**

Would you like help implementing **MongoDB storage for transcriptions?** 🚀

---
---
---


---

## **🔹 4. Build the Web & Mobile Apps**
### **Backend & API**
- **Expose endpoints** for transcription (`/transcribe`, `/upload`).
- **Return processed text** and audio metadata.
- **Store transcriptions** in MongoDB.

### **Frontend**
- **Web (React/Vue/Angular)**
  - Upload `.mp3` files and get real-time transcription.
  - View transcriptions by language.
- **Mobile (Flutter/React Native)**
  - Record voice and get live transcriptions.
  - Store & search transcriptions locally.

---

## **🔹 5. Deploy Everything**
### **📌 Steps for Deployment**
1. **Deploy Backend API**
   - Use **Docker + FastAPI/Flask** for scalability.
   - Deploy on **AWS, DigitalOcean, or Render**.
2. **Deploy Web App**
   - Use **Vercel (React)** or **Netlify** for static sites.
3. **Deploy Mobile App**
   - Publish on **Google Play Store & Apple App Store**.

---

## **🚀 Next Steps Checklist**
✔️ **Fix KJV `.wav` file placement**  
✔️ **Ensure preprocessing works correctly**  
✔️ **Build API for transcription**  
✔️ **Integrate speech-to-text model**  
✔️ **Deploy and test in real-world conditions**  

Would you like help **setting up the API** or **training a model for transcription**? 🚀