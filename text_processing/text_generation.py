import json
import time

from nltk.tokenize import sent_tokenize

from etl.authentications import *
from text_processing import text2speech
from utils import general_utils

logger = general_utils.get_logger(__name__)
Instructions = general_utils.read_instructions("documents/role.txt")
MAX_CONTEXT_HISTORY = 10

def sync_chatRequest(language, user_input, temperature=0.9, frequency_penalty=0.2, presence_penalty=0, conversation_history=None, Instructions=Instructions):
    
    if Instructions:
        conversation = [{"role": "system", "content": Instructions}]

    else:
        raise Exception("Instructions not found")

    if conversation_history:
        for user_response, assistant_response in conversation_history[-MAX_CONTEXT_HISTORY:]:
            conversation.append({ "role": "user", "content": user_response})
            conversation.append({ "role": "assistant", "content": assistant_response})

    conversation.append({"role": "user", "content": user_input})
    completion = sync_client.chat.completions.create(
            model='gpt-4',
            messages=conversation,
            temperature=temperature,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            )
    
    chat_response = completion.choices[0].message.content
    try:
        response_data = json.loads(chat_response)
        text, reaction = response_data['text'], response_data['reaction']
        print("text:", text, "reaction:", reaction)
        sentences = sent_tokenize(text)
        
        for sentence in sentences:
            print(sentence)
            text2speech.convert2speech(sentence) if language == 'en' else text2speech.convert2speech_elevenlabs(sentence)
        return text, reaction

    except:
        logger.warning(chat_response)
        return None, None

    

def startConv_chatRequest(user_transcription, temperature=0.9, frequency_penalty=0.2, presence_penalty=0):
    system_prompt = (
        "You are an expert in both Arabic and English languages. \
        Your primary role involves correcting spelling discrepancies in transcribed text. Follow these guidelines for each task: \
        1. Determine whether the transcription is in Arabic or English. \
        2. Correct any transcription errors. This includes rectifying words from different languages that are incorrectly transcribed or mistranslated. For instance, correcting 'هلو' to 'hello', or identifying 'marhaba' as Arabic, not English. \
        3. Translate any non-Arabic and non-English segments into English. \
        4. Present your output exclusively in a dictionary format. The output must contain two keys: 'text', which holds the corrected, recognized, or translated word in its original or English language, and 'language', indicating the identified origin language (either 'english' or 'arabic') of the sentence or word. \
        Use 'english' for any translated segments. This format must be strictly adhered to for all responses."
    )

    completion = sync_client.chat.completions.create(
            model='gpt-4',
            messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_transcription
            }
        ],
            temperature=temperature,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            )
    
    chat_response = completion.choices[0].message.content
    try:
        response_data = json.loads(chat_response)
        text, language = response_data['text'], response_data['language']
        return text, language.lower()
    
    except:
        logger.warning(chat_response)
        return None, None

    