"""
    THIS MODULE CONTAIN ALL SITE ROUTES
"""
from crypt import methods
import os
import secrets
from datetime import datetime
from PIL import Image
from flask import render_template, url_for, redirect, flash, request
from trabajo import app, db, bcrypt, mail
from flask_mail import Message
from .models import (EmployerInfo, User, JobPost, UserSocial,
                UserLocation, CandidateInfo,
                EmployerFollower, JobApply, JobBookmark, EmployerView)
from .forms import (candidateForm,
            candidateUpdateForm, employerUpdateForm,
            employerForm, chnagePasswordForm, jobPostForm, searchForm,
            userLoginForm, userAddressForm, userSocialForm,
            candidateInfoForm, RequestResetForm, ResetPasswordForm,
            searchForm, EmployerInfoForm, ContactForm, ResumeForm)
from flask_login import login_user, current_user, logout_user, login_required


def getUser(userid):
    user = User.query.filter_by(id=userid).first()
    if user:
        return user
    return False

@app.route('/')
@app.route('/home')
def home():
    """
        home route: list all jobs Job posts
        render >> home.html
    """
    page = request.args.get('page', 1, type=int)
    jobposts = JobPost.query.order_by(JobPost.created_at.desc()).paginate(page=page, per_page=7)
    return render_template('home.html', title="Home", jobposts=jobposts)

@app.context_processor
def context():
    form = searchForm()
    sidemenu = {
        'fulltime': JobPost.query.filter_by(job_type='Full Time').count(),
        'freelance': JobPost.query.filter_by(job_type='Freelance').count(),
        'parttime': JobPost.query.filter_by(job_type='Part Time').count(),
        'internship': JobPost.query.filter_by(job_type='Internship').count(),
        'remote': JobPost.query.filter_by(work_from=1).count(),
        'temporary': JobPost.query.filter_by(job_type='Temporary').count(),

    }
    return dict(form=form, sidemenu=sidemenu)

@app.route('/search_jobs', methods=['GET', 'POST']) 
def searchJobs():
    form = searchForm()
    page = request.args.get('page', 1, type=int)
    keyword = form.search.data
    if not keyword:
        page = request.args.get('page', 1, type=int)
        jobposts = JobPost.query.order_by(JobPost.created_at.desc()).paginate(page=page, per_page=7)
        return render_template('home.html',jobposts=jobposts, form=form)
    jobposts = JobPost.query
    if form.validate_on_submit():
        post = jobposts.msearch(keyword).all()
        if not post:
            flash("We're sorry. We were not able to find a match.", 'warning')
        else:
            jobposts = jobposts.msearch(keyword).paginate(page=page, per_page=7)
    else:
        jobposts = jobposts.msearch(keyword).paginate(page=page, per_page=7)
 
    return render_template('home.html',jobposts=jobposts, form=form)



def save_image(form_picture):
    random_hex = secrets.token_hex(8)
    _, file_ext = os.path.splitext(form_picture.filename)
    picture_file_name = random_hex + file_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_file_name)
    
    output_size = (125, 125)
    resized_image = Image.open(form_picture)
    resized_image.thumbnail(output_size)
    resized_image.save(picture_path)

    return picture_file_name

def saveResume(resume):
    random_hex = secrets.token_hex(8)
    _, file_ext = os.path.splitext(resume.filename)
    resume_file_name = random_hex + file_ext
    resume_path = os.path.join(app.root_path, 'static/resume', resume_file_name)
    resume.save(resume_path)
    return resume_file_name

@app.route('/upload_resume/<int:userid>', methods=['POST', 'GET'])
def resumeUpload(userid):
    form = ResumeForm()
    candidate = CandidateInfo.query.filter_by(user_id=userid).first()
    resume = ''
    if form.validate_on_submit():
        if candidate:
            if candidate.resume:
                os.remove(os.path.join(app.root_path, 'static/resume', candidate.resume))
                candidate.resume = saveResume(form.resume.data)
                candidate.updated_at = datetime.utcnow()
            else:
                candidate.resume = saveResume(form.resume.data)
                candidate.updated_at = datetime.utcnow()
            db.session.commit()
            flash('File uploaded!', 'success')
            return redirect(url_for('resumeUpload', userid=current_user.id))
    if request.method == 'GET':
        resume = candidate.resume
    return render_template('candidate/resume.html',title="Resume", resume=resume, page="candidateProfile", form=form)

