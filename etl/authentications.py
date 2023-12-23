from pymongo import MongoClient
from dotenv import load_dotenv
from openai import OpenAI
import os, openai

load_dotenv()
dbconnection = os.environ.get("dbconnection")
dbname = os.environ.get("dbname")
openai.api_key = os.environ.get("openai_api_key")
ASSISTANT_ID = os.environ.get("openai_assistant_id")
client = OpenAI()

def connect_to_database(connection_string: str=dbconnection, 
                        db_name: str=dbname):
    """
    Get a collection from a MongoDB database.

    Parameters:
        connection_string (str): The MongoDB connection string.
        db_name (str): The name of the database.
    Returns:
        pymongo.database.Database: returns the database object.
    """
    client = MongoClient(connection_string)
    db = client[db_name]
    return db

db = connect_to_database()


