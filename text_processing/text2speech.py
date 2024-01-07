import requests

import io, pygame
from elevenlabs import play
from etl.authentications import *

def convert2speech(message):
    response = sync_client.audio.speech.create(
        model="tts-1",
        voice="echo",
        response_format="opus",
        input=message,
    )

    audio_stream = io.BytesIO(response.content)
    pygame.mixer.init()
    sound = pygame.mixer.Sound(audio_stream)
    sound.play()

    while pygame.mixer.get_busy():
        pygame.time.delay(50)

def convert2speech_elevenlabs(message, voice_id="21m00Tcm4TlvDq8ikWAM", api_key=ELEVENLABAS_API_KEY):
    url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream?optimize_streaming_latency=3'
    headers = {
        'Accept': 'audio/mpeg',
        'xi-api-key': api_key,
        'Content-Type': 'application/json'
    }
    data = {
        'text': message,
        # 'model_id': 'eleven_monolingual_v1',
        'model_id': 'eleven_multilingual_v2',
        'voice_settings': {
            'stability': 0.5,
            'similarity_boost': 0.5
        }
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        # play(response.content, False, False)
        audio_stream = io.BytesIO(response.content)
        pygame.mixer.init()
        sound = pygame.mixer.Sound(audio_stream)
        sound.play()
        while pygame.mixer.get_busy():
            pygame.time.delay(50)
            
    else:
        print(f"Error: {response.status_code}, {response.text}")