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
    # username único
    # email único
    return UserRead(
        id=1,
        **user.model_dump(),
    )


@app.get('/users/', status_code=HTTPStatus.OK, response_model=UserList)
def read_users():
    existing_users = [
        {
            'id': 1,
            'username': 'test',
            'email': 'test@example.com',
            'password': 'test123',
        },
        {
            'id': 2,
            'username': 'test2',
            'email': 'test2@example.com',
            'password': 'test2123',
        },
    ]
    return UserList(users=existing_users)


@app.get(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserRead
)
def read_user(user_id: int):
    # existir no db
    existing_user = {
        'id': user_id,
        'username': 'test',
        'email': 'test@example.com',
        'password': 'test123',
    }
    return UserRead(**existing_user)


@app.patch(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserRead,
)
def update_user(user_id: int, user: UserUpdate):
    # existir no db
    # username único
    # email único
    existing_user = {
        'id': user_id,
        'username': 'test',
        'email': 'test@example.com',
        'password': 'test123',
    }
    changes = user.model_dump()
    existing_user.update(changes)
    return UserRead(**existing_user)


@app.put(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserRead
)
def replace_user(user_id: int, user: UserReplace):
    # existir no db
    # username único
    # email único
    return UserRead(id=user_id, **user.model_dump())


@app.delete('/users/{user_id}', status_code=HTTPStatus.NO_CONTENT)
def delete_user(user_id: int):
    # existir no db
    pass
