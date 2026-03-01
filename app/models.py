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