@app.route('/profile_image', methods=['POST'])
def profileImage():
    user = User.query.filter_by(id=current_user.id).first()
    if user:
        if user.image_file not in ['default.jpg']:
            os.remove(os.path.join(app.root_path, 'static/profile_pics', user.image_file))
        image_file = save_image(request.files['image'])
        user.image_file = image_file
        db.session.commit()
    return "hello"


@app.route('/candidate', methods=['GET', 'POST'])
def candidate():
    """
        candidate route >> a route that create a new candidate
        with the role candidate
        render >> candidate/signup.html
    """
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    candidate_Form = candidateForm()
    if candidate_Form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(candidate_Form.password.data).decode('utf8')
        user = User(
            first_name = candidate_Form.first_name.data,
            last_name = candidate_Form.last_name.data,
            email = candidate_Form.email.data,
            phone_number = candidate_Form.phone_number.data,
            password = hash_password,
            role = 'candidate'
        )

        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('signin'))

    return render_template('candidate/signup.html',title="Signup", candidateForm=candidate_Form)


@app.route('/employer', methods=['GET', 'POST'])
def employer():
    """
        employer route >> a route that create a new employer
        with the role employer and unique company name
        render >> employer/signup.html
    """
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    employer_Form = employerForm()
    if employer_Form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(employer_Form.password.data).decode('utf8')
        user = User(
            first_name = employer_Form.first_name.data,
            last_name = employer_Form.last_name.data,
            company_name = employer_Form.company_name.data,
            email = employer_Form.email.data,
            phone_number = employer_Form.phone_number.data,
            password = hash_password,
            role = 'employer'
        )
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('signin'))
    return render_template('employer/signup.html', title="Signup", employerForm=employer_Form)


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    """
        signin route >> all site user to sign in based on their role
        and redirect them to the home page
        render >> auth/signin.html
    """
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = userLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash("Your Email or password is not correct", 'danger')
    return render_template('auth/signin.html', title="Signin", form=form)


@app.route('/changepassword/<int:userid>', methods=['POST', 'GET'])
@login_required
def changePassword(userid):
    page='candidateProfile'
    if current_user.role == 'employer':
        page='employerProfile'
    form = chnagePasswordForm()
    user = User.query.filter_by(id=userid).first()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf8')
        user.password = hash_password
        db.session.commit()
        flash("Your password has been updated!", 'success')
        return redirect(url_for('changePassword', userid=current_user.id))
    return render_template('auth/change_password.html', page=page, form=form)


@app.route('/follower/<int:userid>', methods=['POST', 'GET'])
@login_required
def employerFollower(userid):
    if request.method == 'GET' and current_user.role in ['candidate']:
        check_follower = EmployerFollower.query.filter_by(user_id=current_user.id, employer_id=userid).first()
        if not check_follower:
            follow = EmployerFollower(
                user_id = current_user.id,
                employer_id = userid
            )
            db.session.add(follow)
            db.session.commit()
    return redirect(url_for('employerProfileDetail', userid=userid))

@app.route('/apply/<int:jobid>', methods=['POST', 'GET'])
@login_required
def jobApply(jobid):
    if request.method == 'GET' and current_user.role in ['candidate']:
        check_application = JobApply.query.filter_by(user_id=current_user.id, job_id=jobid).first()
        if not check_application:
            apply = JobApply(
                job_id = jobid,
                user_id = current_user.id
            )
            db.session.add(apply)
            db.session.commit()
    return redirect(url_for('jobdetail', postid=jobid))


@app.route('/reject/<int:jobid>', methods=['POST', 'GET'])
@login_required
def jobReject(jobid):
    if request.method == 'GET' and current_user.role in ['candidate']:
        check_application = JobApply.query.filter_by(user_id=current_user.id, job_id=jobid).first()
        if check_application:
            db.session.delete(check_application)
            db.session.commit()
    return redirect(url_for('jobdetail', postid=jobid))


@app.route('/bookmark/<int:jobid>', methods=['POST', 'GET'])
@login_required
def jobBookmark(jobid):
    if request.method == 'GET' and current_user.role in ['candidate']:
        check_bookmark = JobBookmark.query.filter_by(user_id=current_user.id, job_id=jobid).first()
        if not check_bookmark:
            bookmark = JobBookmark(
                job_id = jobid,
                user_id = current_user.id
            )
            db.session.add(bookmark)
            db.session.commit()
    return redirect(url_for('home'))

