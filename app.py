from text_processing import text_generation, text2speech, speech2text
from utils import utils
from etl.authentications import *
from api_edit import adjust_assistant

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio

from datetime import datetime
from openai import OpenAI
from typing import Dict

app = FastAPI()

# TO RUN: python -m uvicorn app:app --reload

@app.get("/")
async def root():
    return {"message": "Hello World! I'm Rabah. | 23/12/2023 - voice assitant - Trial 1."}

class AssistantRequest(BaseModel):
    pass

class UploadFilesRequest(BaseModel):
    files_path: str

class DeleteFilesRequest(BaseModel):
    file_ids: list


@app.post("/upload_files")
def upload_files2assitant(upload_files_request: UploadFilesRequest):
    adjust_assistant.create_files(ASSISTANT_ID, upload_files_request.files_path)


@app.post("/delete_files")
def upload_files2assitant(delete_files_request: DeleteFilesRequest):
    adjust_assistant.delete_files(ASSISTANT_ID, delete_files_request.file_ids)


@app.post("/request_chat")
def request_assistant():
    assistant = client.beta.assistants.retrieve(ASSISTANT_ID)
    assistant_instructions = assistant.instructions
    # take picture -> compare picture -> retrieve user id and chat, make it all inside image_processing function and folder.

    # # example: check_user_id + retrieve history
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

    AssistantInteractionObject = text_generation.AssistantInteraction(client, ASSISTANT_ID)
    
    exit_commands = ['اخرج', 'exit', 'أخرج', 'اخرج', 'انهاء', 'end']
    language = None
    while True:
        print(language)
        if language is not None:
            prompt, _ = speech2text.getPrompt(language)

        else:
            prompt, language = speech2text.getPrompt(language)
            if language == 'arabic':
                language='ar'

            else:
                language='en'

        print(prompt)
        if any(command.lower() in prompt.strip().lower() for command in exit_commands) or (prompt.strip().lower() is None):
            break

        AssistantInteractionObject.create_thread_and_run(user_input=prompt, user_instructions=assistant_instructions)
        response = AssistantInteractionObject.get_response()
        utils.pretty_print(response)
        for msg in response.data:
            role = msg.role
            response = msg.content[0].text.value
            if role == 'assistant': 
                # Check state and emotion between 1,2,3,4 and sent it in API
                text2speech.convert2speech(response)

            temp_dict = {role: response}
            conversation.append(temp_dict)

    # Update the chat of the user
    return {"conversation": conversation}
        

