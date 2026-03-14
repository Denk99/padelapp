from fastapi import APIRouter, HTTPException, Depends
from app.models import Player, Token
import app.security as aa
from fastapi.security import OAuth2PasswordRequestForm
from app.dependencies import SessionDep
from sqlmodel import select
from datetime import timedelta

router = APIRouter()

TOKEN_EXPIRATION_TIME = 30

# Login endpoint to obtain a session token
@router.post("/auth/token", response_model=Token)
def login_for_access_token(session: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()):
    player = session.exec(select(Player).where(Player.email == form_data.username)).first()
    if not player:
        player = session.exec(select(Player).where(Player.username == form_data.username)).first()
    if not player or not aa.verify_password(form_data.password, player.hashed_password):
        raise HTTPException(status_code=401, detail="Wrong user/password")
    if not player.is_active:
        raise HTTPException(status_code=403, detail="Inactive player")
    access_token_expires = timedelta(minutes=TOKEN_EXPIRATION_TIME)
    access_token = aa.create_access_token(data={"sub": player.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}