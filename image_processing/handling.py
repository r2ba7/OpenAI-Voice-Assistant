import time

import cv2
import face_recognition

from etl import database_methods
from etl.authentications import *
from utils import general_utils


logger = general_utils.get_logger(__name__)


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

    capture_image = False  # Flag to track if "E" key is pressed
    image = None  # Variable to store the captured image
    while True:
        try:
            ret, frame = cap.read()
            if not ret:
                logger.info("Error: Could not capture an image.")
                break

            cv2.imshow("Camera Feed", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == 101:
                logger.info(f"Image is taken")
                capture_image = True 
                image = frame

            if capture_image:
                break

            cap.release()
            cv2.destroyAllWindows()
            return image
        
        except Exception as e:
            logger.error(f"Error loading image: {str(e)}")
            return None


def compare_images(client_image, db_image):
    """
    Compares two images for facial similarity.

    Parameters:
    - client_image (numpy.ndarray): The client's image.
    - db_image (numpy.ndarray): An image from the database.

    Returns:
    - (bool, int): A tuple where the first element indicates if images are the same (True/False),
                   and the second element is the accuracy percentage of the match (0 if not the same).
    """
    def find_face_encodings(image):
        """
        Finds face encodings in a given image.

        Parameters:
        - image (numpy.ndarray): The image to find face encodings in.

        Returns:
        - encodings (list): The first face encoding found in the image, or None if no faces are detected.
        """   
        face_encodings = face_recognition.face_encodings(image)
        return face_encodings[0] if face_encodings else None
    
    if client_image is None or db_image is None:
        logger.warning("One or both images are None or invalid.")
        return False, 0
    
    client_encodings = find_face_encodings(client_image)
    db_image_encodings = find_face_encodings(db_image)

    if client_encodings is not None and db_image_encodings is not None:
        is_same = face_recognition.compare_faces([client_encodings], db_image_encodings)[0]
        
        if is_same:
            distance = face_recognition.face_distance([client_encodings], db_image_encodings)[0]
            accuracy = 100 - round(distance * 100)
            logger.info("The images are the same")
            logger.info(f"Accuracy Level: {accuracy}%")
            return is_same, accuracy
        
        else:
            logger.warning("The images are not the same")
            return is_same, 0
    
    else:
        return False, 0

def getClient(client_image, accuracy_threshold):
    """
    Identifies the client from a given image based on facial recognition.

    Parameters:
    - client_image (numpy.ndarray): The client's image.
    - accuracy_threshold (int): The minimum accuracy required to consider a match valid.

    Returns:
    - client_id (str or None): The ID of the matched client if found; otherwise, None.
    """
    best_match = {'client_id': None, 'accuracy': 0}

    for image_document in db.images.find():
        client_id, db_image = database_methods.retrieveImage(image_document)
        is_same, accuracy = compare_images(client_image, db_image)

        if is_same and accuracy > best_match['accuracy']:
            best_match['client_id'] = client_id
            best_match['accuracy'] = accuracy

    if best_match['accuracy'] >= accuracy_threshold:
        logger.info(f"Matched client: {client_id}, accuracy: {best_match['accuracy']}%.")
        return best_match['client_id']
    
    else:
        logger.warning(f"No matching client found with accuracy above {accuracy_threshold}%.")
        return None


def clientRecognizition(accuracy_threshold=50):
    """
    Processes client recognition based on a captured image.

    Parameters:
    - accuracy_threshold (int, optional): Threshold for accuracy in image recognition, default is 50.

    Returns:
    - (bool, tuple): Returns a tuple where the first element is a boolean indicating if an existing client was recognized.
                     The second element is a tuple containing the client_id. If an existing client is recognized, it also includes chat history.
    """
    client_image = captureImage()
    time.sleep(5)
    client_id = getClient(client_image=client_image, accuracy_threshold=accuracy_threshold)
    time.sleep(5)
    client_found = False

    if client_id:
        chat_history, chat_found = database_methods.retrieveHistory(client_id)
        client_found = True
        time.sleep(5)
        return client_found, (client_id, chat_history, chat_found)
    
    else:
        client_id = database_methods.createClient()
        chat_found = False
        database_methods.createImage(client_image, client_id)
        time.sleep(5)
        return client_found, (client_id, chat_found)


