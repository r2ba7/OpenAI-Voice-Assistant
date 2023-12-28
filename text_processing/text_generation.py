import re, os, requests, openai, time
import pandas as pd, numpy as np, warnings
from etl.authentications import *
from utils import general_utils

instuctions = general_utils.read_instructions("documents/role.txt")

def tavily_search(query):
    search_result = tavily_client.get_search_context(query, search_depth="advanced", max_tokens=8000)
    return search_result


def chatRequest(user_input, temperature=0.9, frequency_penalty=0.2, presence_penalty=0, conversation_history=None, instuctions=instuctions):

    conversation = [{"role": "system", "content": instuctions}]

    if conversation_history:
        conversation.append({"role": "system", 
                             "content": f"Here is the history of the conversation between you and the client: {conversation_history}"})

    conversation.append({"role": "user", "content": user_input})
    completion = client.chat.completions.create(
            model='gpt-4',
            messages=conversation,
            temperature=temperature,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            )
    
    chat_response = completion.choices[0].message.content
    conversation.append({"role": "assistant", "content": chat_response})
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