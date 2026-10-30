import pyttsx3
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Adjust the rate as needed
voices=engine.getProperty('voices')
for voice in voices:
    if 'Microsoft Zira Desktop - English (United States)' in voice.name:
        engine.setProperty('voice', voice.id)
        break
engine.say('Sally sells seashells by the seashore.')
# engine.say('The quick brown fox jumped over the lazy dog.')
engine.runAndWait()