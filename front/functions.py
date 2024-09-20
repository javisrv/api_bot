import os
from requests import post
from typing import Generator
from dotenv import load_dotenv

load_dotenv()
FASTAPI_PASSWORD = os.getenv('FASTAPI_PASSWORD')
FASTAPI_URL = os.getenv('FASTAPI_URL')

url = FASTAPI_URL

payload = {
    "session_id": "",
    "input": ""
}

headers = {
    'accept': 'application/json',
    'X-API-Key': FASTAPI_PASSWORD,
    'Content-Type': 'application/json'
    }


def write_stream(text: str) -> Generator:
    for s in text:
        yield s


def get_response(prompt: str, conversation_id) -> dict:
    payload["input"] = prompt
    payload["session_id"] = conversation_id
    response = post(url, json=payload, headers=headers).json()
    return response
