import pytest
from app import app, db
from app.models import user_accounts, login_details

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

@pytest.fixture
def test_user():
    user = user_accounts(
        first_name="Test",
        last_name="User",
        phone_number="1234567890"
    )
    db.session.add(user)
    db.session.flush()

    login = login_details(
        user_account_id=user.user_account_id,
        username="testuser",
        email_address="test@example.com"
    )
    login.set_password("securepassword")
    db.session.add(login)
    db.session.commit()

    return login

def login_helper(client, username="testuser", password="securepassword"):
    return client.post('/login', data={
        'username': username,
        'password': password
    }, follow_redirects=True)


def test_successful_login(client, test_user):
    response = login_helper(client)
    assert response.status_code == 200
    assert b"Recent Tickets" in response.data

def test_failed_login(client):
    response = client.post('/login', data={
        'username': 'wronguser',
        'password': 'wrongpass'
    }, follow_redirects=True)
    assert b"Invalid username or password" in response.data

def test_logout(client, test_user):
    login_helper(client)
    response = client.post('/logout', follow_redirects=True)
    assert b"Successfully logged out." in response.data

