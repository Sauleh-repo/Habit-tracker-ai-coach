# sql_app/init_db.py

from .database import Base, engine
from . import models

print("Creating database tables...")

# This command connects to the database and creates all the tables
# defined in your models.py file.
Base.metadata.create_all(bind=engine)

print("Database tables created successfully.")