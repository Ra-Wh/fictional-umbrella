import pytest
from app import app, db
from app.models import user_accounts, login_details
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

def login_helper(client, username="testuser", password="securepassword"):
    return client.post('/login', data={
        'username': username,
        'password': password
    }, follow_redirects=True)

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


def test_index_loads_with_data(client, test_user, create_tickets):
    login_helper(client)
    response = client.get('/', follow_redirects=True)
    assert response.status_code == 200
    assert b"Ticket 0" in response.data
    assert b"Recent Tickets" in response.data

from unittest.mock import patch

def test_db_error_shows_error_flash(client, test_user):
    login_helper(client)

    # Patch the 'all' method to raise an exception when trying to load tickets
    with patch('app.routes.tickets.query') as mock_query:
        mock_query.filter.return_value.limit.return_value.all.side_effect = Exception("Simulated DB failure")
        response = client.get('/', follow_redirects=True)
        print(response.data.decode())

        assert response.status_code == 200
        assert b"There was a problem loading ticket data. Please try again later." in response.data
        
def test_create_ticket_page_loads(client, test_user):
    login_helper(client)
    response = client.get('/ticket/create')

    assert response.status_code == 200
    assert b"Create" in response.data 
