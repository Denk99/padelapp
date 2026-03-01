from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select
from app.models import Match, MatchCreate, MatchPublic, MatchUpdatePlayers, MatchUpdateSettings
from app.dependencies import SessionDep

router = APIRouter()

# GET Methods
    # GET Match method
@router.get("/matches/{match_id}", response_model=MatchPublic)
def get_match(session: SessionDep, match_id: int):
    return session.get(Match, match_id)

    # GET Matches list
@router.get("/matches/", response_model=list[MatchPublic])
def get_match_list(session: SessionDep, offset: int = 0, limit: int = Query(default=100, le=100)) -> list[Match]:
    matches = list(session.exec(select(Match).offset(offset).limit(limit)).all())
    if not matches:
        raise HTTPException(status_code=404, detail="No matches in Database")
    return matches

# POST Methods
@router.post("/matches/")
def post_match(match: MatchCreate, session: SessionDep):
    db_match = Match.model_validate(match)
    session.add(db_match)
    session.commit()
    session.refresh(db_match)
    return db_match