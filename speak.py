# This is a sample Python script.
import sys
from gtts import gTTS
from playsound import playsound
import os
import pyttsx3

# To install pyttsx3, use :
#   sudo apt-get install espeak
#   pip3 install pyttsx3 (not sure if you need to do this)
# 
# For Gtts, the video says that you use
#   sudo apt install mpg123
#   sudo pip3 install gTTs

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(name)  # Press Ctrl+F8 to toggle the breakpoint.


def say_hi_internet(name):
#    text = 'Hi' + name + ', To say this, I need an internet connection'
    text = name
    language = 'en'
    myobj = gTTS(text=text, lang=language, slow=False)

    try:
        os.remove("welcome1.mp3")
    except:
        pass
    myobj.save("welcome1.mp3")
    playsound("welcome1.mp3")
    os.remove("welcome1.mp3")


def say_hi_local(name):
    engine = pyttsx3.init()
    engine.setProperty('rate',150)
#    engine.setProperty('voice','english+m1')
    engine.setProperty('voice','english+f2')
    engine.say('Hello' + name + ', to say this, I do NOT need an internet connection ')
    engine.runAndWait()


def say_hi_local_different_voices(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    for voice in voices:
        print(voice.id)
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

#    print_hi(text)
    say_hi_internet(text)
#    say_hi_local(text)
#    say_hi_local_different_voices(text')
