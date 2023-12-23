import cv2, pymongo, io, numpy as np
from gridfs import GridFS
from etl.authentications import db


def save_image_in_db(image):

    try:

        fs = GridFS(db, collection='clients')
        image_bytes = cv2.imencode('.jpg', image)[1].tobytes()

        # Save the image to MongoDB GridFS
        fs.put(io.BytesIO(image_bytes), filename="client_image.jpg")

        print("Image saved in MongoDB GridFS.")
        return True

    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def retrieve_image_from_db(client_image):
    try:
        fs = GridFS(db, collection='clients')

        # Find the image by filename (you can change the filename as needed)
        image_file = fs.find_one({"filename": client_image})

        if image_file:
            # Read the image data from GridFS and convert it to a numpy array
            image_data = image_file.read()
            image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)

            print("Image retrieved from MongoDB GridFS.")
            return image
        else:
            print("Image not found in MongoDB GridFS.")
            return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None