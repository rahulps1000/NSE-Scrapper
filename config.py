from os import environ

from dotenv import load_dotenv

load_dotenv()

class Config:
    DB_URI = environ.get("DB_URI")