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
    """
    Handles the entire cycle of a conversation with an AI assistant.

    Description:
        This function manages the conversation flow with a user, starting from user recognition and ending with 
        the option to save the conversation. It continuously captures user input through speech recognition, 
        processes it, and generates responses using the AI assistant. The function also tracks the duration of 
        the conversation.

    Returns:
        dict: A dictionary containing the entire conversation history.
    
    Note:
        The conversation cycle is broken when the user indicates a desire to exit. The function then offers 
        the option to save the conversation history. The total duration of the conversation is also displayed.
    """
    start_time = time.time()
    client_id, conv_history, conv_found = main.clientRecognition()
    language = main.startConversationPrompt()
    current_conv = []
    while True:
        user_prompt, _ = speech2text.getPrompt(language) 
        logger.info(f"Transcript: {user_prompt}")

        exit_flag = main.exitConversation(user_prompt=user_prompt)
        if exit_flag:
            break
        

        assistant_response, reaction = main.conversationCycle(language=language, user_input=user_prompt, 
                                                              conversation_history=conv_history+current_conv)
        if reaction == "other":
            current_conv.append((user_prompt, assistant_response))
        
        time.sleep(1)

    is_save = main.saveConversationPrompt(language)
    main.saveConversation(is_save=is_save, conv_found=conv_found,
                          client_id=client_id, conv_history=current_conv)
        
    minutes, seconds = divmod(time.time() - start_time, 60)
    print(f"Time it took is: {int(minutes)} minutes and {int(seconds)} seconds")
    return {"conversation": conv_history}