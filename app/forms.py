import sqlalchemy as sa

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, ValidationError
from wtforms.widgets import Select

def validate_issue_type(form, field):
    valid_choices = ['incident', 'request', 'support']
    if field.data not in valid_choices:
        raise ValidationError('Invalid issue type selection.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    phone_number = StringField('Phone Number')
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
    DataRequired(),
    Length(min=12, max=64),
    Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])', 
           message="Password must include at least one uppercase letter, one lowercase letter, one number, and one special character.")
           ])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class CreateTicketForm(FlaskForm):
    issue_type = SelectField(
        'Issue Type',
        choices=[('incident', 'Incident'), ('request', 'Request'), ('support', 'Support')],
        validators=[DataRequired(), validate_issue_type],
        render_kw={"placeholder": "Select an issue type"}
    )
    priority = SelectField(
        'Priority', 
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')], 
        validators=[DataRequired()], 
        widget=Select(),
        render_kw={"placeholder": "Select priority level"}
        )
    summary = TextAreaField(
        'Summary', 
        validators=[DataRequired(), Length(min=1, max=40)],
        render_kw={"placeholder": "Briefly summarize the issue."}
        )
    details = TextAreaField(
        'Details', 
        validators=[DataRequired(), Length(min=1, max=500)],
        render_kw={"placeholder": "Provide detailed information about the issue"}
        )
    submit = SubmitField('Submit')

class AddCommentForm(FlaskForm):
    comment = TextAreaField('Add comment', validators=[DataRequired()])
    submit = SubmitField('Add')