from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select
from app.models import Match, MatchCreate, MatchPublic, MatchUpdatePlayers, MatchUpdateSettings
from app.dependencies import SessionDep

router = APIRouter()

# GET Methods
    #GET Match method
@router.get("/matches/{match_id}", response_model=MatchPublic)
def get_match(session: SessionDep, match_id: int):
    return session.get(Match, match_id)