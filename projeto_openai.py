from openai import OpenAI
from dotenv import load_dotenv
import speech_recognition as sr
from io import BytesIO
from playsound import playsound
from pathlib import Path
from datetime import datetime
import os
import re

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Defina OPENAI_API_KEY no arquivo .env")

client = OpenAI(api_key=OPENAI_API_KEY)
recognizer = sr.Recognizer()

# Configurações básicas do projeto
TEXT_TO_AUDIO_MODEL = "tts-1"
AUDIO_TO_TEXT_MODEL = "whisper-1"
CHAT_MODEL = "gpt-3.5-turbo"
MAX_TOKENS = 120
TEMPERATURE = 1
LANGUAGE = "pt"
VOICE = "onyx"
AUDIO_FILE = Path("assistant_speech.mp3")
TRANSCRIPT_FILE = Path("conversation_log.txt")
MAX_HISTORY_MESSAGES = 10
EXIT_COMMANDS = {"sair da conversa", "encerrar", "tchau"}


def save_audio(timeout=5, phrase_time_limit=20):
    with sr.Microphone() as source:
        print("Ouvindo...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(
            source,
            timeout=timeout,
            phrase_time_limit=phrase_time_limit,
        )
    return audio


def audio_to_text():
    audio = save_audio()
    wav_data = BytesIO(audio.get_wav_data())
    wav_data.name = "audio.wav"

    response = client.audio.transcriptions.create(
        model=AUDIO_TO_TEXT_MODEL,
        file=wav_data,
        language=LANGUAGE,
    )
    return response.text.strip()


def build_messages(history, user_text):
    """Mantém um contexto curto para reduzir custo e ruído."""
    system_message = {
        "role": "system",
        "content": "Responda em português de forma clara, curta e objetiva.",
    }
    recent_history = history[-MAX_HISTORY_MESSAGES:]
    return [system_message, *recent_history, {"role": "user", "content": user_text}]


def model_assistant(messages):
    response = client.chat.completions.create(
        messages=messages,
        model=CHAT_MODEL,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
    )
    return response.choices[0].message.content.strip()


def text_to_audio(text):
    response = client.audio.speech.create(
        model=TEXT_TO_AUDIO_MODEL,
        voice=VOICE,
        input=text,
    )

    if AUDIO_FILE.exists():
        AUDIO_FILE.unlink()

    response.write_to_file(AUDIO_FILE)
    playsound(str(AUDIO_FILE))


def save_conversation(role, content):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with TRANSCRIPT_FILE.open("a", encoding="utf-8") as file:
        file.write(f"[{timestamp}] {role}: {content}\n")


def should_exit(text):
    confirmation = text.lower().strip()
    confirmation = re.sub(r'[^\w\s]', '', confirmation)
    print(confirmation)
    return confirmation in EXIT_COMMANDS


def main():
    history = []

    print("Assistente iniciado. Diga 'sair da conversa', 'encerrar' ou 'tchau' para encerrar.")

    while True:
        try:
            transcription = audio_to_text()
            if not transcription:
                print("Nenhum áudio reconhecido.")
                continue

            print("User:", transcription)
            save_conversation("user", transcription)

            if should_exit(transcription):
                print("Encerrando...")
                break

            messages = build_messages(history, transcription)
            model_response = model_assistant(messages)

            history.append({"role": "user", "content": transcription})
            history.append({"role": "assistant", "content": model_response})

            print("Assistant:", model_response)
            save_conversation("assistant", model_response)
            text_to_audio(model_response)

        except sr.WaitTimeoutError:
            print("Tempo de espera excedido. Tente falar novamente.")
        except KeyboardInterrupt:
            print("\nExecução interrompida pelo usuário.")
            break
        except Exception as error:
            print(f"Erro: {error}")


if __name__ == "__main__":
    main()
