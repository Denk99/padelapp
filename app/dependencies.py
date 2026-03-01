from app.database import get_session
from sqlmodel import Session
from typing import Annotated
from fastapi import Depends

SessionDep = Annotated[Session, Depends(get_session)]