import re, os, requests, json, openai, time
import pandas as pd, numpy as np, warnings
from etl.authentications import *

def create_files(assistant_id, files_path=None, file_object=False):
    uploaded_files = []

    if files_path:
        
        for f in os.listdir(files_path):
            file = client.files.create(file=open(f"{files_path}/{f}", "rb"),purpose="assistants")
            uploaded_files.append(file)
    
    elif file_object:
        uploaded_files = client.files.list()

    ids = []
    for f in uploaded_files:
        ids.append(f.id)

    client.beta.assistants.update(
            assistant_id,
            file_ids=ids,
    )

def delete_files(assistant_id, files_ids):
    for f_id in files_ids:
        client.files.delete(f_id)
    
    time.sleep(0.5)
    create_files(assistant_id, files_path=None, file_object=True)
    