from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, RegistrationForm, CreateTicketForm, AddCommentForm
from app import app, db
from flask_login import current_user, logout_user, login_required, login_user
import sqlalchemy as sa
import sqlalchemy.orm
from app.models import login_details, user_accounts, tickets, ticket_comments
from urllib.parse import urlsplit
from flask import session
from utils.template_utils import get_base_template
from datetime import datetime
from sqlalchemy import or_
from sqlalchemy.orm import joinedload


@app.route('/')
@app.route('/index')
@login_required
def index():
    app.logger.info(f"{current_user.username} accessed the index dashboard.")
    if current_user.is_admin:
        recent_tickets = tickets.query.filter(
            tickets.status != 'closed', 
        ).limit(10).all()


        count_open = tickets.query.filter(
            tickets.status == 'open',
        ).count()

        count_in_progress = tickets.query.filter(
            tickets.status == 'in_progress',
        ).count()

        count_closed = tickets.query.filter(
            tickets.status == 'closed',
        ).count()

    else:

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
            #Login error logging
            app.logger.info(f"unable to authenticate {form.username.data}. Invalid username or password.")
            #User error message
            flash('Invalid username or password')
            return redirect(url_for('login'))
        #Successful login logging
        app.logger.info(f"{current_user.username} authenticated")
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
    app.logger.info(f"{current_user.username} logged out")
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
        app.logger.info(f"{form.username.data} registration successful.")
        flash('Registration Successful', 'success')
        return redirect(url_for('login'))
    app.logger.info(f"Registration unsuccessful for username: {form.username.data}. Validation errors: {form.errors}")
    return render_template('register.html', title='Register', form=form)

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    app.logger.info(f"{current_user.username} accessed ticket creation.")
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
        app.logger.info(f"{current_user.username} created new ticket: {new_ticket.ticket_id}.")
        return redirect(url_for('index'))
    app.logger.info(f"{current_user.username} ticket creation failed. Creation errors: {form.errors}")
    return render_template('create.html', title="create ticket", form=form, base_template=get_base_template())

