import pytest
from app import app, db
from app.models import user_accounts, login_details, tickets
from unittest.mock import patch
from config import TestConfig



@pytest.fixture
def client():
    app.config.from_object(TestConfig)
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            assert 'test' in app.config['SQLALCHEMY_DATABASE_URI']
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

@pytest.fixture
def test_admin():
    user = user_accounts(
        first_name="Test",
        last_name="Admin",
        phone_number="1234567890",
        is_admin=True
    )
    db.session.add(user)
    db.session.flush()

    login = login_details(
        user_account_id=user.user_account_id,
        username="testadmin",
        email_address="admin@example.com"
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

def login_as_admin(client):
    return login_helper(client, username="testadmin")

@pytest.fixture
def create_tickets(test_user):
    from app.models import tickets
    for i in range(12):
        ticket = tickets(
            ticket_summary=f"Ticket {i}",
            ticket_details="This is a test ticket",
            issue_type="support",
            status="open",
            priority="medium",
            user_account_id=test_user.user_account_id
        )
        db.session.add(ticket)
    db.session.commit()

def test_user_cant_delete_tickets(client, test_user, create_tickets):
    login_helper(client)
    response = client.get('/ticket/delete/2', follow_redirects=True)
    assert response.status_code == 200
    assert b'You do not have permission to perform this action.' in response.data

def test_admin_can_delete_ticket(client, test_admin, create_tickets):
    login_as_admin(client)
    response = client.get('/ticket/delete/2', follow_redirects=True)
    assert response.status_code == 200
    print(response.data.decode())
    assert b'Ticket deleted successfully!' in response.data

def test_db_error(client, test_admin, create_tickets):
    login_as_admin(client)

    with patch('app.routes.db.session.commit', side_effect=Exception("Simulated DB failure")):
        response = client.get('/ticket/delete/2', follow_redirects=True)

    assert response.status_code == 200
    assert b"An error occurred deleting the ticket. Please try again later." in response.data