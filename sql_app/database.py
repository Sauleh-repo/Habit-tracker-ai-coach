import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# This finds the absolute path to the directory this file is in
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# This ensures the DB file is always created inside the sql_app folder on any OS
DB_PATH = os.path.join(BASE_DIR, "sql_app.db")

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()