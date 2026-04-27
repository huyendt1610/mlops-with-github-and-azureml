import os 

class Config: 
    # JWT 
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', '')
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRE_MINUTES = 30
