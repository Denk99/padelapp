from sqlmodel import Session, SQLModel, create_engine

# Database Dev variables
DB_USER = "postgres"                # User of Postgre DB access
DB_PASSWORD = ""                    # Password of Postgre DB access
DB_HOST = "localhost"               # Local server
DB_PORT = "5432"                    # Default port
DB_NAME = "test"                    # DB name

# PostgreSQL URL
sql_url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(sql_url, echo=True)

# DB creation and session
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    print("Connection OK")

def get_session():
    with Session(engine) as session:
        yield session