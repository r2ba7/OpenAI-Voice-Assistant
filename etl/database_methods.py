import datetime

import cv2
import numpy as np

from etl.authentications import db
from utils import general_utils

logger = general_utils.get_logger(__name__)


def createClient():
    try:
        current_time = datetime.datetime.now()
        client_document = {
            'createdAt': current_time
        }
        result = db.clients.insert_one(client_document)
        client_id = result.inserted_id
        logger.info(f"New client was created with ID: {client_id}")
        return client_id

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return None

def createImage(client_image, client_id):
    try:
        image_bytes = cv2.imencode('.jpg', client_image)[1].tobytes()
        current_time = datetime.datetime.now()
        image_document = {
            'client_id': client_id,
            'imageData': image_bytes,
            'createdAt': current_time,
            'updatedAt': current_time
        }

        db.images.insert_one(image_document)
        logger.info(f"Created image for client: {client_id}.")

    except Exception as e:
        logger.error(f"Error in save_image: {str(e)}")

def createConv(chat_history, client_id):
    try:
        current_time = datetime.datetime.now()
        chat_document = {
            'client_id': client_id,
            'chatHistory': chat_history,
            'createdAt': current_time
        }

        db.messages.insert_one(chat_document)
        logger.info(f"Created chat history for client: {client_id}.")

    except Exception as e:
        logger.error(f"Error in createConv: {str(e)}")
    
def updateConv(chat_history, client_id):
    try:
        current_time = datetime.datetime.now()
        result = db.messages.update_one(
            {'client_id': client_id},
            {
                '$set': {
                    'chatHistory': chat_history,
                    'updatedAt': current_time
                }
            }
        )
        if result.matched_count == 0:
            logger.warning(f"No conversation found for client_id: {client_id}")
        elif result.modified_count == 0:
            logger.info(f"No updates were necessary for client_id: {client_id}")
        else:
            logger.info(f"Conversation updated for client_id: {client_id}")

    except Exception as e:
        logger.error(f"Error in updateConv: {str(e)}")

def retrieveHistory(client_id):
    try:
        chat_document = db.messages.find_one({'client_id': client_id})
        chat_found = False
        if chat_document:
            chat_history = chat_document['chatHistory']
            chat_found = True
            logger.info(f"Chat history was found for client_id: {client_id}")
            return chat_history, chat_found
        
        else:
            logger.info(f"No chat history was found for client_id: {client_id}")
            return [], chat_found
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return [], chat_found


def retrieveImage(image_document):
    try:
        client_id = image_document['client_id']
        image_data = image_document['imageData']
        image_array = np.frombuffer(image_data, np.uint8)
        db_image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        return client_id, db_image

    except Exception as e:
        logger.error(f"Error loading image: {str(e)}")
        return None, None
    

