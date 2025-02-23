from fastapi import FastAPI
from src.core.config import settings
from src.api.routes import health, audio, chat

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

# Include routers
app.include_router(health.router)
app.include_router(audio.router, prefix="/audio", tags=["audio"])
# app.include_router(chat.router, prefix="/chat", tags=["chat"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)