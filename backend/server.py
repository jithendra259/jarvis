# Backward-compatible redirect to main.py
import uvicorn
from main import app
from config.settings import settings

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.JARVIS_HOST, port=settings.JARVIS_PORT, reload=True)
