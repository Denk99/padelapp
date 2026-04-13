from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import select, Session
from app.models import Match, MatchCreate, MatchPublic, MatchUpdate
from app.dependencies import get_session
from app.security import CurrentPlayer

router = APIRouter()

# GET Methods
    # GET Match
@router.get("/matches/{match_id}", response_model=MatchPublic)
def get_match(match_id: int, current_player: CurrentPlayer, session: Session = Depends(get_session)):
    match = session.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match

    # GET Match list
@router.get("/matches/", response_model=list[MatchPublic])
def get_match_list(current_player: CurrentPlayer, offset: int = 0, limit: int = Query(default=100, le=100), session: Session = Depends(get_session)):
    matches = session.exec(select(Match).offset(offset).limit(limit)).all()
    if not matches:
        raise HTTPException(status_code=404, detail="No matches in database")
    return matches

# POST Methods

@router.post("/matches/", response_model=MatchPublic)
def post_match(
    match: MatchCreate,
    current_player: CurrentPlayer,
    session: Session = Depends(get_session),
):
    db_match = Match.from_orm(match)
    session.add(db_match)
    session.commit()
    session.refresh(db_match)
    return db_match

# PATCH Methods

@router.patch("/matches/{match_id}", response_model=MatchPublic)
def update_match_settings(match_id: int, match_update: MatchUpdate, current_player: CurrentPlayer, session: Session = Depends(get_session),):
    db_match = session.get(Match, match_id)
    if not db_match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    update_data = match_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_match, key, value)
    
    session.add(db_match)
    session.commit()
    session.refresh(db_match)
    return db_match

# DELETE Methods

@router.delete("/matches/{match_id}")
def delete_match(
    match_id: int,
    current_player: CurrentPlayer,
    session: Session = Depends(get_session),
):
    db_match = session.get(Match, match_id)
    if not db_match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    session.delete(db_match)
    session.commit()
    return {"ok": True}