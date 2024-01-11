import asyncio
import io

import numpy as np
import pandas as pd
import speech_recognition as sr

from etl.authentications import *
from text_processing import text2speech, text_generation
from utils import general_utils

logger = general_utils.get_logger(__name__)


def getPrompt(language=None, temperature=0):
    def transcribeAudio(buffer, language, temperature):
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

    async def async_transcribe_audio(buffer, language, temperature):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, transcribeAudio, buffer, language, temperature)

    recognizer = sr.Recognizer()

    while True:
        try:
            with sr.Microphone() as source:
                logger.info("Listening")
                # recognizer.adjust_for_ambient_noise(source) 
                audio = recognizer.listen(source)

            logger.info("Finished Recording")
            buffer = io.BytesIO(audio.get_wav_data()); buffer.name = 'test.wav';
            transcript = asyncio.run(async_transcribe_audio(buffer, language, temperature))
            if transcript is None:
                logger.warning("Transcription failed, trying again...")
                text2speech.convert2speech("Transcription failed, trying again")
                continue

            else:
                if language is None:
                    corrected_text, corrected_language = text_generation.startConv_chatRequest(transcript.text)
                    logger.info(f"corrected text: {corrected_text}, corrected language: {corrected_language}, transcript text:{transcript.text}")
                    
                    if corrected_language not in ['english', 'arabic']:
                        logger.warning("Transcription failed or language not supported, trying again...")
                        text2speech.convert2speech("Transcription failed or language not supported, trying again...")
                        continue
                        
                    return corrected_text, corrected_language
                
                else:
                    logger.info(transcript.text)
                    return transcript.text, transcript.language

        except Exception as e:
            logger.error(f"Error during recording or processing: {e}")