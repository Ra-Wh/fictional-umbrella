from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
import enum

#Types

class IssueType(enum.Enum):
    incident = 'Incident'
    request = 'Request'
    support = 'Support'

class PriorityType(enum.Enum):
    low = 'low'
    medium = 'medium'
    high = 'high'
    critical = 'critical'

class StatusType(enum.Enum):
    open = 'Open'
    closed = 'Closed'
    in_progress = 'In Progress'

# Tables

class error_logging(db.Model):
    error_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    error_timestamp: so.Mapped[sa.DateTime] = so.mapped_column(sa.DateTime, default=sa.func.now(), nullable=False)
    error_message: so.Mapped[str] = so.mapped_column(sa.TEXT)
    error_severity: so.Mapped[str] = so.mapped_column(sa.Enum('INFO', 'WARNING', 'ERROR', 'CRITICAL'))

class tickets(db.Model):
    ticket_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_account_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user_accounts.user_account_id', ondelete='CASCADE'), nullable=False)
    created_date: so.Mapped[sa.DateTime] = so.mapped_column(sa.DateTime, default=sa.func.now(), nullable=False)
    ticket_details: so.Mapped[sa.Text] = so.mapped_column(sa.Text, nullable=False)
    issue_type: so.Mapped[sa.Enum] = so.mapped_column(sa.Enum(IssueType), nullable=False)
    priority: so.Mapped[sa.Enum] = so.mapped_column(sa.Enum(PriorityType), nullable=False)
    isClosed: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)
    ticket_summary: so.Mapped[str] = so.mapped_column(sa.String(40), nullable=False)
    status: so.Mapped[sa.Enum] = so.mapped_column(sa.Enum(StatusType), nullable=False, default=StatusType.open)
    needs_attention: so.Mapped[bool] = so.mapped_column(sa.Boolean, nullable=False, default=False)

class ticket_comments(db.Model):
    comment_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    ticket_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('tickets.ticket_id', ondelete='CASCADE'), nullable=False)
    user_account_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user_accounts.user_account_id', ondelete='CASCADE'), nullable=False)
    created_date: so.Mapped[sa.DateTime] = so.mapped_column(sa.DateTime, default=sa.func.now(), nullable=False)
    comment_details: so.Mapped[sa.Text] = so.mapped_column(sa.Text, nullable=False)

class user_accounts(UserMixin, db.Model):
    user_account_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    first_name: so.Mapped[str] = so.mapped_column(sa.String(50), nullable=False)
    last_name: so.Mapped[str] = so.mapped_column(sa.String(50), nullable=False)
    phone_number: so.Mapped[str] = so.mapped_column(sa.String(20))
    account_created_date: so.Mapped[sa.DateTime] = so.mapped_column(sa.DateTime, default=sa.func.now(), nullable=False)
    last_login: so.Mapped[sa.DateTime] = so.mapped_column(sa.DateTime, default=sa.func.now(), nullable=False)
    is_deleted: so.Mapped[bool] = so.mapped_column(sa.Boolean, nullable=False, default=0)
    account_deleted_date: so.Mapped[sa.DateTime] = so.mapped_column(sa.DateTime, nullable=True)
    is_admin: so.Mapped[bool] = so.mapped_column(sa.Boolean, nullable=False, default=0)
  
    def get_id(self):
        return str(self.user_account_id)

class login_details(db.Model):
    login_id: so.Mapped[int] =so.mapped_column(primary_key=True)
    user_account_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user_accounts.user_account_id', ondelete='CASCADE'), nullable=False)
    username: so.Mapped[str] = so.mapped_column(sa.String(50), index=True, unique=True, nullable=False)
    email_address: so.Mapped[str] = so.mapped_column(sa.String(120), nullable=False, index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256), nullable=False)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        if password:
            self.password_hash = generate_password_hash(password)
        else:
            print("Error: Password cannot be None or empty")

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return db.session.get(user_accounts, int(id))