from fastapi import FastAPI
import uvicorn
import src.database.db

app = FastAPI()

@app.get("/")
def index():
    return { "msg": "index" }

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)
