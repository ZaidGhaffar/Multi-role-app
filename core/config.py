from dotenv import load_dotenv
import os

load_dotenv()



class Settings:
    def __init__(self):
        self.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
        self.ALGORITHM = os.getenv("ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
        self.DATABASE_URL = os.getenv("DATABASE_URL")

settings = Settings()

