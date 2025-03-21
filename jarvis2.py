import threading
import pyttsx3
import time
import webbrowser as wb
import speech_recognition as sr
import requests
import os

# Define a stop flag to control text-to-speech interruption and assistant termination
stop_flag = threading.Event()
flag=True
f=True #to stop the assistent perminataly using stop command 
# Define a class for command execution
class Command:
    def execute(self, assistant):
        raise NotImplementedError

# Define specific command classes for each command
class OpenApp(Command):
    def __init__(self,file):
        self.file=file
    def execute(self,assistent):
        if "whatsapp" in self.file.lower()or"whatsup" in self.file.lower():
            os.system("start whatsapp://")
        elif " microsoft" in self.file.lower():
            print(" ok" )
            if "word" in self.file.lower():
              print(" kk")
              os.system("start winword")
            elif "power point" in self.file.lower():
                os.system("start powerpnt")
            elif "excel" in self.file.lower():
              os.system("start excel")
            else:
              print("Invalid application. Please enter 'word', 'powerpoint', or 'excel'.")
        elif "calculator" in self.file.lower():
            os.system("calc")
        elif "notepad" in self.file.lower():
            os.system("notepad")
        elif "file manager" in self.file.lower():
            os.system("start explorer")
class ShutdownCommand(Command):
    def execute(self, assistant):
        assistant.say("Shutting down the system")
        assistant.say("Shutdown in 4 seconds")
        assistant.say("3 seconds")
        assistant.say("2 seconds")
        assistant.say("1 second")
        os.system('shutdown /s /t 1')

class MapLocationCommand(Command):
    def __init__(self, location):
        self.location = location
    
    def execute(self, assistant):
        url = f"https://www.google.nl/maps/place/{self.location}/"
        wb.open_new_tab(url)
        assistant.say(f"Here is {self.location}")

class TopResultCommand(Command):
    def __init__(self, result):
        self.result = result
    
    def execute(self, assistant):
        if not stop_flag.is_set():
            assistant.say("Top result: " + self.result)
        print(self.result)

# Define the VoiceAssistant class
class VoiceAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 140)
    
    def say(self, text):
        if stop_flag.is_set():
            stop_flag.clear()  # Reset the flag
            return
        self.engine.say(text)
        self.engine.runAndWait()
    
    def listen(self):
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)  # Adjust for 0.5 seconds of ambient noise
                self.recognizer.energy_threshold = self.recognizer.energy_threshold + 400 
                print("Listening...")# Adjust the energy threshold as needed
                audio = self.recognizer.listen(source)
                command_text = self.recognizer.recognize_google(audio)
                print(f"Received command: {command_text}")
                return command_text
        except sr.UnknownValueError:
            pass
        except sr.RequestError:
            pass
        return "ok"
    
    def handle_command(self, command_text):
        global flag, f
        print(command_text)
        if "go to sleep" in command_text:
            os.system('rundll32.exe powrprof.dll,SetSuspendState 0,1,0')
            flag=False
        elif command_text =="ok":
            print(command_text)
            pass
        elif "what is the time right now" in command_text:
            self.say(time.ctime())
            print(time.ctime())
            flag=False 
        elif "shutdown the system" in command_text:
            command = ShutdownCommand()
            command.execute(self)
            flag=False 
        elif "where is" in command_text:
            location = command_text.split("where is")[-1].strip()
            command = MapLocationCommand(location)
            command.execute(self)
            flag=False 
        elif "send a mail" in command_text:
            self.say("To whom would you like to send the email?")
            print("To whom would you like to send the email?")
            mail_address = input("Please enter the mail ID: ")
            # Implement sending mail here
            self.say("Mail sent.")
            flag=False 
        elif command_text.startswith("stop"):
            # Interrupt text-to-speech by setting the stop flag
            self.say("ok see you later boss")
            print("Text-to-speech interrupted.")
            stop_flag.set()
            time.sleep(1)
            flag=False
            f=False
        elif "open " in command_text.lower():
            command = OpenApp(command_text)
            command.execute(self)
            flag=False 
        else:
            # Search for query and handle the result
            search_query = command_text
            API_KEY = "AIzaSyAsNp9bjQfGOmyxKSqLVeOOm-s4TVE1QIU"
            ENGINE_ID = "c230e74fb583343d0"
            url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={ENGINE_ID}&q={search_query}"
            wb.open_new_tab(f"https://www.google.com/search?q={search_query}")
            response = requests.get(url)
            data = response.json()
            if 'items' in data:
                top_result = data['items'][0]['snippet']
                command = TopResultCommand(top_result)
                command.execute(self)
            else:
                self.say("No results found.")
                print("No results found.")
            flag=False 

# Background running functionality
def run_voice_assistant():
   # global flag
    assistant = VoiceAssistant()
    while not stop_flag.is_set() and f:
        command_text = assistant.listen()
        if command_text=='jarvis'or command_text=='Jarvis' or flag:
            assistant.say("yes boss" )
            command= assistant.listen()
            print(" jj" )
            assistant.handle_command(command)
        

# Start the voice assistant in a separate thread
if __name__ == "__main__":
    # Create a thread for the voice assistant to run in the background
    assistant_thread = threading.Thread(target=run_voice_assistant)
    assistant_thread.start()
    # Keep the main thread running, allowing the assistant to operate in the background
    while f:# check the Stop variable to stop the assistent
        time.sleep(0.5)# Keep the main thread active
    stop_flag.set()
    assistant_thread.join()
    print("Voice assistant has been stopped.")
