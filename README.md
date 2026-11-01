# Maippas

Maippas is a local voice-chat app. It listens for a wake word, transcribes speech
with Vosk, sends the conversation to Ollama, and reads the response aloud using
the system's text-to-speech voices.

## Requirements

- Python
- [Ollama](https://ollama.com/) running on this computer
- A microphone and speakers
- The small English Vosk speech-recognition model

## Setup

1. Install the Python dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

   Microphone input also requires PyAudio. If it is not installed with your
   environment, install it with:

   ```powershell
   python -m pip install pyaudio
   ```

2. Download the [Vosk small English model](https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip)
   and extract it so the model files are directly inside `models\vosk`. The app
   expects the model directory at that path by default (not an extra
   `vosk-model-small-en-us-0.15` directory nested inside it).

3. Start Ollama and download the default chat model:

   ```powershell
   ollama pull tinyllama:1.1b
   ```

## Run

From the project directory, start the app with:

```powershell
python app.py
```

Say **“Maippas”**, **“M”**, or **“Mai”** to start a request. You can say the
wake word followed by your request, or say the wake word by itself and wait for
the prompt. Say **“quit”**, **“exit”**, **“stop”**, **“bye”**, **“goodbye”**, or
**“shutdown”** after the wake word to exit.

Speech recognition runs locally with Vosk. Chat responses use the local Ollama
service, and conversation messages are stored in `conversations.sqlite3` in
the project directory by default. The assistant is prompted to speak like a
pirate. On Windows, Maippas selects the Microsoft Zira voice when available;
otherwise it uses the system's default voice.

## Configuration

These environment variables are optional:

| Variable | Default | Description |
| --- | --- | --- |
| `OLLAMA_MODEL` | `tinyllama:1.1b` | Ollama model used to generate responses. Pull the model with `ollama pull <model>` before using it. |
| `VOSK_MODEL_PATH` | `models\vosk` | Path to the extracted Vosk model directory. |
| `MAIPPAS_DB_PATH` | `conversations.sqlite3` in the project directory | Path to the SQLite database. |

For example, in PowerShell:

```powershell
$env:OLLAMA_MODEL = "llama3.2"
$env:VOSK_MODEL_PATH = "C:\models\vosk"
$env:MAIPPAS_DB_PATH = "C:\data\maippas.sqlite3"
python app.py
```