@app.route('/bookmark_reject/<int:jobid>', methods=['POST', 'GET'])
@login_required
def jobRejectBookmark(jobid):
    if request.method == 'GET' and current_user.role in ['candidate']:
        bookmark = JobBookmark.query.filter_by(user_id=current_user.id, job_id=jobid).first()
        if bookmark:
            db.session.delete(bookmark)
            db.session.commit()
    return redirect(url_for('home'))


@app.route('/unfollower/<int:userid>', methods=['POST', 'GET'])
@login_required
def employerUnfollow(userid):
    if request.method == 'GET' and current_user.role in ['candidate']:
        check_follower = EmployerFollower.query.filter_by(user_id=current_user.id, employer_id=userid).first()
        if check_follower:
            db.session.delete(check_follower)
            db.session.commit()
    return redirect(url_for('employerProfileDetail', userid=userid))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/candidateProfile/<int:userid>', methods=['GET', 'POST'])
@login_required
def candidateProfile(userid):
    """
        Candidate: Basic profile update
    """
    user = User.query.get_or_404(userid)
    form = candidateUpdateForm()
    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        user.phone_number = form.phone_number.data
        db.session.commit()
        flash('Profile updated', 'success')
        return redirect(url_for('candidateProfile', userid=current_user.id))
    elif request.method == 'GET':
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
        form.email.data = user.email
        form.phone_number.data = user.phone_number

    return render_template('candidate/profile.html', page='candidateProfile', form=form)


@app.route('/profile_detail/<int:userid>', methods=['GET', 'POST'])
@login_required
def candidateProfileDetail(userid):
    form = candidateInfoForm()
    candidate_info = CandidateInfo.query.filter_by(user_id=userid).first()
    skill_list = request.form.getlist('skill[]')
    skill_str = ','.join(map(str, skill_list))
    if request.method == 'POST' and candidate_info is None:
        if form.validate_on_submit(): 
            candidate = CandidateInfo(
                experiance = form.experiance.data,
                min_salary = form.min_salary.data,
                gender = form.gender.data,
                education_level = form.qualification.data,
                skill = skill_str,
                about = form.about.data,
                birth_date = form.birth_date.data,
                user = current_user
            )
            db.session.add(candidate)
            db.session.commit()
            flash('Profile updated', 'success')
            return redirect(url_for('candidateProfileDetail', userid=current_user.id))
    elif form.validate_on_submit():
        candidate_info.experiance = form.experiance.data
        candidate_info.min_salary = form.min_salary.data
        candidate_info.gender = form.gender.data
        candidate_info.education_level = form.qualification.data
        candidate_info.about = form.about.data
        candidate_info.skill = skill_str
        candidate_info.birth_date = form.birth_date.data
        db.session.commit()
        flash('Profile updated', 'success')
        return redirect(url_for('candidateProfileDetail', userid=current_user.id))
    elif request.method == 'GET' and candidate_info not in [None]:
        form.experiance.data = candidate_info.experiance
        form.min_salary.data = candidate_info.min_salary
        form.gender.data = candidate_info.gender
        form.qualification.data = candidate_info.education_level
        form.about.data = candidate_info.about
        form.birth_date.data = candidate_info.birth_date
    skill = ''
    if candidate_info:
        skill = candidate_info.skill

    return render_template('candidate/profile_detail.html', skill=skill, page='candidateProfile', form=form)


@app.route('/employerProfile/<int:userid>', methods=['GET', 'POST'])
@login_required
def employerProfile(userid):
    """
        Employer: Basic info update
    """
    user = User.query.get_or_404(userid)
    form = employerUpdateForm()

    location = userAddressForm()
    social = userSocialForm()

    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.company_name = form.company_name.data
        user.email = form.email.data
        user.phone_number = form.phone_number.data
        db.session.commit()
        return redirect(url_for('employerProfile', userid=current_user.id))
    elif request.method == 'GET':
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
        form.company_name.data = user.company_name
        form.email.data = user.email
        form.phone_number.data = user.phone_number
    return render_template('employer/profile.html', page='employerProfile', form=form, location=location, social=social)


