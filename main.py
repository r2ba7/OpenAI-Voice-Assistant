import time
import string

from etl import database_methods
from etl.authentications import *
from image_processing import client_recognition, image_capturing
from text_processing import text2speech, speech2text, text_generation
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
    client_id = client_recognition.getClient(client_image=client_image, accuracy_threshold=accuracy_threshold)
    conv_history = []; conv_found = False;

    if client_id:
        conv_history, conv_found = database_methods.retrieveHistory(client_id)

    else:
        client_id = database_methods.createClient()
        database_methods.createImage(client_image, client_id)

    return client_id, conv_history, conv_found


def say_message(message, language):
    if language == 'en':
        text2speech.convert2speech(message)

    elif language == 'ar':
        text2speech.convert2speech_elevenlabs(message)

    else:
        text2speech.convert2speech(message)

def is_command_present(commands, prompt, exit_flag=False):
    if not exit_flag:
        return any(command.lower() in prompt.strip().lower() for command in commands)
    
    else:
        return any(command.lower() in prompt for command in commands)


def startConversationPrompt():
    def get_language_specific_messages_start(language):
        messages = {
            'ar': ("لنبدأ المحادثة" , "برجاء المحاوله مره اخرى"),
            'en': ("Lets start conversation", "Please try again")
        }
        return messages[language]

    start_commands = ['start', 'go', 'begin', 'بدأ', 'بدا', 'انطلق']

    say_message("Please say start or go For English", language='en')
    say_message("برجاء قول ابدأ او انطلق للعربيه", language='ar')

    while True:
        prompt, detected_language = speech2text.getPrompt(None)
        print(prompt) 
        language = 'ar' if detected_language == 'arabic' else 'en'
        start_message, keyword_error_message = get_language_specific_messages_start(language)
        if is_command_present(start_commands, prompt):
            say_message(start_message, language)
            logger.info(f"{prompt.strip().lower()} - Conversation will start.")
            return language
        
        else:
            say_message(keyword_error_message, language)
            logger.error(f"{keyword_error_message}")
            continue


def conversationCycle(language, user_input, conversation_history):
    def get_language_specific_messages_cycle(language):
        messages = {
            'ar': ("برجاء تكرار المحاوله مره اخرى"),
            'en': ("Please repeat again")
        }
        return messages[language]

    while True:
        chat_response, reaction = text_generation.sync_chatRequest(language=language, user_input=user_input, 
                                                          conversation_history=conversation_history)
        if chat_response is not None and reaction is not None:
            return chat_response, reaction
        
        else:
            error_message = get_language_specific_messages_cycle(language=language)
            say_message(error_message, language)
            continue


def saveConversationPrompt(language):
    def get_language_specific_messages_save(language):
        messages = {
            'ar': ("هل تحب ان تحتفظ بالمحادثة؟", "برجاء المحاوله مره اخرى"),
            'en': ("Would you like to save this conversation?", "Please try again")
        }
        return messages[language]
    

    no_save_commands = ['no', 'none', 'لا', 'لأ']
    save_commands = ['yes', 'save', 'ya', 'yeah', 'okay', 'ah', 'ايوه', 'اجل', 'أجل', 'بلى', 'نعم']

    save_message, keyword_error_message = get_language_specific_messages_save(language=language)
    say_message(save_message, language)
    
    while True:
        prompt, _ = speech2text.getPrompt(language)
        logger.info(f"Transcript: {prompt}")

        if is_command_present(no_save_commands, prompt):
            return False

        elif is_command_present(save_commands, prompt):
            return True

        else:
            say_message(keyword_error_message, language)

def exitConversation(user_prompt):
    exit_commands = ['end', 'exit', 'finish', 'اخرج', 'أخرج', 'اخرج', 'انهاء']
    translator = str.maketrans('', '', string.punctuation)
    user_prompt_words = user_prompt.strip().lower().translate(translator).split()
    if is_command_present(exit_commands, user_prompt_words, True):
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

    
