from flask_wtf import FlaskForm
from wtforms import DateField, StringField, PasswordField, IntegerField, SubmitField, SelectField, FloatField, TextAreaField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    company_name = StringField('Company Name', validators=[DataRequired(), Length(min=2, max=255)])
    address = StringField('Address', validators=[DataRequired(), Length(min=2, max=255)])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    category = SelectField('Category', choices=[('PVT', 'Private'), ('PBC', 'Public')], validators=[DataRequired()])
    submit = SubmitField('Register')
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email address.')

class TenderForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    tender_number = StringField('Tender Number', validators=[DataRequired()])
    # Change to IntegerField to match the model
    required_experience = IntegerField('Required Experience', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    delivery_time = StringField('Delivery Time', validators=[DataRequired()])
    # Add field for additional_criteria
    additional_criteria = StringField('Additional Criteria', validators=[DataRequired()])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Create Tender')

class BidForm(FlaskForm):
    bid_document = FileField('Bid Document (PDF only)', validators=[DataRequired()])
    submit = SubmitField('Upload Bid')
