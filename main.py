import time
import string

from etl import database_methods
from etl.authentications import *
from image_processing import client_recognition, image_capturing
from text_processing import text2speech, speech2text
from utils import general_utils

logger = general_utils.get_logger(__name__)


def clientRecognition(accuracy_threshold=50):
    """
    Recognizes a client from a captured image and retrieves or initializes their conversation history.

    Parameters:
    - accuracy_threshold (int, optional): The minimum accuracy percentage required for a valid image 
      recognition match. Defaults to 50.

    Returns:
    - client_id (str): The unique identifier of the client. It's either retrieved from the database if 
      the client is recognized or created anew if not.
    - conv_history (list of str): The conversation history between the client and the assistant. Each 
      entry in the list is a string representing one line of conversation.
    - conv_found (bool): A flag indicating whether an existing conversation history was found (True) 
      or not (False).
    - chat_history_instructions (str or None): A formatted string containing the conversation history, 
      accompanied by instructions for how it can be used. Returns None if no conversation history is found.

    The function captures an image, tries to recognize the client, and retrieves or initializes the chat 
    history based on the recognition result.
    """
    client_image = image_capturing.captureImage()
    # time.sleep(5)
    client_id = client_recognition.getClient(client_image=client_image, accuracy_threshold=accuracy_threshold)
    # time.sleep(5)
    conv_history_instructions = None
    conv_history = []
    conv_found = False

    if client_id:
        conv_history, conv_found = database_methods.retrieveHistory(client_id)
        if conv_found:
            formatted_conv_history = "\n".join(conv_history)
            conv_history_instructions = (
                f"Here is a chat conversation between you and the client:\n{formatted_conv_history}\n"
                "You can use that history to know information about the client, and also you can fetch information from previous chats."
            )

    else:
        client_id = database_methods.createClient()
        database_methods.createImage(client_image, client_id)

    # time.sleep(5)
    return client_id, conv_history, conv_found, conv_history_instructions


def startConversationPrompt():
    start_commands = ['start', 'go', 'begin', 'بدأ', 'بدا', 'انطلق']
    take_photo_commands = ['take', 'photo', 'تصوير', 'صور']
    # dont exit from take photo until frame is returned, use this frame to retrieve client information from database
    logger.info(f"In Start")
    text2speech.convert2speech("Please say start or go - برجاء قول ابدأ او انطلق")
    while True:
        prompt, detected_language = speech2text.getPrompt(None) 
        # English and Arabic here to adjust messages, in getPrompt I make sure that output must be in English or Arabic.
        if detected_language == 'arabic':
            language = 'ar'
            start_message = "لنبدأ المحادثة"
            keyword_error_message = "برجاء المحاوله مره اخرى"

        elif detected_language == 'english':
            language = 'en'
            start_message = "Lets start conversation"
            keyword_error_message = "Please try again to start conversation"

        logger.info(f"Detected Language: {language}, Transcript: {prompt}")

        if any(command.lower() in prompt.strip().lower() for command in start_commands):
            logger.info(f"{prompt.strip().lower()} - Conversation will start.")
            text2speech.convert2speech(start_message)
            return language
        
        else:
            text2speech.convert2speech(keyword_error_message)
            continue
        

def saveConversationPrompt(language):
    no_save_commands = ['no', 'none', 'لا', 'لأ']
    save_commands = ['yes', 'save', 'ya', 'yeah', 'okay', 'ah', 'ايوه', 'اجل', 'أجل', 'بلى', 'نعم']

    # English and Arabic here to adjust messages, in getPrompt I make sure that output must be in English or Arabic.
    if language == 'ar':
        save_message = "هل تحب ان تحتفظ بالمحادثة؟"
        keyword_error_message = "برجاء المحاوله مره اخرى"

    elif language == 'en':
        save_message = "Would you like to save this conversation?"
        keyword_error_message = "Please try again"

    text2speech.convert2speech(save_message)

    while True:
        prompt, _ = speech2text.getPrompt(language)
        logger.info(f"Transcript: {prompt}")

        if any(command.lower() in prompt.strip().lower() for command in no_save_commands):
            logger.info(f"{prompt.strip().lower()} - Not saved.")
            is_save = False
            return is_save

        elif any(command.lower() in prompt.strip().lower() for command in save_commands):
            logger.info(f"{prompt.strip().lower()} - saved.")
            is_save = True
            return is_save

        else:
            text2speech.convert2speech(keyword_error_message)


def exitConversation(user_prompt):
    exit_commands = ['end', 'exit', 'finish', 'اخرج', 'أخرج', 'اخرج', 'انهاء']
    translator = str.maketrans('', '', string.punctuation)
    user_prompt_words = user_prompt.strip().lower().translate(translator).split()
    
    if any(command.lower() in user_prompt_words for command in exit_commands):
        return True
    
    else:
        return False


def saveConversation(is_save, conv_found, client_id, conv_history):
    if is_save:
        if conv_found:
            logger.info(f"Updated conversation for client: {client_id}")
            database_methods.updateConv(conv_history=conv_history, client_id=client_id)

        else:
            logger.info(f"Created conversation for client: {client_id}")
            database_methods.createConv(conv_history=conv_history, client_id=client_id)

    else:
        logger.warning(f"Conversation wasn't saved for client: {client_id}")

    
