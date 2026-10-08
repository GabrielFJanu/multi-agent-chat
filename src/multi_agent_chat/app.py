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


@app.get('/users/', status_code=HTTPStatus.OK, response_model=list[UserRead])
def read_users():
    return [
        UserRead(
            id=1,
            username='test',
            email='test@example.com',
        ),
        UserRead(
            id=2,
            username='test2',
            email='test2@example.com',
        ),
    ]
