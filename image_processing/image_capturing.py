import queue
import threading
import time

import cv2

from text_processing import text2speech, text_generation, speech2text
from utils import general_utils

logger = general_utils.get_logger(__name__)

def get_speech_prompt(q, image_prompts):
    try:
        prompt, _ = speech2text.getPrompt(language="en")
        if any(command.lower() in prompt.strip().lower() for command in image_prompts):
            q.put(True)
            
    except Exception as e:
        logger.error(f"Error in speech prompt thread: {str(e)}")



def captureImage():
    """
    Captures an image using the default camera.

    Returns:
    - image (numpy.ndarray): Captured image if successful; None if an error occurs or if 'E' key is pressed.
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.info("Error: Could not open the camera.")
        return None

    image = None
    text2speech.convert2speech("Say: cheese, capture, photo, picture to take picture.")
    image_prompts = ['cheese', 'capture', 'photo', 'picture']
    time.sleep(1)
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.info("Error: Could not capture an image.")
                break
            
            prompt, _ = speech2text.getPrompt(language="en")
            if any(command.lower() in prompt.strip().lower() for command in image_prompts):
                image = frame
                break

    except Exception as e:
        logger.error(f"Error taking image: {str(e)}")
        
    finally:
        cap.release()
        cv2.destroyAllWindows()

    return image