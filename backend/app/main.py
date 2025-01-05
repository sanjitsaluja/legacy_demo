from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import mental_health_conversation

app = FastAPI(title="Mental Health API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "https://your-domain.com",  # Production domain
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(
    mental_health_conversation.router,
    prefix="/api/v1",
    tags=["conversations"],
)


@app.get("/")
def read_root():
    return {"message": "Welcome to Mental Health API"}
