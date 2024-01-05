import json
import time

from etl.authentications import *
from text_processing import text2speech
from utils import general_utils




instuctions = general_utils.read_instructions("documents/role.txt")

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


def startConv_chatRequest(user_input, temperature=0.9, frequency_penalty=0.2, presence_penalty=0):
    conversation = [{"role": "system", "content": "You're a bilingual assistant trained to recognize, understand, and correct both Arabic and English languages. \
                     When given an input – a word or a sentence – your task is to detect its origin language, even if it was transcribed or written in another script or language. \
                     If the input contains words from a language other than English or Arabic, translate only those words into English, keeping the rest of the input unchanged. \
                     You should consider common transliterations and recognize words from one language that are commonly used or known in another (e.g., 'Hello' written as 'هلو'). \
                     In cases where the input is entirely in a language other than English or Arabic, translate the entire input to English. \
                     Your output must be a dictionary, with two keys: text, containing the corrected, recognized, or translated word in its original or English language, \
                     and language, indicating the identified origin language of the word or 'English' for translated segments."}]
    
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
    text, language = response_data['text'], response_data['language']
    return text, language.lower()

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