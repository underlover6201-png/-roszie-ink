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
from scripts.seed_data import _seed_logic

with app.app_context():
    db.create_all()
    print("✓ All tables created.")

    # Auto-create admin if no users exist
    from app.models.user import User, UserRole
    if User.query.count() == 0:
        admin = User(
            email="admin@roszieink.com",
            username="roszie",
            role=UserRole.admin,
        )
        admin.set_password("roszieink!!!")
        db.session.add(admin)
        db.session.commit()
        print("✓ Admin account created: roszie / roszieink!!!")

    # Seed demo data if DB is empty
    from app.models.artist import Artist
    if Artist.query.count() == 0:
        print("Seeding demo data...")
        _seed_logic()
        print("✓ Demo data seeded.")
