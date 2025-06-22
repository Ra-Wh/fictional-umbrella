import pytest
from app import app, db
from app.models import user_accounts, login_details, tickets
from unittest.mock import patch


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

def test_correct_ticket_returned(client, test_user, create_tickets):
    login_helper(client)

    response = client.get('/ticket/view/2', follow_redirects=True)
    assert response.status_code == 200
    assert b"Ticket 1" in response.data

def test_add_comment(client, test_user, create_tickets):
    login_helper(client)

    response = client.post('/ticket/view/2', data={
         'ticket_id' : 2,
         'user_account_id' : test_user.user_account_id,
         'comment' : 'Test comment'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Test comment" in response.data

def test_error_if_no_comment_data(client, test_user, create_tickets):
    login_helper(client)

    response = client.post('/ticket/view/2', data={
        'ticket_id' : 2,
        'user_account_id' : test_user.user_account_id,
        'comment' : ''
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"This field is required." in response.data

def test_db_error(client, test_user, create_tickets):
    login_helper(client)

    with patch('app.routes.db.session.commit', side_effect=Exception("Simulated DB failure")):
        response = client.post('/ticket/view/2', data={
            'ticket_id' : 2,
            'user_account_id' : test_user.user_account_id,
            'comment' : 'Test comment'
        }, follow_redirects=True)

    assert response.status_code == 200
    assert b"An error occurred while editing comment. Please try again later." in response.data

def test_close_ticket(client, test_admin, create_tickets):
    login_as_admin(client)

    response = client.post(f'/ticket/view/2', data={
        'comment': 'Closing this ticket.',
        'action': 'closed'
    }, follow_redirects=True)

    assert response.status_code == 200
    updated_ticket = db.session.get(tickets, 2)
    assert updated_ticket.status.value == 'Closed'

def test_user_cant_close_ticket(client, test_user, create_tickets):
    login_helper(client)

    response = client.post('/ticket/view/2', data={
        'ticket_id' : 2,
        'user_account_id' : test_user.user_account_id,
        'comment' : ''
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Comment and Close Ticket" not in response.data


