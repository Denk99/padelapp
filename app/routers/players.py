from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select
from datetime import timezone, datetime
from app.models import Player, PlayerCreate, PlayerUpdate, PlayerPublic
from app.dependencies import SessionDep
from app.security import CurrentPlayer
import app.security as sec

router = APIRouter()

#GET Methods
    # GET Player
@router.get("/players/{player_id}",response_model=PlayerPublic)
def get_player(current_player: CurrentPlayer, session: SessionDep, player_id: int):
    player = session.get(Player, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

    # GET Player list
@router.get("/players/", response_model=list[PlayerPublic]) 
def get_player_list(current_player: CurrentPlayer, session: SessionDep, offset: int = 0, limit: int = Query(default=100, le=100)) -> list[Player]:
    players = list(session.exec(select(Player).offset(offset).limit(limit)).all())
    if not players:
        raise HTTPException(status_code=404, detail="No players in Database")
    return players

    #GET Player Profile
@router.get("/players/profile/")
def get_player_profile(current_player: CurrentPlayer):
    return current_player

    #GET Player token
@router.get("/players/profile/token/")
def verify_player_token(current_player: CurrentPlayer):
    return {
        "valid": True,
        "player": {
            "id": current_player.id,
            "nombre": current_player.nombre,
            "email": current_player.email,
            "rol": current_player.rol,
            "nivel": current_player.nivel,
            "ciudad": current_player.ciudad,
        }
    }

# POST Methods
    #POST Player (No auth required)
@router.post("/players/")
def post_player(player: PlayerCreate, session: SessionDep) -> Player:
    email_registered = session.exec(select(Player).where(Player.email == player.email)).first()
    if email_registered:
        raise HTTPException(400, detail="Email already registered.")
    
    hashed_password = sec.get_password_hash(player.password)

    db_player = Player(
        nombre=player.nombre,
        email=player.email,
        password=hashed_password,
        nivel=player.nivel,
        ciudad=player.ciudad,
        rol=player.rol or "jugador",
        creado_en= datetime.now(timezone.utc)
    )
    try:
        session.add(db_player)
        session.commit()
        session.refresh(db_player)
    except:
         session.rollback()
         raise HTTPException(status_code=400, detail="Unable to complete transaction.")   
    return db_player

# UPDATE methods
     # UPDATE Player
@router.patch("/players/{player_id}")
def update_player(current_player: CurrentPlayer, player_id: int, player: PlayerUpdate, session: SessionDep):
    player_db = session.get(Player, player_id)
    if not player_db:
        raise HTTPException(status_code=404, detail="Hero not found")
    player_data = player.model_dump(exclude_unset=True)
    player_db.sqlmodel_update(player_data)
    session.add(player_db)
    session.commit()
    session.refresh(player_db)
    return player_db

# DELETE methods
    # DELETE Player
@router.delete("/players/{player_id}")
def delete_player(current_player: CurrentPlayer, player_id: int, session: SessionDep):
    player = session.get(Player, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    session.delete(player)
    session.commit()
    return {"ok": True}