@app.route('/view', defaults={'ticket_id': None}, methods=['GET', 'POST'])
@app.route('/view/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
def view(ticket_id):
    app.logger.info(f"{current_user.username} viewed ticket: {ticket_id}")
    ticket = tickets.query.filter(
        tickets.ticket_id == ticket_id
    ).filter(
        or_(current_user.is_admin, tickets.user_account_id == current_user.user_account_id)
    ).first()

    if ticket is None:
        app.logger.error(f"{current_user.username} viewed ticket: {ticket_id} - ticket not found.")
        flash("Ticket not found or you don't have permission to view it.", "danger")
        return redirect(url_for("index"))
    
    form = AddCommentForm()

    if form.validate_on_submit():
        app.logger.error(f"{current_user.username} added comment to ticket: {ticket_id}")
        action = request.form.get('action')

        valid_statuses = {"open", "in_progress", "closed"}

        try:
            if action in valid_statuses:
                ticket.status = action
                if action == "closed":
                    ticket.closed_date = datetime.now()
                db.session.commit()
                app.logger.info(f"Ticket {ticket.ticket_id} status updated to '{action}' by {current_user.username}")
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Failed to update ticket status for ticket {ticket.ticket_id}: {e}")

        try:
            new_comment = ticket_comments(
                ticket_id=ticket_id,
                user_account_id=current_user.user_account_id,
                comment_details=form.comment.data
            )
            db.session.add(new_comment)
            db.session.commit()
            app.logger.info(f"Comment added to ticket {ticket_id} by {current_user.username}")
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Failed to add comment to ticket {ticket_id}: {e}")


        return redirect(url_for('view', ticket_id=ticket_id))  # Redirect to refresh template

    app.logger.error(f"{current_user.username} atempted to add comment to ticket: {ticket_id} errors: {form.errors}.")
    comments = ticket_comments.query.filter_by(ticket_id=ticket_id).all()
    username = login_details.query.filter_by(user_account_id=current_user.user_account_id).with_entities(login_details.username).scalar()

    return render_template('view.html', title='View Ticket', form=form, base_template=get_base_template(), ticket=ticket, comments=comments, username=username)

@app.route('/open-tickets', methods=['GET', 'POST'])
@login_required
def open_tickets():
    if current_user.is_admin:
        open_tickets = tickets.query.filter(
            tickets.status != 'closed', 
        ).all()
    else:
        open_tickets = tickets.query.filter(
            tickets.status != 'closed', 
            tickets.user_account_id == current_user.user_account_id
        ).all()
    return render_template('open.html', title='Open Tickets', base_template=get_base_template(), tickets=open_tickets)

@app.route('/closed-tickets', methods=['GET', 'POST'])
@login_required
def closed_tickets():
    if current_user.is_admin:
        closed_tickets = tickets.query.filter(
            tickets.status == 'closed',
        ).all()
    else:
        closed_tickets = tickets.query.filter(
            tickets.status == 'closed', 
            tickets.user_account_id == current_user.user_account_id
        ).all()
    return render_template('closed.html', title='Open Tickets', base_template=get_base_template(), tickets=closed_tickets)


@app.route('/delete', defaults={'ticket_id': None}, methods=['GET', 'POST'])
@app.route('/delete/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
def delete(ticket_id):
    if not current_user.is_admin:
        flash("You do not have permission to perform this action.", "warning")
        return redirect(url_for("index"))

    ticket = tickets.query.filter_by(ticket_id=ticket_id).first()
    if not ticket:
        flash("Ticket not found.", "danger")
        return redirect(url_for("index"))

    db.session.delete(ticket)
    db.session.commit()

    flash("Ticket and associated comments deleted successfully!", "success")
    return redirect(url_for("index"))

@app.route('/promote', defaults={'user_account_id': None}, methods=['GET', 'POST'])
@app.route('/promote/<int:user_account_id>', methods=['GET', 'POST'])
@login_required
def promote(user_account_id):
    if current_user.is_admin:
        user = user_accounts.query.filter_by(user_account_id=user_account_id).first()
        if user:
            user.is_admin = True
            db.session.commit()
            flash("User promoted successfully", "success")
        else:
            flash("User not found.", "danger") # Change this to a generic error?
    else:
        flash("You do not have permission to perform this action.", "warning")
    return redirect(url_for("users"))


@app.route('/demote', defaults={'user_account_id': None}, methods=['GET', 'POST'])
@app.route('/demote/<int:user_account_id>', methods=['GET', 'POST'])
@login_required
def demote(user_account_id):
    if not current_user.is_admin:
        flash("You do not have permission to perform this action.", "warning")
        return redirect(url_for("users"))

    if user_account_id == current_user.user_account_id:
        flash("You cannot demote yourself.", "warning")
        return redirect(url_for("users"))

    user = user_accounts.query.filter_by(user_account_id=user_account_id).first()
    if user:
        user.is_admin = False
        db.session.commit()
        flash("User demoted successfully.", "success")
    else:
        flash("Unable to process your request.", "danger")
    return redirect(url_for("users"))
    
@app.route('/delete/user', defaults={'user_account_id': None}, methods=['GET', 'POST'])
@app.route('/delete/user/<int:user_account_id>', methods=['GET', 'POST'])
@login_required
def delete_user(user_account_id):
    if not current_user.is_admin:
        flash("You do not have permission to perform this action.", "warning")
        return redirect(url_for("index"))
        
    user = user_accounts.query.filter_by(user_account_id=user_account_id).first()
    if not user:
        flash ("User not found.", "danger")
        return redirect(url_for("index"))
    
    db.session.delete(user)
    db.session.commit()

    flash("User deleted successfully!", "success")
    return redirect(url_for("users"))

@app.route('/users', methods=['GET', 'POST'])
@login_required
def users():
    users = db.session.query(
        user_accounts.user_account_id,
        user_accounts.first_name,
        user_accounts.last_name,
        user_accounts.account_created_date,
        user_accounts.is_deleted,
        user_accounts.account_deleted_date,
        user_accounts.is_admin,
        login_details.username
    ).join(login_details).all()

    return render_template('users.html', title='Users', base_template=get_base_template(), users=users)