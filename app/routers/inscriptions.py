from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select, Session
from app.models import Inscription, InscriptionStatus, MatchStatus
from app.dependencies import get_session
from app.security import CurrentPlayer


router = APIRouter()

# GET Methods
    # GET Unread notifications
@router.get("/inscriptions/", response_model=list[Inscription])
def get_inscription(current_player: CurrentPlayer, session: Session = Depends(get_session)):
    inscriptions = session.exec(
        select(Inscription)
        .where(Inscription.usuario_id == current_player.id)
        .where(Inscription.estado == InscriptionStatus.confirmado)
    )
    if not inscriptions or inscriptions == []:
        raise HTTPException(status_code=404, detail="No inscriptions available")
    return inscriptions

    #GET All inscriptions
@router.get("/inscriptions/all", response_model=list[Inscription])
def get_all_inscription(current_player: CurrentPlayer, session: Session = Depends(get_session)):
    inscriptions = session.exec(
        select(Inscription)
    )
    if not inscriptions or inscriptions == []:
        raise HTTPException(status_code=404, detail="No inscriptions available")
    return inscriptions
