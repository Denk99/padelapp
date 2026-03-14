from fastapi.security import OAuth2PasswordBearer
import jwt
from fastapi import HTTPException, status, Depends
from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone
from typing import Optional, Annotated
from app.models import TokenData, Player
from app.dependencies import SessionDep
from sqlmodel import select


# Security Config
ALGORITHM = "HS256"
TOKEN_EXPIRATION_TIME = 30
SECRET_KEY = "mypass123"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated ="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Auth Dependencies
def get_current_user(session: SessionDep, token: str = Depends(oauth2_scheme)):
    token_data = verify_token(token)
    player = session.exec(select(Player).where(Player.email == token_data.email)).first()
    if player is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User does not exist.", headers={"WWW-Authenticate": "Bearer"})
    return player

def get_current_active_user(current_user: Player = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return current_user

# Password dependencies

def verify_password(plain_text_pwd: str, hashed_pwd: str) -> bool:
    return pwd_context.verify(plain_text_pwd, hashed_pwd)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

#Token dependencies

def create_access_token(data: dict, expires_delta: Optional[timedelta]=None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRATION_TIME)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unable to verify credentials.", headers={"WWW-Authenticate": "Bearer"})
        return TokenData(email=email)
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unable to verify credentials.", headers={"WWW-Authenticate": "Bearer"})

# Dependencies for simplification
CurrentPlayer = Annotated[Player, Depends(get_current_user)]
ActivePlayer = Annotated[Player, Depends(get_current_active_user)]