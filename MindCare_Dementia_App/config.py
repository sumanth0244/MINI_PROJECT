import os
from dotenv import load_dotenv
load_dotenv()
class Config:
    SECRET_KEY=os.getenv("FLASK_SECRET_KEY","dev-secret-change-me")
    DB=dict(host=os.getenv("DB_HOST","localhost"), user=os.getenv("DB_USER","root"), password=os.getenv("DB_PASSWORD",""), database=os.getenv("DB_NAME","mindcare_db"))