@app.route('/usersocial/<int:userid>', methods=['GET', 'POST'])
@login_required
def userSocial(userid):
    if current_user.role == 'candidate':
        page = 'candidateProfile'
    else:
        page='employerProfile'

    social = userSocialForm()
    socialLinks = UserSocial.query.filter_by(user_id=userid).first()
    
    if request.method == 'POST' and socialLinks is None:
         if social.validate_on_submit():
            links = UserSocial(
                website = social.website.data,
                facebook = social.facebook.data,
                linkedin = social.linkedin.data,
                twitter = social.twitter.data,
                google = social.google.data,
                user = current_user
            )
            db.session.add(links)
            db.session.commit()
            flash('Social linkes updated!', 'success')
            return redirect(url_for('userSocial', userid=current_user.id))
    elif social.validate_on_submit():
        socialLinks.website = social.website.data
        socialLinks.facebook = social.facebook.data
        socialLinks.linkedin = social.linkedin.data
        socialLinks.twitter = social.twitter.data
        socialLinks.google = social.google.data
        db.session.commit()
        flash('Social links updated!', 'success')
        return redirect(url_for('userSocial', userid=current_user.id))
    elif request.method == 'GET' and socialLinks not in [None]:
        social.website.data = socialLinks.website
        social.facebook.data = socialLinks.facebook
        social.linkedin.data = socialLinks.linkedin
        social.twitter.data = socialLinks.twitter
        social.google.data = socialLinks.google
    
    return render_template('userinfo/social_link.html', page=page, social=social)


@app.route('/useraddress/<int:userid>', methods=['GET', 'POST'])
@login_required
def userAddress(userid):
    if current_user.role == 'candidate':
        page = 'candidateProfile'
    else:
        page='employerProfile'
    # location form
    location = userAddressForm()
    #check if the users address exist
    user_location = UserLocation.query.filter_by(user_id=userid).first()
    if request.method == 'POST' and user_location is None:
        if location.validate_on_submit():
            address = UserLocation(
                country = location.country.data,
                state = location.state.data,
                city = location.city.data,
                zip_code = location.zip_code.data,
                user = current_user
            )
            db.session.add(address)
            db.session.commit()
            flash('Address updated', 'success')
            return redirect(url_for('userAddress', userid=current_user.id))
    elif location.validate_on_submit():
        user_location.country = location.country.data
        user_location.state = location.state.data
        user_location.city = location.city.data
        user_location.zip_code = location.zip_code.data
        db.session.commit()
        flash('Address updated', 'success')
        return redirect(url_for('userAddress', userid=current_user.id))
    elif request.method == "GET" and user_location not in [None]:
        location.country.data = user_location.country
        location.state.data = user_location.state
        location.city.data = user_location.city
        location.zip_code.data = user_location.zip_code
    return render_template('userinfo/address.htm', page=page, location=location)


@app.route('/jobpost', methods=['GET', 'POST'])
@login_required
def jobpost():
    form = jobPostForm()
    
    if form.validate_on_submit():
        skill_list = request.form.getlist('skill[]')
        skill_str = ','.join(map(str, skill_list))
        remote = 0
        if request.form.get('remotejob'):
            remote = int(request.form.get('remotejob'))
        jobpost = JobPost(
                job_title= form.job_title.data, 
                job_description = form.job_description.data,
                job_type = form.job_type.data,
                experiance = form.experiance.data,
                gender = form.gender.data,
                full_address = form.full_address.data,
                required_skill = skill_str,
                qualification = form.qualification.data,
                deadline = form.deadline.data,
                work_from = remote,
                min_salary = form.min_salary.data,
                max_salary = form.max_salary.data,
                user = current_user
        )
        db.session.add(jobpost)
        db.session.commit()
        flash('Your post has been created successfully!', 'success')
        return redirect(url_for('home'))
       
    return render_template('jobs/jobpost.html', page='employerProfile', form=form)

