import os
from dotenv import load_dotenv

import openai
from pymongo import MongoClient
from openai import OpenAI, AsyncOpenAI
from tavily import TavilyClient

load_dotenv()

dbconnection = os.environ.get("dbconnection")
dbname = os.environ.get("dbname")

OPENAI_API_KEY = os.environ.get("openai_api_key")
ASSISTANT_ID = os.environ.get("openai_assistant_id")

TAVILY_API_KEY = os.environ.get("tavily_api_key")


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

sync_client = OpenAI(api_key=OPENAI_API_KEY)
async_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
db = connect_to_database()


