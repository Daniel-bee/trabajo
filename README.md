# Trabajo
![Alt text](https://i.ibb.co/kyLcGJH/Screenshot-from-2022-07-11-10-46-31.png)
## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)
* [Features](#features)
* [CodeExample](#codeexample)
* [Screenshots](#screenshots)

## General info
  Trabajo is a Job listing site specific to software industry positions. Candidates can search by job title and location, salary, date posted, and experience level.
## Technologies
Project is created with:
  - Flask 2.1.2
  - Bootstrap 5, HTML, CSS, JavaScript
  - jQuery and Ajax
  - Jinja2 3.1.2
  - Flask-SQLAlchemy 2.5.1
  - WTForms 3.0.1
  - Flask-WTF 1.0.1
  - Flask-Bcrypt 1.0.1
  - Flask-CKEditor 0.4.6
  - bcrypt 3.2.2
  - email-validator 1.2.1
  - Flask-Login 0.6.1
  - Flask-Mail 0.9.1
  - flask-msearch 0.2.9.2
  - itsdangerous 2.0.1
  - phonenumbers 8.12.51
  - Pillow 9.1.1

## setup
To run this project

```
Creating a virtual environment
python3 -m venv .

Activating a virtual environment
. venv/bin/activate

pip3 install -r requirements.txt
python start.py

```
## Features
  - Creating an account as a candidate and Employer
  - Employer: post jobs
  - Candidate: apply for the post
  - Candidate: follow Employers
  - Employer: Accept or reject an applicant
  - Sending email
  - user authentication

## CodeExample
```
route to create new job
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

```
```
route that manage job post
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

```
## Screenshots
![Alt text](https://i.ibb.co/s62Rm94/2.png)

![Alt text](https://i.ibb.co/DMXm45b/1.png)

