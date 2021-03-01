import pyttsx3
import random

engine = pyttsx3.init()
engine.setProperty('rate', 300)

def get_tts(sentence):
    file_name = "resources/sounds/" + str(random.randint(0, 999999)) + ".mp3"
    engine.save_to_file(sentence, file_name)
    engine.runAndWait()
    return file_name
