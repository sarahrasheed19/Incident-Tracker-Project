from flask_sqlalchemy import SQLAlchemy
from app.base import Session

db = SQLAlchemy()
session = Session()
