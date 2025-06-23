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

def test_ticket_creation(client, test_user):
    login_helper(client)

    response = client.post('/ticket/create', data={
        'details': 'Ticket details', 
        'issue_type' : 'support', 
        'priority' : 'medium',
        'summary' :'Ticket Summary'
    }, follow_redirects = True)

    assert response.status_code == 200
    assert b"Ticket created successfully" in response.data

def test_ticket_creation_error(client, test_user):
    login_helper(client)

    response = client.post('/ticket/create', data={
        'details': 'Ticket details', 
        'issue_type' : 'support', 
        'priority' : 'medium',
        'summary' :''
    }, follow_redirects = True)

    assert response.status_code == 200
    assert b"This field is required." in response.data

def test_ticket_creation_db_exception(client, test_user):
    login_helper(client)

    with patch('app.routes.db.session.commit', side_effect=Exception("Simulated DB failure")):
        response = client.post('/ticket/create', data={
            'details': 'Ticket details', 
            'issue_type' : 'support', 
            'priority' : 'medium',
            'summary' :'Ticket Summary'
        }, follow_redirects = True)

    assert response.status_code == 200
    assert b"An error occurred while creating your ticket. Please try again later." in response.data