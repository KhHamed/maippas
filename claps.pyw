import os
import subprocess
import sys
import time
import numpy as np
import pyaudio

# --- CONFIGURATION ---
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
THRESHOLD = 15000  # Adjust this based on your room's background noise

SCRIPT_TO_RUN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "your_target_script.py")  # Change this to the script you want to run on clap detection

p = pyaudio.PyAudio()

stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK,
)

try:
    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        audio_data = np.frombuffer(data, dtype=np.int16)
        peak = np.max(np.abs(audio_data))

        if peak > THRESHOLD:
            subprocess.run([sys.executable, SCRIPT_TO_RUN])
            
            # 2-second cooldown so a single clap echo doesn't trigger it twice
            time.sleep(2)

except Exception:
    # Fail silently in the background if an error occurs
    pass
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()