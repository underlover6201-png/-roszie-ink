"""
Production DB initializer.
Run once on a fresh database: creates all tables from models,
then stamps alembic as up-to-date so flask db upgrade is a no-op.
"""
import os
import sys

os.environ.setdefault("FLASK_ENV", "production")

# wsgi.py already calls create_app("production")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wsgi import app
from app.extensions import db

with app.app_context():
    db.create_all()
    print("✓ All tables created.")
