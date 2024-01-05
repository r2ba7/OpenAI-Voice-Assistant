import asyncio
import string
import time
from datetime import datetime
from typing import Dict

from fastapi import FastAPI, HTTPException
from openai import OpenAI
from pydantic import BaseModel

from etl import database_methods
from etl.authentications import *
from image_processing import handling
from text_processing import text2speech, text_generation, speech2text
from utils import general_utils

app = FastAPI()
logger = general_utils.get_logger(__name__)

# TO RUN: python -m uvicorn app:app --reload

@app.get("/")
async def root():
    return {"message": "Hello World! I'm Rabah, the programmer of Rabeh. | 5/1/2024 - voice assistant - Trial 1."}


@app.post("/request_chat")
def request_assistant():
    start_time = time.time()
    is_found, data = handling.clientRecognizition()
    if is_found:
        client_id, chat_history, chat_found = data
        if chat_found:
            formatted_chat_history = "\n".join(chat_history)
            print(chat_history)
            chat_history_instructions = (
                f"Here is a chat conversation between you and the client:\n{formatted_chat_history}\n"
                "You can use that history to know information about the client, and also you can fetch information from previous chats."
            )
        else:
            chat_history_instructions = None
    
    else:
        client_id, chat_found = data
        chat_history = []
        chat_history_instructions = None

    
    language = speech2text.startConversation()
    exit_commands = ['end', 'exit', 'finish', 'اخرج', 'أخرج', 'اخرج', 'انهاء']
    while True:
        user_prompt, _ = speech2text.getPrompt(language) 
        logger.info(f"Transcript: {user_prompt}")

        translator = str.maketrans('', '', string.punctuation)
        user_prompt_words = user_prompt.strip().lower().translate(translator).split()
        if any(command.lower() in user_prompt_words for command in exit_commands):
            break
        
        # chat_response = asyncio.run(text_generation.async_chatRequest(user_input=user_prompt))
        text, reaction = text_generation.sync_chatRequest(user_input=user_prompt, conversation_history=chat_history_instructions)
        if reaction == "other":
            chat_history.append(f"user:{user_prompt}")
            chat_history.append(f"assistant:{text}")

    is_save = speech2text.saveConversation(language)
    if is_save:
        if chat_found:
           database_methods.updateConv(chat_history=chat_history, client_id=client_id)

        else:
            database_methods.createConv(chat_history=chat_history, client_id=client_id)
        
        
    end_time = time.time()
    time_difference_seconds = end_time - start_time

    # Extract minutes and seconds from the time difference
    minutes, seconds = divmod(time_difference_seconds, 60)

    # Print the time in minutes and seconds
    print(f"Time it took is: {int(minutes)} minutes and {int(seconds)} seconds")
    # Update the chat of the user
    return {"conversation": chat_history}
        

