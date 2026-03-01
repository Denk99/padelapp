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
    # POST Match method
@router.post("/matches/")
def post_match(match: MatchCreate, session: SessionDep):
    db_match = Match.model_validate(match)
    session.add(db_match)
    session.commit()
    session.refresh(db_match)
    return db_match

# UPDATE Methods
    # UPDATE Match method
@router.patch("/matches/{match_id}")
def update_match_settings(match_id: int, match: MatchUpdateSettings, session: SessionDep):
    match_db = session.get(Match, match_id)
    if not match_db:
        raise HTTPException(status_code=404, detail="Hero not found")
    match_data = match.model_dump(exclude_unset=True)
    match_db.sqlmodel_update(match_data)
    session.add(match_db)
    session.commit()
    session.refresh(match_db)
    return match_db

# DELETE Methods
    # DELETE Match method
@router.delete("/matches/{match_id}")
def delete_match(match_id: int, session: SessionDep):
    db_match = session.get(Match, match_id)
    session.delete(db_match)
    session.commit()
    return {"ok": True}
