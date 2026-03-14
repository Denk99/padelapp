from sqlmodel import Field, Session, SQLModel, create_engine, select, Relationship
from datetime import date
from pydantic import EmailStr, BaseModel
from typing import Optional

# Classes
    # Player classes
class PlayerBase(SQLModel):
    username: str  = Field(index=True, unique=True)
    full_name: str
    email: str  = Field(index=True, unique=True)
    birth_date: date | None = None
    is_male: bool
    city: str

class Player(PlayerBase, table = True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    is_active: bool = Field(default=True)

class PlayerPublic(PlayerBase):
    id: int
    username: str
    city: str
    is_male: bool
    is_active: bool = True

class PlayerCreate(PlayerBase):
    username: str
    full_name: str
    email: EmailStr
    birth_date: date | None = Field(default=None)
    city: str
    is_male: bool
    password: str

class PlayerUpdate(PlayerBase):
    username: str | None = None
    full_name: str | None = None
    surname: str | None = None
    email: str | None = None
    birth_date: date | None = None
    is_male: bool | None = None
    city: str | None = None
    is_active: bool | None = None

    # Match - Player intermediate table
class MatchPlayerLink(SQLModel, table=True):
    match_id: int | None = Field(
        default=None,
        foreign_key="match.id",
        primary_key=True
    )
    player_id: int | None = Field(
        default=None,
        foreign_key="player.id",
        primary_key=True
    )

    # Match classes
class MatchBase(SQLModel):
    is_1v1: bool
    is_private: bool

class Match(MatchBase, table = True):
    id: int | None = Field(default=None, primary_key=True)
    host: Player | None = Relationship(sa_relationship_kwargs={"foreign_keys": "[Match.host_id]"})
    host_id: int | None = Field(default=None, foreign_key="player.id")
    winner_id: int | None = Field(default=None, foreign_key="player.id")
    winner: Player | None = Relationship(sa_relationship_kwargs={"foreign_keys": "[Match.winner_id]"})
    status: str | None = Field(default="Planificado")
    programmed_date: date | None
    players: list[Player] = Relationship(link_model=MatchPlayerLink)
    
class MatchCreate(MatchBase):
    is_1v1: bool
    is_private: bool
    host_id: int | None = None

class MatchPublic(MatchBase):
    id: int
    host_id: int | None
    winner_id: int | None    
    
class MatchUpdateSettings(MatchBase):
    is_1v1: bool | None = None
    is_private: bool | None = None

class MatchUpdatePlayers(MatchBase):
    players: list[Player] | None = None


    # Pydantic models
class PlayerLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None