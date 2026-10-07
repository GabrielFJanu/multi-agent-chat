from http import HTTPStatus

from fastapi import FastAPI

from src.multi_agent_chat.schemas import Message

app = FastAPI()


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return Message(message='Hello, world!')
