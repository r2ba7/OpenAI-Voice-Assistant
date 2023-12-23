import re, os, requests, json, openai, io, pygame
import pandas as pd, numpy as np, warnings
from etl.authentications import *

def convert2speech(message):
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        response_format="opus",
        input=message,  
    )
    with io.BytesIO(response.content) as audio_stream:
        # Initialize Pygame
        pygame.mixer.init()

        # Load the audio stream
        pygame.mixer.music.load(audio_stream)

        # Play the audio
        pygame.mixer.music.play()

        # Keep the program running while the audio plays
        while pygame.mixer.music.get_busy():
            pygame.time.delay(50)