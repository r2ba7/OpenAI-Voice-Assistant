import re, os, requests, openai, time
import pandas as pd, numpy as np, warnings
from etl.authentications import *

def wait_on_run(run, thread, assistant_id):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id, assistant_id=assistant_id)
        time.sleep(0.5)
    return run

def submit_message(assistant_id, thread, user_message_content, user_instructions=None):
    """
    assistant_id: The ID of the assistant.
    thread: The thread for each run.
    user_message_content: The input content from the user
    user_instructions: The history of the messages between.
    """
    message = client.beta.threads.messages.create(thread_id=thread.id, role="user", content=user_message_content)
    run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant_id, additional_instructions=user_instructions)
    return message, run

def create_thread_and_run(user_input, assistant_id, instructions=None):
    thread = client.beta.threads.create()
    message, run = submit_message(assistant_id=assistant_id, thread=thread, user_message_content=user_input, user_instructions=instructions)
    return thread, run, message


def get_response(thread, message):
    messages_list = client.beta.threads.messages.list(thread_id=thread.id, order="asc", after=message.id)
    return messages_list


class AssistantInteraction:
    def __init__(self, client, ASSISTANT_ID):
        self.client = client
        self.ASSISTANT_ID = ASSISTANT_ID
        self.run = None
        self.thread = None
        self.message = None

    def submit_message(self, user_message_content, user_instructions=None):
        message = self.client.beta.threads.messages.create(thread_id=self.thread.id, role="user", content=user_message_content)
        run = self.client.beta.threads.runs.create(thread_id=self.thread.id, assistant_id=self.ASSISTANT_ID, additional_instructions=user_instructions)
        return message, run
    
    def wait_on_run(self):
        while self.run.status == "queued" or self.run.status == "in_progress":
            self.run = self.client.beta.threads.runs.retrieve(thread_id=self.thread.id, run_id=self.run.id, assistant_id=self.ASSISTANT_ID)
            time.sleep(0.5)
    
    def create_thread_and_run(self, user_input, user_instructions=None):
        self.thread = self.client.beta.threads.create()
        self.message, self.run = self.submit_message(assistant_id=self.ASSISTANT_ID, user_message_content=user_input, 
                                                     user_instructions=user_instructions)
        self.run = self.wait_on_run(self.ASSISTANT_ID)
        return self.thread, self.run, self.message


    def get_response(self):
        messages_list = self.client.beta.threads.messages.list(thread_id=self.thread.id, order="asc", after=self.message.id)
        return messages_list