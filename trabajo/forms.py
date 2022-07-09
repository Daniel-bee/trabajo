from flask_wtf import FlaskForm
from trabajo import bcrypt
from trabajo.models import User
from flask_ckeditor import CKEditorField
import phonenumbers
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, SelectField, IntegerField, SubmitField, TextAreaField, DateField, BooleanField, RadioField, URLField
from wtforms.validators import DataRequired, EqualTo, Email, Length, url, ValidationError
from flask_login import current_user


class candidateForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=3, max=20)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=60)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Create an account")

    def validate_phone(self, phone_number):
        if len(phone_number.data) > 14:
            raise ValidationError('Invalid phone number.')
        try:
            p = phonenumbers.parse(phone_number.data)
            if not (phonenumbers.is_valid_number(p)):
                raise ValidationError('Invalid phone number.')
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')
    def validate_phone_number(self, phone_number):
        user = User.query.filter_by(phone_number=phone_number.data).first()
        if user:
            raise ValidationError('That Phone Number is taken. Please choose a different one.')
            
class candidateUpdateForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=3, max=20)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone', validators=[DataRequired()])
    submit = SubmitField("Update")

    def validate_phone(self, phone_number):
        if len(phone_number.data) > 14:
            raise ValidationError('Invalid phone number.')
        try:
            p = phonenumbers.parse(phone_number.data)
            if not (phonenumbers.is_valid_number(p)):
                raise ValidationError('Invalid phone number.')
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number')

class employerForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=3, max=20)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=3, max=20)])
    company_name = StringField('Company Name', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=60)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Create an account")

    def validate_phone(self, phone_number):
        if len(phone_number.data) > 14:
            raise ValidationError('Invalid phone number.')
        try:
            p = phonenumbers.parse(phone_number.data)
            if not (phonenumbers.is_valid_number(p)):
                raise ValidationError('Invalid phone number.')
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')
    def validate_company_name(self, company_name):
        user = User.query.filter_by(company_name=company_name.data).first()
        if user:
            raise ValidationError('That Company name is taken. Please choose a different one.')
    def validate_phone_number(self, phone_number):
        user = User.query.filter_by(phone_number=phone_number.data).first()
        if user:
            raise ValidationError('That Phone Number is taken. Please choose a different one.')

class employerUpdateForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=3, max=20)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=3, max=20)])
    company_name = StringField('Company Name', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone', validators=[DataRequired()])
    submit = SubmitField("Update")

    def validate_phone(self, phone_number):
        if len(phone_number.data) > 14:
            raise ValidationError('Invalid phone number.')
        try:
            p = phonenumbers.parse(phone_number.data)
            if not (phonenumbers.is_valid_number(p)):
                raise ValidationError('Invalid phone number.')
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number')

class userLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Sign in')
    
class chnagePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired(), Length(min=8, max=60)])
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=8, max=60)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Update')

    def validate_old_password(self, old_password):
        user = User.query.filter_by(id=current_user.id).first()
        password = bcrypt.check_password_hash(user.password, old_password.data)
        if not password:
            raise ValidationError('password not match.')

class jobPostForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Sign in')

class jobPostForm(FlaskForm):
    job_title = StringField('Job Title', validators=[DataRequired()])
    job_description = CKEditorField('Job Description', validators=[DataRequired()])
    job_type = SelectField(u'Job Type', 
                    choices=[('Full Time', 'Full Time'), 
                             ('Part Time', 'Part Time'),
                             ('Freelance', 'Freelance'),
                             ('Internship', 'Internship'),
                             ('Temporary', 'Temporary')],
                    validators=[DataRequired()])

    gender = RadioField(u'Gender', 
                choices=[('Female', 'Female'), 
                            ('Male', 'Male'),
                            ('Both', 'Both'),
                            ], validators=[DataRequired()])
    deadline = DateField('Application Deadline')
    experiance = SelectField('Experiance',
                choices=[('Fresh', 'Fresh'),
                        ('< 1 year', '< 1 year'),
                        ('1 year','1 year'),
                        ('2 years','2 years'),
                        ('3 years','3 years'),
                        ('4 years','4 years'),
                        ('5 years','5 years'),
                        ('6 years','6 years'),
                        ('7 years','7 years'),
                        ('8+ years','8+ years')
                        ])
    qualification =SelectField('Qualification', 
                choices=[('Certificate','Certificate'),
                        ('Diploma','Diploma'),
                        ('Dergree Bachelor','Dergree Bachelor'),
                        ("Master's Degree","Master's Degree")])

    min_salary = IntegerField('Min', validators=[DataRequired()])
    max_salary = IntegerField('Max', validators=[DataRequired()])
    full_address = StringField('Full Address', validators=[DataRequired()])

    submit = SubmitField('Post a Job')

class userAddressForm(FlaskForm):
    country = StringField('Country', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    zip_code = IntegerField('Zip Code', validators=[DataRequired()])
    submit = SubmitField("Update")

class userSocialForm(FlaskForm):
    website = URLField("Website",validators=[url()])
    facebook = URLField("Facebook",validators=[url()])
    linkedin = URLField("Linkedin",validators=[url()])
    google = URLField("Google",validators=[url()])
    twitter = URLField("Twitter",validators=[url()])
    submit = SubmitField("Update")


class candidateInfoForm(FlaskForm):
    about = CKEditorField('About', validators=[DataRequired()] )
    experiance = SelectField('Experiance',
            choices=[('Fresh', 'Fresh'),
                    ('< 1 year', '< 1 year'),
                    ('1 year','1 year'),
                    ('2 years','2 years'),
                    ('3 years','3 years'),
                    ('4 years','4 years'),
                    ('5 years','5 years'),
                    ('6 years','6 years'),
                    ('7 years','7 years'),
                    ('8+ years','8+ years')
                    ])
    min_salary = IntegerField('Min Salary', validators=[DataRequired()])
    qualification = SelectField('Qualification', 
                choices=[('Cirtificate','Cirtificate'),
                        ('Diploma','Diploma'),
                        ('Dergree Bachelor','Dergree Bachelor'),
                        ("Master's Degree","Master's Degree")])
    gender = RadioField(u'Gender', 
                choices=[('Female', 'Female'), 
                            ('Male', 'Male'),
                            ], validators=[DataRequired()])
    birth_date = DateField('Birth Date',format='%Y-%m-%d')
    submit = SubmitField("Update")
class ResumeForm(FlaskForm):
    resume = FileField('Resume',validators=[FileRequired('File was empty!')])
    submit = SubmitField("Submit")

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class searchForm(FlaskForm):
    search = StringField('Search', validators=[DataRequired()])


class EmployerInfoForm(FlaskForm):
    about = CKEditorField('About', validators=[DataRequired()])
    submit = SubmitField('Update')

class ContactForm(FlaskForm):
    name= StringField('Your Name', validators=[DataRequired()])
    subject = StringField('Subject', validators=[DataRequired()])
    email = StringField('Your Email', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    message = CKEditorField('Message', validators=[DataRequired()])
    submit = SubmitField('SUBMIT')
