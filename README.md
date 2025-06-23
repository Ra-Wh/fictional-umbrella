# fictional-umbrella

## Initial set-up

Clone the repository onto your local device using your prefered method.

Create the python virtual environment (venv)

~ python3 -m venv venv

Activate the venv

- linux bash:           ~ source venv/bin/activate
- windows bash:         ~ source venv/Scripts/activate
- windows powershell:   ~ venv\Scripts\activate

Install requirements from requirements.txt

~ pip install -r requirements.txt

Start app

~ flask run

## Basic User Accout Details

Username: User1

Password: 1234

## Admin User Account Details

Username: Admin1

Password: 4321

## Add two basic users to db

flask db init
flask db migrate -m 'initial'
flask db upgrade

#Python

from app import app, db
from app.models import user_accounts, login_details, tickets
import sqlalchemy as sa
app.app_context().push()

new_user = user_accounts(first_name='Admin', last_name='1', phone_number='07852345169', is_admin=True)
db.session.add(new_user)
db.session.commit()

new_login = login_details(user_account_id=new_user.user_account_id, username="Admin1", email_address="admin1@email.com")
new_login.set_password('4321')
db.session.add(new_login)
db.session.commit()

new_user = user_accounts(first_name='User', last_name='1', phone_number='07852345169', is_admin=False)
db.session.add(new_user)
db.session.commit()

new_login = login_details(user_account_id=new_user.user_account_id, username="User1", email_address="user1@email.com")
new_login.set_password('1234')
db.session.add(new_login)
db.session.commit()

## Run test

set FLASK_ENV=testing && python -m pytest

Without the FLASK_ENV the prod database will be deleted!!

Remove-Item Env:FLASK_ENV

Run this once testing is complete!!