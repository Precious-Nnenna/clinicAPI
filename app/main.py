from fastapi import FastAPI

from app.auth.auth_router import router as auth_router

import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI()

app.include_router(auth_router)


@app.get("/")
def get_home():
    return{"message": "hii"}

