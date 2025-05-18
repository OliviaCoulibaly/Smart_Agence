from sqlalchemy import create_engine # type: ignore
from sqlalchemy.orm import sessionmaker, declarative_base # type: ignore

db_path = 'sqlite:///smart_agence.db'
engine = create_engine(db_path)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

try:
    conn = engine.connect() # type: ignore

    print("Success!")
except Exception as ex:
   print(f"Erreur de connexion : {ex}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()   