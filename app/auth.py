from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from fastapi import HTTPException, status, Depends
from passlib.context import CryptContext
from datetime import date, timedelta, datetime
from typing import Optional
from app.models import TokenData, Player
from app.dependencies import SessionDep
from sqlmodel import select
import database
import time


# Security Config
ALGORITHM = "HS256"
TOKEN_EXPIRATION_TIME = 30
SECRET_KEY = "mypass123"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated ="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


#AUTH DEPENDENCIES
def get_current_user(token: str = Depends(oauth2_scheme), session: SessionDep = Depends(database.get_session)):
    token_data = verify_token(token)
    player = session.exec(select(Player).where(Player.email == token_data.email)).first()
    if player is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User does not exist.", headers={"WWW-Authenticate": "Bearer"})
    return player

def get_current_active_user(current_user: Player = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inactive user")

def verify_password(plain_text_pwd: str, hashed_pwd: str) -> bool:
    return pwd_context.verify(plain_text_pwd, hashed_pwd)

def get_pwd_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta]=None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow()
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    enconded_jwt = jwt.encode(to_encode, SECRET_KEY,algorithm=ALGORITHM)
    return enconded_jwt


def verify_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unable to verify credentials.", headers={"WWW-Authenticate": "Bearer"})
        return TokenData(email=email)
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unable to verify credentials.", headers={"WWW-Authenticate": "Bearer"})


