from fastapi import FastAPI, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import Field, Session, SQLModel, create_engine, select, Relationship
from typing import Annotated
from contextlib import asynccontextmanager

# Database Dev variables
sql_file = "padelapp.db"
sql_url = f"sqlite:///{sql_file}"

connect_args = {"check_same_thread": False}
engine = create_engine(sql_url, connect_args=connect_args)

# Classes
    # Player classes
class PlayerBase(SQLModel):
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)
    is_male: bool

class Player(PlayerBase, table = True):
    id: int | None = Field(default=None, primary_key=True)

class PlayerPublic(PlayerBase):
    id: int  

class PlayerCreate(PlayerBase):
    name: str
    age: int | None = Field(default=None, index=True) 
    is_male: bool  

class PlayerUpdate(PlayerBase):
    name: str | None = None

    # Match - Player intermediate table
"""class MatchPlayerLink(SQLModel, table=True):
    match_id: int | None = Field(default=None, foreign_key="match.id", primary_key=True)
    player_id: int | None = Field(default=None, foreign_key="player.id", primary_key=True)"""

    # Match class
"""class Match(SQLModel, table = True):
    id: int
    is_1v1: bool
    host: Player | None = Relationship()
    players: list[Player] = Relationship(link_model=MatchPlayerLink)
    winner: Player | None = Relationship()"""

# DB creation and session
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

# Operations
    # ON EVENT methods (Lifecycle)
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("App iniciada")
    create_db_and_tables()
    yield
    print("App cerrada")

    # Inicialización
app = FastAPI(lifespan=lifespan)

    # GET methods
        # GET Root
@app.get("/")
def read_root():
    return {"Hello": "World"}

        # GET Player
@app.get("/players/{player_id}")
def get_player(player_id: int):
    return {"player_id": player_id}

        # GET Player list
@app.get("/players/", response_model=list[PlayerPublic]) 
def get_player_list(session: Session = Depends(get_session), offset: int = 0, limit: int = Query(default=100, le=100)) -> list[PlayerPublic]:
    players = list(session.exec(select(PlayerPublic).offset(offset).limit(limit)).all())
    return players


    # POST methods
        #POST Player
@app.post("/players/")
def post_player(player: PlayerCreate, session: SessionDep) -> Player:
    db_player = Player.model_validate(player)
    session.add(db_player)
    session.commit()
    session.refresh(db_player)
    return db_player

    # UPDATE methods
        # UPDATE Player
@app.patch("/players/{player_id}")
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
@app.delete("/players/{player_id}")
def delete_player(player_id: int, session: SessionDep):
    player = session.get(Player, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    session.delete(player)
    session.commit()
    return {"ok": True}
