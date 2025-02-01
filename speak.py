# This is a sample Python script.
import sys
from gtts import gTTS
from playsound import playsound
import os
import pyttsx3

# To install pyttsx3, use :
#   sudo apt-get install espeak
#   pip install pyttsx3 (For windows)
# 
# For Gtts, the video says that you use
#   sudo apt install mpg123
#   sudo pip3 install gTTs

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(name)  # Press Ctrl+F8 to toggle the breakpoint.


def say_hi_internet(text, filename="welcome.mp3"):
    """Uses gTTS (Google Text-to-Speech) to say the given text.
    Requires an internet connection.
    """
    language = 'en'
    myobj = gTTS(text=text, lang=language, slow=False)

    try:
        if os.path.exists(filename):
            os.remove(filename)
        myobj.save(filename)
    #    os.system("play welcome1.mp3 tempo 1.2 >/dev/null 2>&1")  # If this doesn't work, comment out and use the playsound command as below
        playsound(filename)           # This works for Win10/python 3.9
    finally:
        if os.path.exists(filename):
            os.remove(filename)


def say_hi_local(text, voice_index=0, rate=150):
    """Uses pyttsx3 to say the given text locally without requiring an internet connection."""
    engine = pyttsx3.init()
    engine.setProperty('rate', rate)
    voices = engine.getProperty('voices')
    if voice_index < len(voices):
        engine.setProperty('voice', voices[voice_index].id)

#    engine.setProperty('voice','english+m1')
#    engine.setProperty('voice','english+f2')
#    engine.say(name + ', to say this, I do NOT need an internet connection ')
    engine.say(text)
    engine.runAndWait()


def say_hi_local_different_voices(text):
    """Uses pyttsx3 to say the given text in all available voices."""
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    for voice in voices:
        print(f"Using voice: {voice.id}")
        engine.setProperty('voice', voice.id)  # changes the voice
        engine.say(text)
        engine.runAndWait()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    try:
        text = sys.argv[1]
    except:
        text = "Hello world"
        pass

    try:
        voice_index = sys.argv[2]
    except:
        voice_index = 0
        pass

#    print_hi(text)
#    say_hi_internet(text)
    say_hi_local(text, voice_index)
#    say_hi_local_different_voices(text)
