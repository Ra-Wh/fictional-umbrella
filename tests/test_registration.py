import pytest
from app import app, db
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


app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

def test_register_success(client):
    response = client.post('/register', data={
        'first_name': 'Test',
        'last_name': 'User',
        'phone_number': '1234567890',
        'username': 'testuser',
        'email': 'test@example.com',
        'password': '!LongPassword1',
        'password2': '!LongPassword1'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Registration Successful" in response.data

def test_register_missing_field(client):
    response = client.post('/register', data={
        'first_name': 'Test',
        'last_name': 'User',
        'phone_number': '1234567890',
        'username': '',
        'email': 'test@example.com',
        'password': '!LongPassword1',
        'password2': '!LongPassword1'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"This field is required." in response.data

from unittest.mock import patch

def test_register_failure(client):
    with patch('app.routes.db.session.commit', side_effect=Exception("Simulated DB failure")):
        response = client.post('/register', data={
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '1234567890',
            'username': 'testuser',
            'email': 'test@example.com',
            'password': '!LongPassword1',
            'password2': '!LongPassword1'
        }, follow_redirects=True)

    assert response.status_code == 200
    assert b"An error occurred while creating your account" in response.data