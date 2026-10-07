from http import HTTPStatus

from fastapi import FastAPI

from multi_agent_chat.schemas import UserCreate, UserRead

app = FastAPI()


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserRead)
def create_user(user: UserCreate):
    return UserRead(
        id=1,
        username=user.username,
        email=user.email,
    )
