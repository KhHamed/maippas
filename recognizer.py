import speech_recognition as sr

# إنشاء كائن للتعرف على الصوت
r = sr.Recognizer()

# استخدام الميكروفون كمصدر للصوت
with sr.Microphone() as source:
    print("Speak ...")
    audio = r.listen(source)  # تسجيل الصوت

    try:
        # تحويل الصوت لنص باستخدام Google
        text = r.recognize_google(audio, language="en-US")
        print("Text:", text)
    except sr.UnknownValueError:
        print("Could not hear what you said")
    except sr.RequestError:
        print("connection lost ")
