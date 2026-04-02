import pytest
from app import app, db
from unittest.mock import patch
from config import TestConfig


loginDetails = {
    'first_name': 'Test',
    'last_name':'User',
    'phone_number': '1234567890',
    'username': 'testuser',
    'email': 'test@example.com',
    'password': '!LongPassword1',
}

@pytest.fixture
def client():
    app.config.from_object(TestConfig)
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            assert 'test' in app.config['SQLALCHEMY_DATABASE_URI']
            db.drop_all()


app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

def test_register_success(client):
    response = client.post('/register', data={
        'first_name': loginDetails['first_name'],
        'last_name': loginDetails['last_name'],
        'phone_number': loginDetails['phone_number'],
        'username': loginDetails['username'],
        'email': loginDetails['email'],
        'password': loginDetails['password'],
        'password2': loginDetails['password']
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Registration Successful" in response.data

def test_register_missing_field(client):
    response = client.post('/register', data={
        'first_name': loginDetails['first_name'],
        'last_name': loginDetails['last_name'],
        'phone_number': loginDetails['phone_number'],
        'username': '',
        'email': loginDetails['email'],
        'password': loginDetails['password'],
        'password2': loginDetails['password']
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"This field is required." in response.data

from unittest.mock import patch

def test_register_failure(client):
    with patch('app.routes.db.session.commit', side_effect=Exception("Simulated DB failure")):
        response = client.post('/register', data={
            'first_name': loginDetails['first_name'],
            'last_name': loginDetails['last_name'],
            'phone_number': loginDetails['phone_number'],
            'username': loginDetails['username'],
            'email': loginDetails['email'],
            'password': loginDetails['password'],
            'password2': loginDetails['password']
        }, follow_redirects=True)

    assert response.status_code == 200
    assert b"An error occurred while creating your account" in response.data

def test_minimally_secure_password(client):
    response = client.post('/register', data={
        'first_name': loginDetails['first_name'],
        'last_name': loginDetails['last_name'],
        'phone_number': loginDetails['phone_number'],
        'username': loginDetails['username'],
        'email': loginDetails['email'],
        'password': loginDetails['password'],
        'password2': loginDetails['password']
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Registration Successful" in response.data

def test_very_secure_password(client):
    response = client.post('/register', data={
        'first_name': loginDetails['first_name'],
        'last_name': loginDetails['last_name'],
        'phone_number': loginDetails['phone_number'],
        'username': loginDetails['username'],
        'email': loginDetails['email'],
        'password': loginDetails'TIAV5Pn0wgi!hh',
        'password2': loginDetails'TIAV5Pn0wgi!hh'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Registration Successful" in response.data

def test_password_with_no_capital_letter(client):
    response = client.post('/register', data={
        'first_name': loginDetails['first_name'],
        'last_name': loginDetails['last_name'],
        'phone_number': loginDetails['phone_number'],
        'username': loginDetails['username'],
        'email': loginDetails['email'],
        'password': loginDetails'!longpassword1',
        'password2': loginDetails'!longpassword1'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Password must include at least one uppercase letter, one lowercase letter, one number, and one special character." in response.data

def test_password_with_no_lowercase_letter(client):
    response = client.post('/register', data={
        'first_name': loginDetails['first_name'],
        'last_name': loginDetails['last_name'],
        'phone_number': loginDetails['phone_number'],
        'username': loginDetails['username'],
        'email': loginDetails['email'],
        'password': loginDetails'!LONGPASSWORD1',
        'password2': loginDetails'!LONGPASSWORD1'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Password must include at least one uppercase letter, one lowercase letter, one number, and one special character." in response.data

def test_password_with_no_number(client):
    response = client.post('/register', data={
        'first_name': loginDetails['first_name'],
        'last_name': loginDetails['last_name'],
        'phone_number': loginDetails['phone_number'],
        'username': loginDetails['username'],
        'email': loginDetails['email'],
        'password': loginDetails'!LongPasswords',
        'password2': loginDetails'!LongPasswords'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Password must include at least one uppercase letter, one lowercase letter, one number, and one special character." in response.data

def test_password_with_no_special_character(client):
    response = client.post('/register', data={
        'first_name': loginDetails['first_name'],
        'last_name': loginDetails['last_name'],
        'phone_number': loginDetails['phone_number'],
        'username': loginDetails['username'],
        'email': loginDetails['email'],
        'password': loginDetails'LongPassword11',
        'password2': loginDetails'LongPassword11'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Password must include at least one uppercase letter, one lowercase letter, one number, and one special character." in response.data