@app.route('/job_update_form/<int:jobid>', methods=['GET', 'POST'])
@login_required
def jobUpdateForm(jobid):
    form = jobPostForm()
    jobpost = JobPost.query.filter_by(id=jobid).first()
    if request.method == 'GET':
        form.job_title.data = jobpost.job_title
        form.job_description.data = jobpost.job_description
        form.job_type.data = jobpost.job_type
        form.experiance.data = jobpost.experiance
        form.gender.data = jobpost.gender
        form.full_address.data = jobpost.full_address
        form.qualification.data = jobpost.qualification
        form.deadline.data = jobpost.deadline
        form.min_salary.data = jobpost.min_salary
        form.max_salary.data = jobpost.max_salary
    skill = ''
    if jobpost:
        skill = jobpost.required_skill
    return render_template('jobs/job_update.html', skill=skill, jobpost=jobpost, page='employerProfile', form=form)

@app.route('/jobupdate/<int:jobid>', methods=['GET', 'POST'])
@login_required
def jobUpdate(jobid):
    form = jobPostForm()
    jobpost = JobPost.query.filter_by(id=jobid).first()
    if form.validate_on_submit():
        skill_list = request.form.getlist('skill[]')
        skill_str = ','.join(map(str, skill_list))
        remote = 0
        if request.form.get('remotejob'):
            remote = int(request.form.get('remotejob'))
        if jobpost:
            jobpost.job_title = form.job_title.data
            jobpost.job_description = form.job_description.data
            jobpost.job_type = form.job_type.data
            jobpost.experiance = form.experiance.data
            jobpost.gender = form.gender.data
            jobpost.full_address = form.full_address.data
            jobpost.required_skill = skill_str
            jobpost.qualification = form.qualification.data
            jobpost.deadline = form.deadline.data
            jobpost.work_from = remote
            jobpost.min_salary = form.min_salary.data
            jobpost.max_salary = form.max_salary.data
            jobpost.user = current_user
            db.session.commit()
            flash('Your post has been updated successfully!', 'success')

    return redirect(url_for('jobUpdateForm', jobid=jobpost.id))

@app.route('/jobdelete/<int:jobid>', methods=['GET', 'POST'])
@login_required
def jobDelete(jobid):
    jobpost = JobPost.query.filter_by(id=jobid).first()
    job_application = JobApply.query.filter_by(job_id=jobid).all()
    if jobpost:
        db.session.delete(jobpost)
        if job_application:
            for application in job_application:
                db.session.delete(application)
        db.session.commit()
        flash('Your post has been deleted successfully!', 'success')
    return redirect(url_for('manageJobs'))


@app.route('/company_job_post/<string:companyName>', methods=['GET', 'POST'])
def companyJobPost(companyName):
    employer = User.query.filter_by(company_name=companyName).first()
    if employer:
        page = request.args.get('page', 1, type=int)
        jobposts = JobPost.query.filter_by(employer_id=employer.id).order_by(JobPost.created_at.desc()).paginate(page=page, per_page=7)
        
    return render_template('jobs/company_post.html', jobposts=jobposts, employerName=employer.company_name)


def countApplicant(jobid):
    applicant = JobApply.query.filter_by(job_id=jobid).all()
    if applicant:
        return len(applicant)
    return 0

@app.route('/manageJobs')
@login_required
def manageJobs():
    jobposts = JobPost.query.filter_by(employer_id=current_user.id).order_by(JobPost.created_at.desc()).all()
    now = datetime.now()
    todayWithoutTime = now.date()
    if current_user.role == 'employer':
        posts = JobPost.query.filter_by(employer_id=current_user.id).all()
        active_jobs = 0
        for post in posts:
            deadline =  post.deadline.date()
            current_datetime = datetime.now()
            today = current_datetime.date()
            if deadline > today:
                active_jobs += 1
    employer = {
        'total_follower': EmployerFollower.query.filter_by(employer_id=current_user.id).count(),
        'total_view': EmployerView.query.filter_by(employer_id=current_user.id).count(),
        'active_jobs': active_jobs,
        'today': todayWithoutTime,
        'count_applicant': countApplicant
    }
    return render_template('jobs/manage_jobs.html', page='employerProfile', jobposts=jobposts, employer=employer)

def checkApplication(jobid, candidate_id):
    applicant = JobApply.query.filter_by(job_id=jobid, user_id=candidate_id).first()
    if applicant:
        return True
    return False


@app.route('/jobdetail/<int:postid>')
def jobdetail(postid):
    jobpost = JobPost.query.get_or_404(postid)
    job_applicant= {
        'count': countApplicant,
        'id': JobApply.query.filter_by(job_id=postid).all(),
        'info': getUser
    }
    return render_template('jobs/jobdetails.html', jobpost=jobpost, job_applicant=job_applicant, application=checkApplication)


