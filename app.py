"""
Local voice chat using Vosk for speech recognition and Ollama for responses.
"""
import json
import os
import re
import sqlite3
from pathlib import Path

import ollama
import pyttsx3
import speech_recognition as sr


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = Path(
    os.getenv("MAIPPAS_DB_PATH", str(BASE_DIR / "conversations.sqlite3"))
)
VOSK_MODEL_PATH = Path(
    os.getenv("VOSK_MODEL_PATH", str(BASE_DIR / "models" / "vosk"))
)
MAX_HISTORY_MESSAGES = 20
WAKE_WORDS = {"maippas", "maipas", "maipass", "mai", "my", "may", "m", "em"}
QUIT_COMMANDS = {"quit", "exit", "stop", "bye", "goodbye", "shutdown"}
SYSTEM_PROMPT = "You are a helpful assistant that speaks like a pirate."


def main():
    if not connect_to_ollama():
        print("Could not connect to Ollama.")
        return

    try:
        model = load_vosk_model()
    except RuntimeError as exc:
        print(exc)
        return

    database = initialize_database()
    conversation_id = start_conversation(database)
    recognizer = sr.Recognizer()
    engine = pyttsx3.init()
    configure_tts(engine)

    print("Maippas is listening. Say 'Maippas', 'M', or 'Mai' to start.")
    print("Say a wake word followed by 'quit' to exit.")

    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.3)
            while True:
                audio = listen_to_words(recognizer, source)
                if audio is None:
                    continue

                recognized_text = recognize_local_speech(model, audio)
                if not recognized_text:
                    continue

                user_text = remove_wake_word(recognized_text)
                if user_text is None:
                    continue

                if not user_text:
                    print("Maippas: Yes?")
                    read_the_response(engine, "Yes?")
                    audio = listen_to_words(recognizer, source)
                    if audio is None:
                        continue
                    user_text = recognize_local_speech(model, audio)
                    if not user_text:
                        continue

                user_text = user_text.strip()
                print("User:", user_text)

                if is_quit_command(user_text):
                    print("Maippas: Goodbye!")
                    read_the_response(engine, "Goodbye!")
                    break

                try:
                    response = generate_response(database, conversation_id, user_text)
                except Exception as exc:
                    print(f"Ollama response error: {exc}")
                    continue

                read_the_response(engine, response)
    except Exception as exc:
        print(f"Voice chat error: {exc}")
    finally:
        database.close()


def load_vosk_model():
    try:
        from vosk import Model
    except ImportError as exc:
        raise RuntimeError(
            "Vosk is not installed. Run 'pip install -r requirements.txt'."
        ) from exc

    if not VOSK_MODEL_PATH.is_dir():
        raise RuntimeError(
            "Vosk model not found. Download and unpack the small English model "
            "from https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip "
            f"to '{VOSK_MODEL_PATH}', or set VOSK_MODEL_PATH to your model folder."
        )

    try:
        return Model(str(VOSK_MODEL_PATH))
    except Exception as exc:
        raise RuntimeError(
            f"Could not load the Vosk model at '{VOSK_MODEL_PATH}': {exc}"
        ) from exc


def initialize_database():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    database = sqlite3.connect(DATABASE_PATH)
    database.execute("PRAGMA foreign_keys = ON")
    database.execute(
        """
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY,
            started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    database.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY,
            conversation_id INTEGER NOT NULL REFERENCES conversations(id),
            role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
            content TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    database.commit()
    return database


def start_conversation(database):
    cursor = database.execute("INSERT INTO conversations DEFAULT VALUES")
    database.commit()
    return cursor.lastrowid


def listen_to_words(recognizer, source):
    try:
        return recognizer.listen(source, timeout=5, phrase_time_limit=8)
    except sr.WaitTimeoutError:
        return None


def recognize_local_speech(model, audio):
    from vosk import KaldiRecognizer

    sample_rate = 16_000
    recognizer = KaldiRecognizer(model, sample_rate)
    audio_data = audio.get_raw_data(convert_rate=sample_rate, convert_width=2)
    recognizer.AcceptWaveform(audio_data)
    return json.loads(recognizer.FinalResult()).get("text", "").strip()


def remove_wake_word(text):
    words = re.findall(r"\w+", text.lower())
    if words and words[0] == "hey":
        words = words[1:]
    if not words or words[0] not in WAKE_WORDS:
        return None
    return " ".join(words[1:])


def is_quit_command(text):
    return text.lower().strip("?!., ") in QUIT_COMMANDS


def generate_response(database, conversation_id, user_input):
    database.execute(
        "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
        (conversation_id, "user", user_input),
    )
    database.commit()

    history = database.execute(
        """
        SELECT role, content
        FROM (
            SELECT id, role, content
            FROM messages
            ORDER BY id DESC
            LIMIT ?
        )
        ORDER BY id
        """,
        (MAX_HISTORY_MESSAGES,),
    ).fetchall()
    if history and history[0][0] == "assistant":
        history = history[1:]
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend({"role": role, "content": content} for role, content in history)

    model_name = os.getenv("OLLAMA_MODEL", "tinyllama:1.1b")
    response = ollama.chat(
        model=model_name,
        messages=messages,
        keep_alive="10m",
        options={"num_predict": 128},
    )
    answer = response["message"]["content"].strip()
    database.execute(
        "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
        (conversation_id, "assistant", answer),
    )
    database.commit()

    print(f"\nMaippas: {answer}")
    return answer


def connect_to_ollama():
    try:
        ollama.list()
        return True
    except Exception as exc:
        print(f"Ollama connection error: {exc}")
        return False


def configure_tts(engine):
    engine.setProperty("rate", 170)
    for voice in engine.getProperty("voices"):
        if "Microsoft Zira Desktop - English (United States)" in voice.name:
            engine.setProperty("voice", voice.id)
            break


def read_the_response(engine, text):
    engine.say(text)
    engine.runAndWait()


if __name__ == "__main__":
    main()
