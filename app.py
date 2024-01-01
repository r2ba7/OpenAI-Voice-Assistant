import asyncio, time

from datetime import datetime
from openai import OpenAI
from typing import Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from text_processing import text_generation, text2speech, speech2text
from utils import general_utils
from etl.authentications import *


app = FastAPI()
logger = general_utils.get_logger(__name__)

# TO RUN: python -m uvicorn app:app --reload

@app.get("/")
async def root():
    return {"message": "Hello World! I'm Rabah, the programmer of Rabeh. | 1/1/2024 - voice assistant - Trial 1."}


@app.post("/request_chat")
def request_assistant():
    
    # take picture -> compare picture -> retrieve user id and chat, make it all inside image_processing function and folder.
    # example: check_user_id + retrieve history
    user_id = "1"
    
    conversation_state: Dict[str, list] = {}
    
    if user_id not in conversation_state:
        conversation_state[user_id] = []

    conversation = conversation_state[user_id]
    if conversation == []:
        user_instructions = None

    else:
        user_instructions = conversation
        assistant_instructions = assistant_instructions + " Found Conversation History: " + user_instructions

    start_time = time.time()
    language = speech2text.startConversation()
    exit_commands = ['اخرج', 'exit', 'أخرج', 'اخرج', 'انهاء', 'end']
    while True:
        user_prompt, _ = speech2text.getPrompt(language) 
        logger.info(f"Transcript: {user_prompt}")

        if any(command.lower() in user_prompt.strip().lower() for command in exit_commands) or (user_prompt.strip().lower() is None):
            break
        
        # chat_response = asyncio.run(text_generation.async_chatRequest(user_input=user_prompt))
        text, reaction = text_generation.sync_chatRequest(user_input=user_prompt)
        conversation.append({'user': user_prompt})
        conversation.append({'assistant': text})

    is_save = speech2text.saveConversation(language)
    if is_save:
        # Save in database here.
        pass
        
    end_time = time.time()
    time_difference_seconds = end_time - start_time

    # Extract minutes and seconds from the time difference
    minutes, seconds = divmod(time_difference_seconds, 60)

    # Print the time in minutes and seconds
    print(f"Time it took is: {int(minutes)} minutes and {int(seconds)} seconds")
    # Update the chat of the user
    return {"conversation": conversation}
        

