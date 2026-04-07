from __future__ import annotations
from sqlmodel import Field, Session, SQLModel, create_engine, select, Relationship
from datetime import datetime, date, time
from pydantic import EmailStr, BaseModel
from typing import Optional
from enum import Enum

# Classes

    # Auxiliary classes
class Level(str, Enum):
    principiante = "principiante"
    amateur = "amateur"
    bueno = "bueno"
    muy_bueno = "muy bueno"

class MatchStatus(str, Enum):
    abierto = "abierto"
    completo = "completo"
    cancelado = "cancelado"

class MatchLevel(str, Enum):
    iniciacion = "iniciacion"
    intermedio = "intermedio"
    avanzado = "avanzado"
    cualquiera = "cualquiera"

class NotificationType(str, Enum):
    nuevo_partido = "nuevo partido"
    partido_completo = "partido completo"
    partido_cancelado = "partido cancelado"

    # Player classes
class PlayerBase(SQLModel):
    nombre: str = Field(max_length=100)
    email: EmailStr = Field(max_length=100, unique=True, index=True)
    nivel: Level | None = None
    ciudad: str | None = None
    creado_en: datetime | None = None
    rol: str | None = "jugador"

class Player(PlayerBase, table=True):
    __tablename__: str = "usuarios"
    id: int | None = Field(default=None, primary_key=True)
    password: str
    inscripciones: list[Inscription] = Relationship()

class PlayerPublic(SQLModel):
    id: int
    nombre: str
    email: EmailStr
    nivel: Level | None = None
    ciudad: str | None = None
    rol: str

class PlayerCreate(SQLModel):
    nombre: str
    email: EmailStr
    password: str
    nivel: Level | None = None
    ciudad: str | None = None
    rol: str | None = "jugador"

class PlayerUpdate(SQLModel):
    nombre: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    nivel: Level | None = None
    ciudad: str | None = None
    rol: str | None = None

    # Match classes
class MatchBase(SQLModel):
    fecha: date
    hora: time
    ubicacion: str
    nivel_requerido: MatchLevel | None = None
    plazas_totales: int | None = 4
    estado: MatchStatus | None = MatchStatus.abierto
    descripcion: str | None = None

class Match(MatchBase, table=True):
    __tablename__ : str = "partidos"
    id: int | None = Field(default=None, primary_key=True)
    creador_id: int | None = Field(default=None,foreign_key="usuarios.id")
    creado_en: datetime | None = None
    creador: Player | None = Relationship()
    jugadores: list[Player] = Relationship(link_model="MatchPlayerLink")
    inscripciones: list[Inscription] = Relationship()
    
class MatchCreate(SQLModel):
    fecha: date
    hora: time
    ubicacion: str
    nivel_requerido: MatchLevel | None = None
    plazas_totales: int | None = 4
    descripcion: str | None = None
    creador_id: int

class MatchPublic(SQLModel):
    id: int
    fecha: date
    hora: time
    ubicacion: str
    estado: MatchStatus
    plazas_totales: int
    creador_id: int | None   
    
class MatchUpdate(SQLModel):
    fecha: date | None = None
    hora: time | None = None
    ubicacion: str | None = None
    nivel_requerido: MatchLevel | None = None
    plazas_totales: int | None = None
    estado: MatchStatus | None = None
    descripcion: str | None = None

    # Match - Player intermediate table
class Inscription(SQLModel, table=True):
    __tablename__ : str = "inscripciones"
    id: int | None = Field(default=None, primary_key=True)
    partido_id: int | None = Field(
        default=None,
        foreign_key="partidos.id"
    )
    usuario_id: int | None = Field(
        default=None,
        foreign_key="usuarios.id"
    )
    estado: MatchStatus | None = MatchStatus.abierto
    inscrito_en: datetime | None = None
    partido: Match | None = Relationship()
    usuario: Player | None = Relationship()

class NotificationBase(SQLModel):
    tipo: NotificationType
    leida: bool = False
    creado_en: datetime | None = None

# Notification classes
class Notification(NotificationBase, table=True):
    __tablename__ : str = "notificaciones"
    id: int | None = Field(default=None, primary_key=True)
    usuario_id: int | None = Field(default=None, foreign_key="usuarios.id")
    partido_id: int | None = Field(default=None, foreign_key="partidos.id")

    usuario: Player | None = Relationship()
    partido: Match | None = Relationship()

class NotificationCreate(NotificationBase):
    usuario_id: int
    partido_id: int | None = None

class NotificationRead(NotificationBase):
    id: int
    usuario_id: int
    partido_id: int | None

    # Pydantic models
class PlayerLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None