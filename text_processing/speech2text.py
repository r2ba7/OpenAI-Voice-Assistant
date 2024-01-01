import speech_recognition as sr
import re, os, requests, openai, time, io, asyncio
import pandas as pd, numpy as np, warnings
from utils import general_utils
from etl.authentications import *
from text_processing import text2speech

logger = general_utils.get_logger(__name__)


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

async def async_transcribe_audio(buffer, language=None, temperature=0.2):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, transcribeAudio, buffer, language, temperature)


def getPrompt(language=None):
    recognizer = sr.Recognizer()

    while True:
        try:
            with sr.Microphone() as source:
                logger.info("Listening")
                audio = recognizer.listen(source)

            logger.info("Finished Recording")
            buffer = io.BytesIO(audio.get_wav_data()); buffer.name = 'test.wav';
            transcript = asyncio.run(async_transcribe_audio(buffer, language))
            if transcript is None:
                continue

            if language or transcript.language in ['english', 'arabic']:
                return transcript.text, transcript.language
            
            logger.info(f"{transcript.text, transcript.language}")
            text2speech.convert2speech("Language not detected, Please Try again")

        except Exception as e:
            logger.error(f"Error during recording or processing: {e}")



def startConversation():
    start_commands = ['start', 'go', 'بدأ', 'بدا', 'انطلق']
    logger.info(f"In Start")

    while True:
        prompt, detected_language = getPrompt(None) 
        # English and Arabic here to adjust messages, in getPrompt I make sure that output must be in English or Arabic.
        if detected_language == 'arabic':
            language = 'ar'
            start_message = "لنبدأ المحادثة"
            keyword_error_message = "برجاء المحاوله مره اخرى"

        elif detected_language == 'english':
            language = 'en'
            start_message = "Lets start conversation"
            keyword_error_message = "Please try again to start conversation"

        logger.info(f"Detected Language: {language}, Transcript: {prompt}")

        if any(command.lower() in prompt.strip().lower() for command in start_commands):
            logger.info(f"{prompt.strip().lower()} - Conversation will start.")
            text2speech.convert2speech(start_message)
            return language
        
        else:
            text2speech.convert2speech(keyword_error_message)
            continue
        

def saveConversation(language):
    no_save_commands = ['no', 'none', 'لا', 'لأ']
    save_commands = ['yes', 'save', 'ya', 'yeah', 'okay', 'ah', 'ايوه', 'اجل', 'أجل', 'بلى', 'نعم']

    # English and Arabic here to adjust messages, in getPrompt I make sure that output must be in English or Arabic.
    if language == 'ar':
        save_message = "هل تحب ان تحتفظ بالمحادثة؟"
        keyword_error_message = "برجاء المحاوله مره اخرى"

    elif language == 'en':
        save_message = "Would you like to save this conversation?"
        keyword_error_message = "Please try again"

    text2speech.convert2speech(save_message)

    while True:
        prompt, _ = getPrompt(language)
        logger.info(f"Transcript: {prompt}")

        if any(command.lower() in prompt.strip().lower() for command in no_save_commands):
            logger.info(f"{prompt.strip().lower()} - Not saved.")
            is_save = False
            return is_save

        elif any(command.lower() in prompt.strip().lower() for command in save_commands):
            logger.info(f"{prompt.strip().lower()} - saved.")
            is_save = True
            return is_save

        else:
            text2speech.convert2speech(keyword_error_message)