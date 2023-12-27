import speech_recognition as sr
import re, os, requests, openai, time, io, asyncio
import pandas as pd, numpy as np, warnings
from utils import general_utils
from etl.authentications import *
from text_processing import text2speech

logger = general_utils.get_logger(__name__)


def transcribe_audio(buffer, language=None, temperature=0):
    try:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=buffer,
            response_format='verbose_json',
            language=language,
            temperature=temperature
        )
        return transcript
    
    except Exception as e:
        logger.error(f"Error during transcription: {e}")
        return None

async def async_transcribe_audio(buffer, language=None, temperature=0.2):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, transcribe_audio, buffer, language, temperature)


def getPrompt(language=None, max_retries=3):
    recognizer = sr.Recognizer()
    retry_count = 0

    while retry_count < max_retries:
        try:
            with sr.Microphone() as source:
                logger.info("Listening")
                audio = recognizer.listen(source)

            logger.info("Finished Recording")
            buffer = io.BytesIO(audio.get_wav_data())
            buffer.name = 'test.wav'

            transcript = asyncio.run(async_transcribe_audio(buffer, language))
            if transcript is None:
                retry_count += 1
                continue

            if language or transcript.language in ['english', 'arabic']:
                return transcript.text, transcript.language

            text2speech.convert2speech("Language not detected, Please Try again")

        except Exception as e:
            logger.error(f"Error during recording or processing: {e}")
        finally:
            retry_count += 1

    logger.error("Maximum retries reached or failed to process audio")
    return None