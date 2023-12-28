import speech_recognition as sr
import re, os, requests, openai, time, io, asyncio
import pandas as pd, numpy as np, warnings
from utils import general_utils
from etl.authentications import *
from text_processing import text2speech

logger = general_utils.get_logger(__name__)


def transcribe_audio(buffer, language=None, temperature=0):
    try:
        transcript = sync_client.audio.transcriptions.create(
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


def save_conv():
    no_save_commands = ['No', 'None', 'لا', 'لأ', 'Nah']
    language = None

    text2speech.convert2speech("Would you like to save this conversation? - هل تحب ان تحتفظ بالمحادثة؟")

    while True:
        try:
            prompt_data = getPrompt(language if language else None)
            if prompt_data is not None:
                prompt, detected_language = prompt_data
                if detected_language == 'arabic':
                    language = 'ar'
                elif detected_language == 'english':
                    language = 'en'

                if prompt:
                    logger.info(f"Detected Language: {language}, Transcript: {prompt}")
                else:
                    logger.info("Failed to get the transcript.")
            else:
                logger.info("No prompt data returned.")

        except Exception as e:
            raise e

        if any(command.lower() in prompt.strip().lower() for command in no_save_commands) or (prompt.strip().lower() is None):
            is_save = False

        else:
            is_save = True
        
        return is_save, language
        