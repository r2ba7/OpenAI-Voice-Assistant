from image_processing import cap_image
from etl import database_methods
import cv2
import bson

if __name__ == '__main__':
    # python -m main
    # client_image = cap_image.capture_and_save_image()
    # client_id = database.create_client()
    # database.save_image(client_image, client_id)
    try:
        # Retrieve the image using the provided ObjectID
        image = database_methods.retrieve_image(bson.ObjectId('6595a616061f3c0d0b4ddc9a'))

        if image is not None:
            # Display the image
            cv2.imshow("Client Image", image)

            # Wait for the 'E' key to be pressed
            while True:
                if cv2.waitKey(1) & 0xFF == ord('e'):
                    break

            # Destroy all OpenCV windows
            cv2.destroyAllWindows()

        else:
            print("No image found or error retrieving the image.")

    except Exception as e:
        print(f"Error occurred: {e}")

    # End of the program
    print("Program ended.")