# Utilidades de conversión de audio y reconocimiento de voz
from pydub import AudioSegment
import speech_recognition as sr

def convert_ogg_to_wav(ogg_path, wav_path):
    audio = AudioSegment.from_ogg(ogg_path)
    audio.export(wav_path, format="wav")

def recognize_speech_from_audio(wav_path):
    r = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio_data = r.record(source)
        try:
            text = r.recognize_google(audio_data, language="es-MX")
            return text.lower()
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            return None
