"""pytest fixtures"""
import pytest

from app import create_app
from app.extensions import db as _db
from app.models.user import User, UserRole


@pytest.fixture(scope="session")
def app():
    app = create_app("testing")
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope="function")
def db(app):
    with app.app_context():
        yield _db
        _db.session.rollback()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def admin_user(db):
    user = User(email="admin@test.com", username="testadmin", role=UserRole.admin)
    user.set_password("testpass123")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def auth_client(client, admin_user):
    """已登入的 test client"""
    client.post(
        "/admin/login",
        data={"email": admin_user.email, "password": "testpass123"},
        follow_redirects=True,
    )
    return client
