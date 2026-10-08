from http import HTTPStatus

from fastapi import FastAPI

from multi_agent_chat.schemas import (
    UserCreate,
    UserList,
    UserRead,
    UserReplace,
    UserUpdate,
)

app = FastAPI()


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserRead)
def create_user(user: UserCreate):
    return UserRead(
        id=1,
        **user.model_dump(),
    )


@app.get('/users/', status_code=HTTPStatus.OK, response_model=UserList)
def read_users():
    existing_users = [
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
    return UserList(users=existing_users)


@app.patch('/users/', status_code=HTTPStatus.OK, response_model=UserRead)
def update_user(user: UserUpdate):
    existing_user = {
        'id': 1,
        'username': 'test',
        'email': 'test@example.com',
        'password': 'test123',
    }
    existing_user.update(**user.model_dump(exclude_unset=True))
    return UserRead(**existing_user)


@app.put('/users/', status_code=HTTPStatus.OK, response_model=UserRead)
def replace_user(user: UserReplace):
    existing_user = {
        'id': 1,
        'username': 'test',
        'email': 'test@example.com',
        'password': 'test123',
    }
    return UserRead(id=existing_user['id'], **user.model_dump())
