import cv2
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

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.info("Error: Could not capture an image.")
                break

            cv2.imshow("Camera Feed", frame)
            key = cv2.waitKey(1) & 0xFF

            if key == 101:  # 'e' key
                logger.info("Image is taken")
                capture_image = True 
                image = frame
                break

    except Exception as e:
        logger.error(f"Error taking image: {str(e)}")
    finally:
        # Release the camera and close the window regardless of how the loop exits
        cap.release()
        cv2.destroyAllWindows()

    return image