def socialLink(userid):
    employer = UserSocial.query.filter_by(user_id=userid).first()
    if employer:
        return employer
    return 0

@app.route('/employerlist')
def employerList():
    page = request.args.get('page', 1, type=int)
    employer = {
        'profile': User.query.filter_by(role='employer').paginate(page=page, per_page=16),
        'link': socialLink
    }
    return render_template('employer/employer_list.html', employer=employer)

@app.route('/search_employers', methods=['GET', 'POST']) 
def searchEmployer():
    form = searchForm()
    page = request.args.get('page', 1, type=int)
    keyword = form.search.data
    if not keyword:
        return redirect(url_for('employerList'))
    users = User.query
    if form.validate_on_submit():
        post = users.msearch(keyword).all()
        if not post:
            flash("We're sorry. We were not able to find a match.", 'warning')
        else:
            users = users.msearch(keyword).paginate(page=page, per_page=16)
    else:
        users = users.msearch(keyword).paginate(page=page, per_page=16)
    employer = {
        'profile': users,
        'link':socialLink
    }
    return render_template('employer/employer_list.html', employer=employer)


@app.route('/employerdetail/<int:userid>', methods=['GET', 'POST'])
def employerProfileDetail(userid):
    user = User.query.filter_by(id=userid).first()
    if current_user.is_authenticated:
        if current_user.role == 'candidate':
            USER = EmployerView.query.filter_by(user_id=current_user.id).first()
            if not USER:
                create_view = EmployerView(
                    view = 1,
                    employer_id = userid,
                    user_id = current_user.id 
                )
                db.session.add(create_view)
                db.session.commit()

    now = datetime.now()
    todayWithoutTime = now.date()
    posts = JobPost.query.filter_by(employer_id=userid).all()
    active_jobs = 0
    for post in posts:
        deadline =  post.deadline.date()
        current_datetime = datetime.now()
        today = current_datetime.date()
        if deadline > today:
            active_jobs += 1
    employer = {
        'profile': user,
        'address': UserLocation.query.filter_by(user_id=user.id).first(),
        'social': UserSocial.query.filter_by(user_id=user.id).first(),
        'followers':  EmployerFollower.query.filter_by(employer_id=userid).all(),
        'total_follower': EmployerFollower.query.filter_by(employer_id=userid).count(),
        'total_post': JobPost.query.filter_by(employer_id=userid).count(),
        'total_view': EmployerView.query.filter_by(employer_id=userid).count(),
        'active_jobs': active_jobs,
        'today': todayWithoutTime,
        'count_applicant': countApplicant,
        'detail': EmployerInfo.query.filter_by(employer_id=current_user.id).first()
    }

    return render_template('employer/employer_detail.html', employer=employer)

@app.route('/employerInfo/<int:empid>', methods=['GET', 'POST'])
def employerInfo(empid):
    form =EmployerInfoForm()
    employer = EmployerInfo.query.filter_by(employer_id=empid).first()
    if request.method == 'POST' and employer is None:
        if form.validate_on_submit():
            create = EmployerInfo(
                about = form.about.data,
                employer_id = current_user.id
            )
            db.session.add(create)
            db.session.commit()
    elif form.validate_on_submit and employer not in [None]:
            employer.about = form.about.data
            db.session.commit()
    elif request.method == 'GET' and employer not in [None]:
        form.about.data = employer.about
    return render_template('employer/profile_detail.html', page="employerProfile", employer=employer , form=form)

@app.route('/candilist')
def candidateList():
    page = request.args.get('page', 1, type=int)
    candidate = {
        'profile': User.query.filter_by(role='candidate').paginate(page=page, per_page=9),
        'link': socialLink
    }
    return render_template('candidate/candidate_list.html', candidate=candidate)

