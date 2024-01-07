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
import main, setup
from text_processing import text2speech, text_generation, speech2text
from utils import general_utils

app = FastAPI()
logger = general_utils.get_logger(__name__)

# TO RUN: python -m uvicorn app:app --reload

@app.get("/")
async def root():
    return {"message": "Hello World! I'm Rabah, the programmer of Rabeh. | 7/1/2024 - voice assistant - Trial 1."}


@app.post("/request_chat")
def request_assistant():
    start_time = time.time()
    client_id, conv_history, conv_found, conv_history_instructions = main.clientRecognition()
    language = main.startConversationPrompt()
    
    while True:
        user_prompt, _ = speech2text.getPrompt(language) 
        logger.info(f"Transcript: {user_prompt}")

        exit_flag = main.exitConversation(user_prompt=user_prompt)
        if exit_flag:
            break
        
        text, reaction = main.conversationCycle(language=language, user_input=user_prompt, conversation_history=conv_history_instructions)

        if reaction == "other":
            conv_history.append(f"user:{user_prompt}"); conv_history.append(f"assistant:{text}");
            
    is_save = main.saveConversationPrompt(language)
    main.saveConversation(is_save=is_save, conv_found=conv_found,
                             client_id=client_id, conv_history=conv_history)
        
    minutes, seconds = divmod(time.time() - start_time, 60)
    print(f"Time it took is: {int(minutes)} minutes and {int(seconds)} seconds")
    return {"conversation": conv_history}