import json
import time

from nltk.tokenize import sent_tokenize

from etl.authentications import *
from text_processing import text2speech
from utils import general_utils

logger = general_utils.get_logger(__name__)
Instructions = general_utils.read_instructions("documents/role.txt")
MAX_CONTEXT_HISTORY = 20


def get_moderation(question):
    """
    Check the question is safe to ask the model

    Parameters:
        question (str): The question to check

    Returns a list of errors if the question is not safe, otherwise returns None
    """

    errors = {
        "hate": "Content that expresses, incites, or promotes hate based on race, gender, ethnicity, religion, nationality, sexual orientation, disability status, or caste.",
        "hate/threatening": "Hateful content that also includes violence or serious harm towards the targeted group.",
        "self-harm": "Content that promotes, encourages, or depicts acts of self-harm, such as suicide, cutting, and eating disorders.",
        "sexual": "Content meant to arouse sexual excitement, such as the description of sexual activity, or that promotes sexual services (excluding sex education and wellness).",
        "sexual/minors": "Sexual content that includes an individual who is under 18 years old.",
        "violence": "Content that promotes or glorifies violence or celebrates the suffering or humiliation of others.",
        "violence/graphic": "Violent content that depicts death, violence, or serious physical injury in extreme graphic detail.",
    }
    response = openai.Moderation.create(input=question)
    if response.results[0].flagged:
        # get the categories that are flagged and generate a message
        result = [
            error
            for category, error in errors.items()
            if response.results[0].categories[category]
        ]
        return result
    return None


def sync_chatRequest(language, user_input, conv_history=None, temperature=0.9, frequency_penalty=0.2, presence_penalty=0):
    """
    Generates a chat response using GPT-4 based on user input and conversation history.

    Args:
        language (str): The language of the chat.
        user_input (str): The latest user input for the chat.
        conv_history (list, optional): History of past user and assistant messages. Default is None.
        temperature (float, optional): Controls the randomness of the response. Default is 0.9.
        frequency_penalty (float, optional): Penalizes repetitive responses. Default is 0.2.
        presence_penalty (float, optional): Encourages diverse responses. Default is 0.

    Raises:
        Exception: If no instructions are provided.

    Returns:
        tuple: (response text, reaction type) or (None, None) on error.

    Description:
        This function processes a chat request by sending the user's input and conversation history to GPT-4.
        It returns the model's response as text along with a reaction type. If there's an error or if the response
        format is unexpected, it returns None for both values.
    """
    instructions = f'Your name is Rabeh, a Bilingual Sales Assistant. \
        Match the language of each query with precision: always respond in {language} for {language} queries. \
        You are an expert in various products, adept at highlighting their benefits and unique features. \
        For Arabic queries, use Arabic script even for English terms or brand names. \
        Always match {language} in your response, even if the name of the user or certain words in the prompt are typically associated with another language. \
        Maintain consistency in {language}, regardless of the name of the user or specific terms used in their query. \
        Your responses should be concise, informative, and persuasive, tailored to the language of the query without language mixing. \
        Responses must adhere to a strict format: a JSON with exactly two keys, "text" and "reaction". The "text" key contains your response to the query, \
        and the "reaction" key categorizes your response sentiment as "greetings", "farewell", or "other". \
        Ensure that all parts of the response, including any introductory elements, are encapsulated within this dictionary structure, \
        maintaining the format: {{"text": "your response", "reaction": "response category"}}, \
        Example response: {{"text": "Hello, my name is Rabeh, how can I help you today?", "reaction": "greetings"}}. \
        Responses must be no longer than three sentences.'
    
    messages = [{"role": "system", "content": instructions}]

    print
    if conv_history:
        for user_prompt, assistant_response in conv_history[-MAX_CONTEXT_HISTORY:]:
            messages.append({"role": "user", "content": user_prompt})
            messages.append({"role": "assistant", "content": assistant_response})

    messages.append({"role": "user", "content": user_input})
    completion = sync_client.chat.completions.create(
            model='gpt-4',
            messages=messages,
            temperature=temperature,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            )
    
    chat_response = completion.choices[0].message.content
    try:
        response_data = json.loads(chat_response)
        print("text:", response_data['text'], "reaction:", response_data['reaction'])
        sentences = sent_tokenize(response_data['text'])
        for sentence in sentences:
            text2speech.convert2speech(sentence) if language == 'en' else text2speech.convert2speech_elevenlabs(sentence)

        return chat_response, response_data['reaction']

    except:
        logger.warning(f"Error chat response: {chat_response}")
        return None, None

    

def startConv_chatRequest(user_transcription, temperature=0.9, frequency_penalty=0.2, presence_penalty=0):
    system_prompt = (
        'You are an expert in both Arabic and English languages. \
        Your primary role involves correcting spelling discrepancies in transcribed text. Follow these guidelines for each task: \
        1. Determine whether the transcription is in Arabic or English. \
        2. Correct any transcription errors. This includes rectifying words from different languages that are incorrectly transcribed or mistranslated. \
        For instance, correcting "هلو" to "hello", or identifying "marhaba" as English, not Arabic even though its an Arabic word. \
        3. Translate any non-Arabic and non-English segments into English. \
        4. Present your output exclusively in a JSON format. The output must contain two keys: "text", which holds the corrected, recognized, \
        or translated word in its original or English language, and "language", indicating the identified origin language (either "english" or "arabic") \
        of the sentence or word. Example, following this format: {"text": "start", "language": "english"} \
        Use "english" for any translated segments. This format must be strictly adhered to for all responses.'
    )

    completion = sync_client.chat.completions.create(
            model='gpt-4',
            messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_transcription
            }
        ],
            temperature=temperature,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            )
    
    chat_response = completion.choices[0].message.content
    try:
        response_data = json.loads(chat_response)
        text, language = response_data['text'], response_data['language']
        return text, language.lower()
    
    except:
        logger.warning(chat_response)
        return None, None

    