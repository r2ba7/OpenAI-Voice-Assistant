import json
import time

from etl.authentications import *
from text_processing import text2speech
from utils import general_utils




Instructions = general_utils.read_instructions("documents/role.txt")

async def async_chatRequest(user_input, temperature=0.9, frequency_penalty=0.2, presence_penalty=0, conversation_history=None, Instructions=Instructions):
    
    conversation = [{"role": "system", "content": Instructions}]

    if conversation_history:
        conversation.append({"role": "system", 
                             "content": f"Here is the history of the conversation between you and the client: {conversation_history}"})

    conversation.append({"role": "user", "content": user_input})
    completion_stream = await async_client.chat.completions.create(
            model='gpt-4',
            messages=conversation,
            temperature=temperature,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stream=True,
    )
    
    chunks = []
    async for chunk in completion_stream:
        content = chunk.choices[0].delta.content or ""
        chunks.append(content)

    response = "".join(chunks)

    response_data = json.loads(response)

    text, reaction = response_data['text'], response_data['reaction']
    # reaction is sent here
    print("text:", text, "reaction:", reaction)
    text2speech.convert2speech(text)
    return text


def sync_chatRequest(user_input, temperature=0.9, frequency_penalty=0.2, presence_penalty=0, conversation_history=None, Instructions=Instructions):
    if Instructions:
        conversation = [{"role": "system", "content": Instructions}]
    else:
        raise Exception("Instructions not found")

    if conversation_history:
        conversation.append({"role": "system", "content": conversation_history})

    conversation.append({"role": "user", "content": user_input})
    completion = sync_client.chat.completions.create(
            model='gpt-4',
            messages=conversation,
            temperature=temperature,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            )
    
    chat_response = completion.choices[0].message.content
    response_data = json.loads(chat_response)
    text, reaction = response_data['text'], response_data['reaction']
    # send reaction here
    print("text:", text, "reaction:", reaction)
    text2speech.convert2speech(text)
    return text, reaction


def startConv_chatRequest(user_transcription, temperature=0.9, frequency_penalty=0.2, presence_penalty=0):
    prompt = (
        "You're a  translator and expert in Arabic and English languages. \
        Perform the following steps on the recieved transcription: \
        1. Determine if the transcription is in Arabic or English. \
        2. Identify and correct any errors in the transcription. \
            Errors may include words from different languages being incorrectly transcribed or words being mistranslated. \
            For example, 'hello' being said as 'هلو', or 'marhaba' being detected as English instead of Arabic. \
        3. If any part of the transcription is in a language other than Arabic or English, translate that part into English. \
        4. Your output must be a JSON format only, with no introductory or explaining sentences, \
            with two keys: text, containing the corrected, recognized, or translated word in its original or English language, \
            and language, indicating the identified origin language of the sentence/word which either 'English' or 'Arabic', \
            or 'English' for translated segments."
    )

    conversation = [{"role": "system", "content": prompt}]
    conversation.append({"role": "user", "content": f"Transcription: {user_transcription}"})

    completion = sync_client.chat.completions.create(
            model='gpt-4',
            messages=conversation,
            temperature=temperature,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            )
    
    chat_response = completion.choices[0].message.content
    response_data = json.loads(chat_response)
    text, language = response_data['text'], response_data['language']
    return text, language.lower()