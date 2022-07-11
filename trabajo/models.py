from trabajo import db, login_manager, app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __searchable__ = ['company_name', 'first_name', 'last_name']
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    email = db.Column(db.String(100), unique=True)
    company_name = db.Column(db.String(20), unique=True)
    phone_number = db.Column(db.String(15), unique=True)
    role = db.Column(db.String(20))
    password = db.Column(db.String(60))
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    job_posts = db.relationship('JobPost', backref='user', lazy=True)
    user_social = db.relationship('UserSocial', backref='user', lazy=True)
    user_location = db.relationship('UserLocation', backref='user', lazy=True)
    candidate_info = db.relationship('CandidateInfo', backref='user', lazy=True)
    bookmarks = db.relationship('JobBookmark', backref='user', lazy=True)
    apply = db.relationship('JobApply', backref='user', lazy=True)
    follower = db.relationship('EmployerFollower', backref='user', lazy=True)
    view = db.relationship('EmployerView', backref='user', lazy=True)
    employer_info = db.relationship('EmployerInfo', backref='user', lazy=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

class EmployerView(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    view = db.Column(db.Integer, default=0)
    employer_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class EmployerFollower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    employer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class JobBookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class JobApply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class UserSocial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    website = db.Column(db.String(100))
    facebook = db.Column(db.String(100))
    linkedin = db.Column(db.String(100))
    twitter = db.Column(db.String(100))
    google = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class UserLocation(db.Model):
    __searchable__ = ['country', 'experiance', 'experiance', 'zip_code']
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(20), nullable=False)
    state = db.Column(db.String(20), nullable=False)
    city = db.Column(db.String(20), nullable=False)
    zip_code = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class CandidateInfo(db.Model):
    __searchable__ = ['education_level','experiance','experiance']
    id = db.Column(db.Integer, primary_key=True)
    experiance = db.Column(db.String(13))
    education_level = db.Column(db.String(30))
    min_salary = db.Column(db.Integer)
    skill = db.Column(db.Text())
    gender = db.Column(db.String(13), nullable=False)
    birth_date = db.Column(db.DateTime)
    about = db.Column(db.Text())
    resume = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class EmployerInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    about = db.Column(db.Text())
    catagory = db.Column(db.Text())
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    employer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class JobPost(db.Model):
    __searchable__ = ['job_title', 'job_description', 'job_type',
                      'qualification', 'min_salary',
                      'max_salary', 'experiance']
    id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String(100), nullable=False)
    job_description = db.Column(db.Text(), nullable=False)
    job_type = db.Column(db.String(13), nullable=False)
    experiance = db.Column(db.String(13), nullable=False)
    qualification = db.Column(db.String(18), nullable=False)
    required_skill = db.Column(db.Text())
    gender = db.Column(db.String(13), nullable=False)
    min_salary = db.Column(db.Integer, nullable=False)
    max_salary = db.Column(db.Integer, nullable=False)
    full_address = db.Column(db.String(60))
    work_from = db.Column(db.Integer, default=0)
    deadline = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    employer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    