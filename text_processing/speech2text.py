import speech_recognition as sr
import re, os, requests, openai, time, io
import pandas as pd, numpy as np, warnings
from etl.authentications import *


def getPrompt():
    recognizer = sr.Recognizer(); microphone = sr.Microphone()
    print("Listening...")
    with microphone as source:
        audio = recognizer.listen(source)

    print("Finished recording.")
    buffer = io.BytesIO(audio.get_wav_data()); buffer.name = 'test.wav';
    
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=buffer
        )

    return transcript.text