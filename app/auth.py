import os 
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from config import Config


oauth2_schema = OAuth2PasswordBearer(tokenUrl="token")

def create_token(data: dict) -> str: 
    payload = data.copy() 
    payload['exp'] = datetime.now(timezone.utc) + timedelta(minutes=Config.JWT_EXPIRE_MINUTES)
    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM)

def verify_token(token: str = Depends(oauth2_schema)): 
    try: 
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])
        return payload
    except Exception: 
        raise HTTPException(status_code=401, detail="Invalid token") 