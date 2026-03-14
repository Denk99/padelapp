from fastapi import APIRouter, HTTPException, Depends
from app.models import Player
from auth import Token
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from dependencies import SessionDep
from sqlmodel import select

router = APIRouter()

@router.post("/token/", response_model=Token)
def login_for_access_token(session: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()):
    player = session.exec(select(Player).where(Player.email == form_data.username)).first()