"""
the main pattern is:
audio = listen()
text = speech_to_text(audio)
response = ask_ollama(text)
speak(response)
"""
import speech_recognition as sr
import pyttsx3

def main():
    # listen to the words
    r = sr.Recognizer()
    audio = listen_to_words(r)
    # writing the words to the screen
    user = writing_down_the_words_I_said(r, audio)
    print("User:", user)
    # connecting ollama

    # generating response

    # speaking the response


def listen_to_words(r):


    with sr.Microphone() as source:
        print("Speak ...")
        audio = r.listen(source)
    
    return audio


def writing_down_the_words_I_said(r, audio):
    # languages = ["en-US", "ar-EG", "fr-FR"]

    # for lang in languages:
    #     try:
    #         text = r.recognize_google(audio, language=lang)
    #         return text

    try:
        text = r.recognize_google(audio, language="en-US")
        return text

        languages = ["en-US", "ar-EG"]

    except sr.UnknownValueError:
        print("Could not hear what you said")
    except sr.RequestError:
        print("connection lost ")



if __name__ == "__main__":
    main()

