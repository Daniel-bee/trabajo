import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_msearch import Search
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_ckeditor import CKEditor


app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
ckeditor = CKEditor(app)
app.config['CKEDITOR_HEIGHT'] = 190

db = SQLAlchemy(app)
search = Search()
search.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'signin'
login_manager.login_message_category = 'info'

app.config['MAIL_SERVER'] = 'smtp.office365.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')


mail = Mail(app)

from . import route