import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import pyttsx3
import requests
import pyaudio 
from pydub import AudioSegment
import threading
import wave
from tkinter import Tk

DEEPGRAM_API_KEY = "YOUR-KEY"
COHERE_API_KEY = "YOUR-KEY"

# Headers for API requests
deepgram_headers = {
    "Authorization": f"Token {DEEPGRAM_API_KEY}",
    "Content-Type": "audio/wav",
}

def deepgram_tts(text, output_file="output_voice.mp3"):
    url = "https://api.deepgram.com/v1/speak?model=aura-asteria-en"
    payload = {
        "text": text
    }
    try:
        response = requests.post(url, headers={
            "Authorization": f"Token {DEEPGRAM_API_KEY}",
            "Content-Type": "application/json"
        }, json=payload, verify=False)
        # Save the audio response directly to an output file
        with open(output_file, 'wb') as audio_file:
            audio_file.write(response.content)
        print(f"Synthesized audio saved to {output_file}.")
    except Exception as e:
        print(f"Error in Deepgram TTS: {e}")

def convert_to_wav(input_file, output_file):
    audio = AudioSegment.from_file(input_file) 
    audio.export(output_file, format="wav") 

def play_audio(file_path):
    if file_path.endswith(".mp3"):
        # Convert MP3 to WAV for playback
        wav_file_path = file_path.replace(".mp3", ".wav")
        convert_to_wav(file_path, wav_file_path)
        file_path = wav_file_path
    wf = wave.open(file_path, 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    chunk = 1024
    data = wf.readframes(chunk)
    while data:
        stream.write(data)
        data = wf.readframes(chunk)
    stream.stop_stream()
    stream.close()
    p.terminate()

def shorten_keyinsights_and_warn(key_insights):
    api_url = "https://api.cohere.ai/generate"
    headers = {
        "Authorization": "Bearer ",
        "Content-Type": "application/json"
    }

    prompt = f"""
For this Engine Maintainence Prediction insight: {key_insights}, generate a brief overall summary that can be quickly said via audio to the end user. Limit it to two short sentences, ensuring it can be read in under 15 seconds. Don't add anything extra that is not needed   """
    data = {
        # "model": "command-xlarge-20221108",  # or "medium" as per your needs
        "prompt": prompt,
        "max_tokens": 500,
        "temperature": 0.7
    }

    # Make the request to the Cohere API
    response = requests.post(api_url, headers=headers, json=data, verify=False) 
    response_data = response.json()
    print("API Response: ", response_data)
    
    if response.status_code == 200:
        key_insights_short = response_data.get('text', '').strip()
    else:
        key_insights_short = "Error generating insights: " + response_data.get('error', 'Unknown error')
    deepgram_tts(key_insights_short, "output_voice.mp3")
    # show_warning_and_report(key_insights_short)
    return key_insights_short


def show_warning_and_report(insights):
    # Start the text-to-speech in a separate thread
    print("Speech bro")
    summerized_insights = shorten_keyinsights_and_warn(insights)
    speechParallely = threading.Thread(target=play_audio, args=("output_voice.mp3",))
    speechParallely.start()
    def show_message():
        root = Tk()
        # root.withdraw()  # Hide the root window
        root.attributes("-topmost", True)  # Set the root window to be topmost
        messagebox.showinfo("Report", summerized_insights)
        root.destroy()

    message_thread = threading.Thread(target=show_message)
    message_thread.start()
    # Show report message

    
    # Exit the GUI after the messagebox is closed
    # root.quit()
# def play_text_to_speech(insights):
#     engine = pyttsx3.init()
#     engine.say(insights)
#     engine.runAndWait()




# def alert_user(insights):
#     root = tk.Tk()
#     root.title("Engine Alert")
#     print("called")
#     # Customize the button
#     style = ttk.Style()
#     style.configure("TButton",
#                     font=("Helvetica", 12, "bold"),
#                     background="white",
#                     foreground="black",
#                     padding=10,
#                     borderwidth=2)
#     button = ttk.Button(root, text="Check New Engine Alert", command=lambda: shorten_keyinsights_and_warn(insights), style="TButton")
#     button.pack(pady=20)
#     root.quit()