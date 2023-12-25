import speech_recognition as sr
import re, os, requests, openai, time, io
import pandas as pd, numpy as np, warnings
from etl.authentications import *


def getPrompt(language=None):
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        
        # recognizer.adjust_for_ambient_noise(source)
        # time.sleep(1)
        print("Listening...")
        audio = recognizer.listen(source)

    print("Finished recording.")
    buffer = io.BytesIO(audio.get_wav_data()); buffer.name = 'test.wav';
    
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=buffer,
        response_format='verbose_json',
        language=language,
        # temperature=0.2
        )

    return transcript.text, transcript.language