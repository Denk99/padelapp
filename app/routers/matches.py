from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import select, Session
from app.models import Match, MatchCreate, MatchPublic, MatchUpdate, MatchStatus, Inscription, InscriptionStatus
from app.dependencies import get_session
from app.security import CurrentPlayer
from datetime import datetime, timezone

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

    # GET Available Matches
@router.get("/matches/available/", response_model=list[MatchPublic])
def get_available_matches(current_player: CurrentPlayer, offset: int = 0, limit: int = Query(default=30, le=30), session: Session = Depends(get_session)):
    # SELECT Query only for available matches
    matches = session.exec(select(Match).where(Match.estado == MatchStatus.abierto).offset(offset).limit(limit)).all()
    if not matches:
        raise HTTPException(status_code=404, detail="No matches available")
    return matches

# PLAYER JOIN Method
@router.post("/matches/{match_id}/inscripciones/", status_code=201)
def join_match(match_id: int, current_player: CurrentPlayer, session: Session = Depends(get_session)):
    # Check existing match
    match_db = session.get(Match, match_id)
    if not match_db:
        raise HTTPException(status_code=404, detail="Unable to find match")
    # Check if Player already present in Match participants
    existing_inscription = session.exec(select(Inscription)
                                        .where(Inscription.partido_id == match_id)
                                        .where(Inscription.usuario_id == current_player.id)).first()
    if existing_inscription:
        raise HTTPException(status_code=400, detail="Player already in match")
    # Check if there are available Inscriptions
    inscripciones = session.exec(
    select(Inscription).where(Inscription.partido_id == match_id)).all()
    if len(inscripciones) >= (match_db.plazas_totales or 0):
        raise HTTPException(status_code=400, detail="Match is full")

    # Check if MatchStatus is "Open"
    if match_db.estado != MatchStatus.abierto:
        raise HTTPException(status_code=400, detail="Unable to join: Match status is " + str(match_db.estado))
    # Create Inscription
    inscription = Inscription(
        partido_id=match_id,
        usuario_id=current_player.id, # type: ignore
        estado=InscriptionStatus.confirmado,
        inscrito_en=datetime.now(timezone.utc)
    )
    session.add(inscription)
    if match_db.plazas_totales:
        plazas_disponibles = match_db.plazas_totales - (len(inscripciones) + 1)
        if plazas_disponibles <= 0:
            match_db.estado = MatchStatus.completo
            session.add(match_db)
    session.commit()
    return {"message": "OK", "match_id": match_id, "plazas_restantes": str(plazas_disponibles)}


# POST Methods

@router.post("/matches/", response_model=MatchPublic)
def post_match(match: MatchCreate, current_player: CurrentPlayer, session: Session = Depends(get_session)):
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