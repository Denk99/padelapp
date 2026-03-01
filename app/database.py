from sqlmodel import Session, SQLModel, create_engine

# Database Dev variables
sql_file = "padelapp.db"
sql_url = f"sqlite:///{sql_file}"

connect_args = {"check_same_thread": False}
engine = create_engine(sql_url, connect_args=connect_args)

# DB creation and session
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

