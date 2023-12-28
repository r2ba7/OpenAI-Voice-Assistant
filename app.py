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
    return {"message": "Hello World! I'm Rabah. | 28/12/2023 - voice assitant - Trial 1."}


@app.post("/request_chat")
def request_assistant():
    exit_commands = ['اخرج', 'exit', 'أخرج', 'اخرج', 'انهاء', 'end']
    is_save, language = speech2text.save_conv()

    # take picture -> compare picture -> retrieve user id and chat, make it all inside image_processing function and folder.
    # add internet retrieval
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
    text2speech.convert2speech("Lets start conversation - لنبدأ المحادثة")
    while True:
        try:
            prompt_data = speech2text.getPrompt(language)
            if prompt_data is not None:
                user_prompt, _ = prompt_data
                if user_prompt:
                    logger.info(f"Transcript: {user_prompt}")
                else:
                    logger.info("Failed to get the transcript.")
            else:
                logger.info("No prompt data returned.")

        except Exception as e:
            raise e

        if any(command.lower() in user_prompt.strip().lower() for command in exit_commands) or (user_prompt.strip().lower() is None):
            break
        
        chat_response = asyncio.run(text_generation.async_chatRequest(user_input=user_prompt))
        # chat_response = text_generation.sync_chatRequest(user_input=user_prompt)
        conversation.append({'user': user_prompt})
        conversation.append({'assistant': chat_response})


    if is_save:
        pass
        # Save in database here.
    end_time = time.time()
    time_difference_seconds = end_time - start_time

    # Extract minutes and seconds from the time difference
    minutes, seconds = divmod(time_difference_seconds, 60)

    # Print the time in minutes and seconds
    print(f"Time it took is: {int(minutes)} minutes and {int(seconds)} seconds")
    # Update the chat of the user
    return {"conversation": conversation}
        

