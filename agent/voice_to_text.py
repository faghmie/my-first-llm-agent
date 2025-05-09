import speech_recognition  as sr

class AgentListener:
    def listen_and_convert(self):
        # Initialize the recognizer
        recognizer = sr.Recognizer()

        # Use the default microphone as the audio source
        with sr.Microphone() as source:
            recognizer.energy_threshold = 300
            print("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Listening... Speak now!")

            try:
                # Listen to the user's input
                audio = recognizer.listen(
                    source, 
                    timeout = 20,
                    phrase_time_limit = 90
                )
                # audio = recognizer.listen(source)
                print("Processing...")

                # Use Google Web Speech API to convert audio to text
                text = recognizer.recognize_google(audio)
                print(f"Recognized command: {text}")
                return text

            except sr.WaitTimeoutError:
                print("No speech detected within the timeout period.")
                return None
            except sr.UnknownValueError:
                print("Could not understand the audio.")
                return None
            except sr.RequestError as e:
                print(f"Could not request results from Google Web Speech API; {e}")
                return None

    def process_command(self, command):
        # Add your custom processing logic here
        if command:
            command = command.lower()
            print(f"Processing command: {command}")
            # Example: Respond to a "hello" command
            if "hello" in command:
                print("Hello! How can I assist you?")
            elif "exit" in command:
                print("Exiting...")
                exit()
            else:
                print("Command not recognized.")

    def use(self):
        while True:
            command = self.listen_and_convert()
            self.process_command(command)

if __name__ == "__main__":
    listener = AgentListener()
    listener.use()