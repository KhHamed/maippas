from langdetect import detect
import speech_recognition as sr


r = sr.Recognizer()

with sr.Microphone() as source:
    print("Speak ...")
    audio = r.listen(source)


text = r.recognize_google(audio)

lang = detect(text)

print(lang)   # ar, en, fr, ...