import re, os, requests, json, time
import openai
import pandas as pd, numpy as np, warnings
from etl.authentications import *
from utils import general_utils
from text_processing import text2speech

instuctions = general_utils.read_instructions("documents/role.txt")

def tavily_search(query):
    search_result = tavily_client.get_search_context(query, search_depth="advanced", max_tokens=8000)
    return search_result


async def async_chatRequest(user_input, temperature=0.9, frequency_penalty=0.2, presence_penalty=0, conversation_history=None, instuctions=instuctions):
    
    conversation = [{"role": "system", "content": instuctions}]

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

def sync_chatRequest(user_input, temperature=0.9, frequency_penalty=0.2, presence_penalty=0, conversation_history=None, instuctions=instuctions):

    conversation = [{"role": "system", "content": instuctions}]

    if conversation_history:
        conversation.append({"role": "system", 
                             "content": f"Here is the history of the conversation between you and the client: {conversation_history}"})

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
    return chat_response


class AssistantInteraction:
    def __init__(self, client, ASSISTANT_ID):
        self.client = client
        self.ASSISTANT_ID = ASSISTANT_ID
        self.run = None
        self.thread = None
        self.message = None

    def submit_message(self, user_message_content, user_instructions=None):
        message = self.client.beta.threads.messages.create(thread_id=self.thread.id, role="user", content=user_message_content)
        run = self.client.beta.threads.runs.create(thread_id=self.thread.id, assistant_id=self.ASSISTANT_ID, instructions=user_instructions)
        return message, run
    
    def wait_on_run(self):
        while self.run.status == "queued" or self.run.status == "in_progress":
            self.run = self.client.beta.threads.runs.retrieve(thread_id=self.thread.id, run_id=self.run.id)
            time.sleep(0.5)
    
    def create_thread_and_run(self, user_input, user_instructions=None):
        self.thread = self.client.beta.threads.create()
        self.message, self.run = self.submit_message(user_message_content=user_input, user_instructions=user_instructions)
        self.wait_on_run()

    def get_response(self):
        messages_list = self.client.beta.threads.messages.list(thread_id=self.thread.id, order="asc", after=self.message.id)
        return messages_list