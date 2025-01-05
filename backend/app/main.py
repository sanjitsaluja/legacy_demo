from fastapi import FastAPI

from app.api.endpoints import mental_health_conversation

app = FastAPI(title="Mental Health API")

app.include_router(
    mental_health_conversation.router,
    prefix="/api/v1",
    tags=["conversations"],
)


@app.get("/")
def read_root():
    return {"message": "Welcome to Mental Health API"}
