from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from controller.main_router import main_router

load_dotenv()

app = FastAPI()
app.include_router(main_router)
app.mount("/static", StaticFiles(directory="static"), name="static")
