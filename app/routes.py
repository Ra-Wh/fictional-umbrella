from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, RegistrationForm, CreateTicketForm, AddCommentForm
from app import app, db
from flask_login import current_user, logout_user, login_required, login_user
import sqlalchemy as sa
from app.models import login_details, user_accounts, tickets, ticket_comments
from urllib.parse import urlsplit
from flask import session
from utils.template_utils import get_base_template


@app.route('/')
@app.route('/index')
@login_required
def index():
    recent_tickets = tickets.query.filter(
        tickets.status != 'closed', 
        tickets.user_account_id == current_user.user_account_id
    ).limit(10).all()

    count_open = tickets.query.filter(
        tickets.status == 'open',
        tickets.user_account_id == current_user.user_account_id
    ).count()

    count_in_progress = tickets.query.filter(
        tickets.status == 'in_progress',
        tickets.user_account_id == current_user.user_account_id
    ).count()

    count_closed = tickets.query.filter(
        tickets.status == 'closed',
        tickets.user_account_id == current_user.user_account_id
    ).count()

    return render_template(
        'index.html', 
        title='Home', 
        base_template=get_base_template(), 
        tickets=recent_tickets, 
        open_tickets=count_open, 
        in_progress_tickets=count_in_progress,
        closed_tickets=count_closed)


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
        user = user_accounts(
            first_name=form.first_name.data, 
            last_name=form.last_name.data, 
            phone_number=form.phone_number.data
            )
        db.session.add(user)
        db.session.commit()
        login = login_details(
            user_account_id=user.user_account_id, 
            username=form.username.data, 
            email_address=form.email.data
            )
        login.set_password(form.password.data)
        db.session.add(login)
        db.session.commit()
    return render_template('register.html', title='Register', form=form)

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form=CreateTicketForm()
    if form.validate_on_submit():
        new_ticket = tickets(
            user_account_id=current_user.user_account_id, 
            ticket_details=form.details.data, 
            issue_type=form.issue_type.data, 
            priority=form.priority.data,
            ticket_summary=form.summary.data
            )
        db.session.add(new_ticket)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create.html', title="create ticket", form=form, base_template=get_base_template())

@app.route('/view', defaults={'ticket_id': None}, methods=['GET', 'POST'])
@app.route('/view/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
def view(ticket_id):
    ticket = tickets.query.filter(
        tickets.ticket_id == ticket_id,
        tickets.user_account_id == current_user.user_account_id
    ).first()
    form=AddCommentForm()
    if form.validate_on_submit():
        action = request.form.get('action')
        new_comment = ticket_comments(
            ticket_id=ticket_id,
            user_account_id=current_user.user_account_id,
            comment_details=form.comment.data
        )
        ticket.status=action
        db.session.add(new_comment)
        db.session.commit()
    comments = ticket_comments.query.filter_by(
        ticket_id=ticket_id
    )
    username = login_details.query.filter_by(user_account_id=current_user.user_account_id).with_entities(login_details.username).scalar()
    return render_template('view.html', title='view ticket', form=form, base_template=get_base_template(), ticket=ticket, comments=comments, username=username)

@app.route('/open-tickets', methods=['GET', 'POST'])
@login_required
def open_tickets():
    open_tickets = tickets.query.filter(
        tickets.status != 'closed', 
        tickets.user_account_id == current_user.user_account_id
    ).all()
    return render_template('open.html', title='Open Tickets', base_template=get_base_template(), tickets=open_tickets)

@app.route('/closed-tickets', methods=['GET', 'POST'])
@login_required
def closed_tickets():
    return render_template('closed.html', title='Open Tickets', base_template=get_base_template())