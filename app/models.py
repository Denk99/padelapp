from sqlmodel import Field, Session, SQLModel, create_engine, select, Relationship

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
