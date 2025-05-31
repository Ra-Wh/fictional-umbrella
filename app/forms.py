import sqlalchemy as sa

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=50)])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=12, max=64),
        Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])', 
            message="Password must include at least one uppercase letter, one lowercase letter, one number, and one special character.")
    ])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    phone_number = StringField('Phone Number')
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class CreateTicketForm(FlaskForm):
    issue_type = SelectField('Issue Type', choices=[(1, 'incident'),(2, 'request'), (3, 'support')], validators=[DataRequired()])
    priority = SelectField('Priority', choices=[(1, 'Low'), (2, 'Medium'), (3, 'High'), (4, 'Critical')], validators=[DataRequired()])
    summary = TextAreaField('Summary', validators=[DataRequired()])
    details = TextAreaField('Details', validators=[DataRequired()])