@app.route('/search_candidate', methods=['GET', 'POST']) 
def searchCandidate():
    form = searchForm()
    page = request.args.get('page', 1, type=int)
    keyword = form.search.data
    if not keyword:
        return redirect(url_for('candidateList'))
    users = User.query.filter_by(role='candidate')
    if form.validate_on_submit():
        post = users.msearch(keyword).all()
        if not post:
            flash("We're sorry. We were not able to find a match.", 'warning')
        else:
            users = users.msearch(keyword).paginate(page=page, per_page=9)
    else:
        users = users.msearch(keyword).paginate(page=page, per_page=9)
    candidate = {
        'profile': users,
        'link': socialLink
    }
    return render_template('candidate/candidate_list.html', candidate=candidate)

@app.route('/candidatedetail/<int:userid>', methods=['GET', 'POST'])
def candidateDetail(userid):
    user = User.query.filter_by(id=userid).first()
    candidate = {
        'profile': user,
        'address': UserLocation.query.filter_by(user_id=user.id).first(),
        'social': UserSocial.query.filter_by(user_id=user.id).first(),
        'detail': CandidateInfo.query.filter_by(user_id=user.id).first()
    }
    return render_template('candidate/candidate_detail.html', candidate=candidate)


@app.route('/review_applicant/<int:userid>/<int:jobid>', methods=['GET', 'POST'])
def reviewApplicant(userid, jobid):
    user = User.query.filter_by(id=userid).first()
    applicant = JobApply.query.filter_by(job_id=jobid, user_id=userid).first()
    candidate = {
        'profile': user,
        'address': UserLocation.query.filter_by(user_id=user.id).first(),
        'social': UserSocial.query.filter_by(user_id=user.id).first(),
        'detail': CandidateInfo.query.filter_by(user_id=user.id).first(),
        'jobid': jobid,
        'application': applicant
    }
    return render_template('employer/review_applicant.html', candidate=candidate)


@app.route('/accept_applicant/<int:userid>/<int:jobid>', methods=['GET', 'POST'])
def acceptApplicant(userid, jobid):
    applicant = JobApply.query.filter_by(job_id=jobid, user_id=userid).first()
    if applicant:
        applicant.status = 1
        db.session.commit()
    return redirect(url_for('reviewApplicant', userid=userid, jobid=jobid))


@app.route('/reject_applicant/<int:userid>/<int:jobid>', methods=['GET', 'POST'])
def rejectApplicant(userid, jobid):
    applicant = JobApply.query.filter_by(job_id=jobid, user_id=userid).first()
    if applicant:
        applicant.status = 2
        db.session.commit()
    return redirect(url_for('reviewApplicant', userid=userid, jobid=jobid))

def appliedJobPostes(jobid):
    post = JobPost.query.filter_by(id=jobid).first()
    if post:
        return post
    return []


@app.route('/delet_applied_jobs/<int:jobid>', methods=['GET', 'POST'])
@login_required
def deleteApplidJobs(jobid):
    job_application = JobApply.query.filter_by(job_id=jobid, user_id=current_user.id).first()
    if job_application:
        db.session.delete(job_application)
        db.session.commit()
        flash('Your post has been deleted successfully!', 'success')
    return redirect(url_for('candidateAppliedJobs', userid=current_user.id))


@app.route('/candidate_applied_jobs/<int:userid>', methods=['GET', 'POST'])
def candidateAppliedJobs(userid):
    applied_jobs = JobApply.query.filter_by(user_id=userid).all()
    candidate = {
        'applied_jobs': applied_jobs,
        'job_post': appliedJobPostes
    }
    return render_template('candidate/applied_jobs.html', page="candidateProfile", candidate=candidate)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='daniel123_86@live.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('signin'))
    return render_template('auth/reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('signin'))
    return render_template('auth/reset_token.html', title='Reset Password', form=form)

def send_contact_email(name, email, phone, subj, message):
    msg = Message('Contact Us',
                  sender='daniel123_86@live.com',
                  recipients=['obedamoako92@gmail.com'])
    msg.body = f"""
Name: {name}
Subject: {subj}
Email: {email}
Message: {message}
Phone: {phone}
"""
    mail.send(msg)


@app.route('/contactus', methods=["POST",'GET'])
def contactus():
    form = ContactForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        phone = form.phone_number.data
        sub = form.subject.data
        message = form.message.data
        send_contact_email(name, email, phone, sub, message)
        flash('Thank you for getting in touch! We appreciate you contacting us TRABAJO.','success')
    return render_template('contactus.html', title='Contact Us', form=form)

@app.route('/aboutus')
def aboutus():
    return render_template('about.html', title='About Us')