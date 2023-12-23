import cv2

def capture_and_save_image():
    # Open the default camera (usually the built-in webcam, camera index 0)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open the camera.")
        return None

    capture_image = False  # Flag to track if "E" key is pressed
    image = None  # Variable to store the captured image

    while True:
        # Capture a single frame
        ret, frame = cap.read()

        if not ret:
            print("Error: Could not capture an image.")
            break

        # Display the live camera feed
        cv2.imshow("Camera Feed", frame)

        # Check for key press events
        key = cv2.waitKey(1) & 0xFF

        # Check if the "E" key is pressed (key code 101 for lowercase 'e')
        if key == 101:
            capture_image = True  # Set the flag to capture the image
            image = frame

        # Check if the flag is set and break out of the loop
        if capture_image:
            break

    # Release the camera and close the OpenCV window
    cap.release()
    cv2.destroyAllWindows()

    return image
