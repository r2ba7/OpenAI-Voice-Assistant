import io, pygame
import pandas as pd, numpy as np, warnings
from etl.authentications import *

def convert2speech(message):
    response = sync_client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        response_format="opus",
        input=message,
    )
    
    audio_stream = io.BytesIO(response.content)
    
    # Initialize Pygame
    pygame.mixer.init()
    
    # Create a Pygame sound object from the audio stream
    sound = pygame.mixer.Sound(audio_stream)
    
    # Play the audio
    sound.play()
    
    # Wait for the audio to finish playing
    while pygame.mixer.get_busy():
        pygame.time.delay(50)