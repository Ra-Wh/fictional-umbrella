from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, RegistrationForm, CreateTicketForm, AddCommentForm
from app import app, db
from flask_login import current_user, logout_user, login_required, login_user
import sqlalchemy as sa
from app.models import login_details, user_accounts
from urllib.parse import urlsplit
from flask import session
from utils.template_utils import get_base_template


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home', base_template=get_base_template())


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return render_template('login.html', title='Sign in', form=form)
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(login_details).where(login_details.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        user_details = db. session.scalar(
            sa.select(user_accounts).where(user_accounts.user_account_id == user.user_account_id)
        )
        login_user(user_details)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign in', form=form)

@app.route('/logout', methods=['POST'])
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = user_accounts(first_name=form.first_name.data, last_name=form.last_name.data, phone_number=form.phone_number.data)
        db.session.add(user)
        db.session.commit()
        login = login_details(user_account_id=user.user_account_id, username=form.username.data, email_address=form.email.data)
        login.set_password(form.password.data)
        db.session.add(login)
        db.session.commit()
    return render_template('register.html', title='Register', form=form)

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form=CreateTicketForm()
    return render_template('create.html', title="create ticket", form=form, base_template=get_base_template())

@app.route('/view', methods=['GET', 'POST'])
@login_required
def view():
    form=AddCommentForm()
    return render_template('view.html', title='view ticket', form=form, base_template=get_base_template())