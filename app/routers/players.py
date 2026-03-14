from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select
from app.models import Player, PlayerCreate, PlayerUpdate, PlayerPublic
from app.dependencies import SessionDep
import app.auth as aa

router = APIRouter()

#GET Methods
    # GET Player
@router.get("/players/{player_id}", response_model=PlayerPublic)
def get_player(session: SessionDep, player_id: int):
    player = session.get(Player, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

    # GET Player list
@router.get("/players/", response_model=list[PlayerPublic]) 
def get_player_list(session: SessionDep, offset: int = 0, limit: int = Query(default=100, le=100)) -> list[Player]:
    players = list(session.exec(select(Player).offset(offset).limit(limit)).all())
    if not players:
        raise HTTPException(status_code=404, detail="No players in Database")
    return players


# POST Methods
    #POST Player
@router.post("/players/")
def post_player(player: PlayerCreate, session: SessionDep) -> Player:
    username_taken = session.exec(select(Player).where(Player.username == player.username)).first()
    email_registered = session.exec(select(Player).where(Player.email == player.email)).first()
    if username_taken:
        raise HTTPException(400, detail="Username already taken.")
    if email_registered:
        raise HTTPException(400, detail="Email already registered.")
    player.password = aa.get_pwd_hash(player.password)
    db_player = Player.model_validate(player)
    session.add(db_player)
    session.commit()
    session.refresh(db_player)
    return db_player

# UPDATE methods
     # UPDATE Player
@router.patch("/players/{player_id}")
def update_player(player_id: int, player: PlayerUpdate, session: SessionDep):
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
def delete_player(player_id: int, session: SessionDep):
    player = session.get(Player, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    session.delete(player)
    session.commit()
    return {"ok": True}