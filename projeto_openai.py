from openai import OpenAI
from dotenv import load_dotenv
import speech_recognition as sr
from io import BytesIO
from playsound import playsound
from pathlib import Path
import os

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

recognizer = sr.Recognizer()

text_to_audio_model = "tts-1"
audio_to_text_model = "whisper-1"
chat_model = 'gpt-3.5-turbo'
max_tokens = 100
temperature = 1

AUDIO_FILE = 'assistant_speech.mp3'

def save_audio():
    with sr.Microphone() as source:
        print('Ouvindo...')
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)
    return audio

def audio_to_text():
    audio = save_audio()
    wav_data = BytesIO(audio.get_wav_data())
    wav_data.name = 'audio.wav'
    response = client.audio.transcriptions.create(
        model=audio_to_text_model,
        file=wav_data,
        language='pt',
    )
    return response.text

def model_assistant(message):
    response = client.chat.completions.create(
        messages=message,
        model=chat_model,
        max_tokens=max_tokens,
        temperature=temperature
    )
    return response.choices[0].message.content


def text_to_audio(text):
    response = client.audio.speech.create(
        model=text_to_audio_model,
        voice='onyx',
        input=text
    )
    if Path(AUDIO_FILE).exists():
        Path(AUDIO_FILE).unlink()
    response.write_to_file(AUDIO_FILE)
    playsound(AUDIO_FILE)

if __name__ == '__main__':
    messages = []
    while True:
        transcription = audio_to_text()
        messages.append({'role':'user', 'content': transcription})
        print('User: ', transcription)
        model_response = model_assistant(messages)
        messages.append({'role': 'assistant', 'content': model_response})
        text_to_audio(model_response)
        print(model_response)