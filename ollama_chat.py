import requests
import speech_recognition as sr
import pyttsx3
import json
import re
import logging

# Constants
#MODEL = "deepseek-r1:latest"
MODEL = "llama3.1:latest"
API_URL = "http://localhost:11434/api/chat"
MAX_RETRIES = 3

# Setup logging
logging.basicConfig(level=logging.INFO)

#############################################################
# SpeakText - Function to convert text to speech
#############################################################
def SpeakText(engine, command):
    engine.say(command)
    engine.runAndWait()

#############################################################
# recognize_speech_from_mic - Function to recognize speech from microphone
#############################################################
def recognize_speech_from_mic(recognizer, microphone):
    """Transcribe speech from recorded from `microphone`."""
    response = {"success": True, "error": None, "transcription": None}

    try:
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        response["transcription"] = recognizer.recognize_google(audio)
    except sr.RequestError:
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        response["error"] = "Unable to recognize speech"
    
    return response

#############################################################
# chat - Function to interact with the chatbot API
#############################################################
def chat(messages):
    retries = 0
    while retries < MAX_RETRIES:
        try:
            r = requests.post(API_URL, json={"model": MODEL, "messages": messages, "stream": True})
            r.raise_for_status()
            output = ""
            for line in r.iter_lines():
                body = json.loads(line)
                if "error" in body:
                    raise Exception(body["error"])
                if not body.get("done"):
                    message = body.get("message", {})
                    output += message.get("content", "")
                if body.get("done", False):
                    return {"role": "assistant", "content": output}
            return {}
        except requests.RequestException as e:
            retries += 1
            logging.error(f"API request failed (Attempt {retries}/{MAX_RETRIES}): {e}")
            if retries >= MAX_RETRIES:
                return {"role": "assistant", "content": "Error: Unable to connect to the chat service."}

#############################################################
# remove_think_text - Function to remove <think> tags from text
#############################################################
def remove_think_text(input_string):
    """Remove <think>...</think> tags from text."""
    return re.sub(r'<think>.*?</think>', '', input_string, flags=re.DOTALL)

#############################################################
# main - Main interaction loop
#############################################################
def main(myName, botName):
    engine = pyttsx3.init()
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    greet_text = f"Hi {myName}, Please wait for the listening prompt before speaking"
    logging.info(greet_text)
    SpeakText(engine, greet_text)
    
    messages = [
        {"role": "system", "content": f"Your name is {botName} and my name is {myName}. Only respond to my name if I ask for it. Provide the result only in text, no explanations and no formatting."}
    ]

    while True:
        logging.info("Listening for speech...")
        response = recognize_speech_from_mic(recognizer, microphone)

        if response["transcription"] and response["transcription"] != "None":
            user_input = response["transcription"]
            logging.info(f"User: {user_input}")
            messages = [
                {"role": "system", "content": f"Your name is {botName} and my name is {myName}. Only respond to my name if I ask for it. Provide the result only, no explanations."}
            ]
            messages.append({"role": "user", "content": user_input})

            message = chat(messages)
            if message.get("content"):
                clean_content = remove_think_text(message["content"])
                logging.info(f"Assistant: {clean_content}")
                SpeakText(engine, clean_content)
                messages.append(message)
            else:
                logging.error("No response from chat API.")
                SpeakText(engine, "Sorry, I couldn't get a response.")
        else:
            logging.warning("No valid speech detected. Continuing...")

if __name__ == "__main__":
    myName = 'Peter'
    botName = 'Buddy'
    main(myName, botName)
