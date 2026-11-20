from fastapi import FastAPI

from multi_agent_chat.routes import (
    agents,
    auth,
    conversations,
    messages,
    users,
)

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(agents.router)
app.include_router(conversations.router)

app.include_router(messages.router)
