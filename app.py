import uvicorn
from main.services.endpoints import create_app
from main.config import settings

app = create_app()

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8004, reload=True)
