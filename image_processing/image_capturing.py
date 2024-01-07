import queue
import threading
import time

import cv2

from text_processing import text2speech, text_generation, speech2text
from utils import general_utils

logger = general_utils.get_logger(__name__)

def get_speech_prompt(q, image_prompts, stop_signal):
    while not stop_signal.is_set():
        try:
            prompt, _ = speech2text.getPrompt(language="en")
            if prompt and any(command.lower() in prompt.strip().lower() for command in image_prompts):
                q.put(True)
                break
        except Exception as e:
            logger.error(f"Error in speech prompt thread: {str(e)}")

def captureImage():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.info("Error: Could not open the camera.")
        return None

    q = queue.Queue()
    stop_signal = threading.Event()
    image_prompts = ['cheese', 'capture', 'photo', 'picture']
    speech_thread = threading.Thread(target=get_speech_prompt, args=(q, image_prompts, stop_signal))
    speech_thread.start()

    image = None
    text2speech.convert2speech("Say: cheese, capture, photo, picture to take picture.")
    time.sleep(1)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.info("Error: Could not capture an image.")
                break

            cv2.imshow("Camera Feed", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):  # Exit condition
                break

            if not q.empty():
                image = frame
                break
    except Exception as e:
        logger.error(f"Error taking image: {str(e)}")
    finally:
        stop_signal.set()  # Signal to stop the speech thread
        cap.release()
        cv2.destroyAllWindows()
        speech_thread.join()

    return image
