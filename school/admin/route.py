from flask import render_template, flash, redirect, url_for, session,request,current_app
from flask_mail import Message
from school import app, db, bcrypt, mail,photos
from flask_login import login_user,logout_user
from datetime import datetime
from .forms import RegisterAdmin,LoginAdmin, VerificationForm,BlogPost
from .models import Admin_Register,SchoolFee,Category,Post
from school.student.models import Programme,Faculty,Department,Sex,Student_Register,Course,Level,Session, StudentCourse,Payment
from school.student.forms import AddCourseForm
import random
import string
import secrets
import os

def send_verification_email(user_email, verification_code):
    with app.app_context():
        msg = Message('Email Verification',
                      recipients=[user_email],
                      body=f"Your verification code is {verification_code}.",
                      sender=app.config['MAIL_DEFAULT_SENDER'])
        mail.send(msg)

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'username' not in session:
        flash('Please Login First','danger')
        return redirect(url_for('admin_login'))
    return render_template('admin/admin_dashboard.html')


@app.route('/admin_register',methods=['POST','GET'])
def admin_register():
    form = RegisterAdmin()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        name = form.name.data
        username = form.username.data
        email = form.email.data
        
        # Generate a 6-digit random verification code
        verification_code = ''.join(random.choices(string.digits, k=6))
        
        # Create a new student register entry and set verification code
        register = Admin_Register(name=name,username=username,email=email,password=hashed_password,verification_code=verification_code)  # Set verification code
        db.session.add(register)
        db.session.commit()  # Commit with verification code

        flash('Account registered successfully', 'success')

        # Send verification email
        send_verification_email(register.email, verification_code)

        flash('Account created! Please check your email for the verification code.', 'success')
        session['email'] = register.email  # Store email in session for later verification
        return redirect(url_for('verify_email'))

    else:
        if form.errors:
            print('form errors:', form.errors)

    return render_template('admin/admin_register.html', form=form)


@app.route('/verify', methods=['GET', 'POST'])
def verify_email():
    form = VerificationForm()
    if 'email' not in session:
        flash('No registration process found. Please register first.', 'warning')
        return redirect(url_for('admin_register'))

    if form.validate_on_submit():
        # Retrieve the user by email from session
        admin_reg = Admin_Register.query.filter_by(email=session['email']).first()
        if admin_reg and admin_reg.verification_code == form.code.data:
            admin_reg.verified = True  # Mark the account as verified
            admin_reg.verification_code = None  # Clear the verification code after verification
            db.session.commit()
            flash('Your account has been verified!', 'success')
            session.pop('email', None)  # Remove email from session
            return redirect(url_for('admin_login'))
        else:
            flash('Invalid verification code. Please try again.', 'danger')

    return render_template('/admin/verify_email.html', form=form)


@app.route('/admin/resend_code', methods=['GET'])
def resend_verification_codes():
    if 'email' not in session:
        flash('No registration process found. Please register first.', 'warning')
        return redirect(url_for('admin_register'))

    # Retrieve the student record from the session's email
    admin_reg = Admin_Register.query.filter_by(email=session['email']).first()

    if not admin_reg:
        flash('Account not found. Please register first.', 'danger')
        return redirect(url_for('admin_register'))

    if admin_reg.verified:
        flash('Your account is already verified!', 'info')
        return redirect(url_for('admin_login'))

    # Generate a new 6-digit random verification code
    new_verification_code = ''.join(random.choices(string.digits, k=6))

    # Update the verification code in the database
    admin_reg.verification_code = new_verification_code
    db.session.commit()

    # Resend verification email
    send_verification_email(admin_reg.email, new_verification_code)

    flash('A new verification code has been sent to your email.', 'success')
    return redirect(url_for('verify_email'))



@app.route('/admin_login',methods=['POST','GET'])
def admin_login():
    form=LoginAdmin()
    if form.validate_on_submit():
        admin=Admin_Register.query.filter_by(username=form.username.data).first()
        if admin:
            if bcrypt.check_password_hash(admin.password,form.password.data):
                login_user(admin)
                session['username']=admin.username
                flash('Login Successfully','success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Wrong Password Try Again','danger')
        else:
            flash('That User Does Not Exist','danger')
    return render_template('/admin/admin_login.html',form=form)


@app.route('/admin/logout')
def admin_logout():
    if 'username' not in session:
        flash('please Login first','danger')
        return redirect(url_for('customer_login'))
    logout_user()
    return redirect(url_for('admin_login'))


@app.route('/admin/view_student')
def view_student():
    if 'username' not in session:
        flash('Please Login First','danger')
        return redirect(url_for('admin_login'))
    stud=Student_Register.query.all()
    return render_template('/admin/view_student.html',stud=stud)


@app.route('/admin/delete_student/<int:id>',methods=['POST','GET'])
def delete_student(id):
    if 'username' not in session:
        flash('Please Login First','danger')
        return redirect(url_for('admin_login'))
    delete=Student_Register.query.get_or_404(id)
    # Check for linked students before attempting to delete the student
    linked_school = StudentCourse.query.filter_by(student_register_id=id).count()

    if linked_school > 0:
        # There are student linked to this student course, so do not delete
        flash(f'The student {delete.last_name} cannot be deleted because it is linked to existing student.', 'warning')
        return redirect(url_for('view_student'))
    
    # Proceed with deletion if no linked products
    if request.method == 'POST':
        try:
            db.session.delete(delete)
            db.session.commit()
            flash(f'Student {delete.name} has been deleted successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting student: {str(e)}', 'danger')

    return redirect(url_for('view_student'))


@app.route('/admin/programme',methods=['POST','GET'])
def programme():
    if 'username' not in session:
        flash('Please Login First','danger')
        return redirect(url_for('admin_login'))
    if request.method=='POST':
        prog=request.form.get('prog')
        prog=Programme(name=prog)
        db.session.add(prog)
        db.session.commit()
        flash('Programme Added Successfully','success')
    return render_template('/admin/programme.html')

@app.route('/admin/view_programme')
def view_programme():
    if 'username' not in session:
        flash('Please Login First','danger')
        return redirect(url_for('admin_login'))
    prog=Programme.query.all()
    return render_template('/admin/view_programme.html',prog=prog)

@app.route('/admin/edit_programme/<int:id>',methods=['POST','GET'])
def edit_programme(id):
    if 'username' not in session:
        flash('Please Login First','danger')
        return redirect(url_for('admin_login'))
    progs=Programme.query.get_or_404(id)
    if request.method=='POST':
        progs.name=request.form.get('pog')
        db.session.commit()
        flash(f'Programme {progs.name} updated successfully','success')
        return redirect(url_for('view_programme'))
    return render_template('/admin/edit_programme.html',progs=progs)


@app.route('/admin/deleteprogramme/<int:id>',methods=['POST','GET'])
def delete_programme(id):
    if 'username' not in session:
        flash('Please Login First','danger')
        return redirect(url_for('admin_login'))
    delete=Programme.query.get_or_404(id)
    # Check for linked products before attempting to delete the category
    linked_school = Student_Register.query.filter_by(programme_id=id).count()

    if linked_school > 0:
        # There are products linked to this category, so do not delete
        flash(f'The Programme {delete.name} cannot be deleted because it is linked to existing student.', 'warning')
        return redirect(url_for('view_programme'))
    
    # Proceed with deletion if no linked products
    if request.method == 'POST':
        try:
            db.session.delete(delete)
            db.session.commit()
            flash(f'Programme {delete.name} has been deleted successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting category: {str(e)}', 'danger')

    return redirect(url_for('view_programme'))


@app.route('/admin/faculty',methods=['POST','GET'])
def faculty():
    if 'username' not in session:
        flash('Please Login First','danger')
        return redirect(url_for('admin_login'))
    if request.method=='POST':
        falc=request.form.get('falc')
        falc=Faculty(name=falc)
        db.session.add(falc)
        db.session.commit()
        flash('Faculty Added Successfully','success')
    return render_template('/admin/faculty.html')


@app.route('/admin/view_faculty')
def view_faculty():
    if 'username' not in session:
        flash('Please Login First','danger')
        return redirect(url_for('admin_login'))
    facult=Faculty.query.all()
    return render_template('/admin/view_faculty.html',facult=facult)


@app.route('/admin/edit_faculty/<int:id>',methods=['POST','GET'])
def edit_faculty(id):
    if 'username' not in session:
        flash('Please Login First','danger')
        return redirect(url_for('admin_login'))
    falc=Faculty.query.get_or_404(id)
    if request.method=='POST':
        falc.name=request.form.get('fal')
        db.session.commit()
        flash(f'Programme {falc.name} updated successfully','success')
        return redirect(url_for('view_faculty'))
    return render_template('/admin/edit_faculty.html',falc=falc)


@app.route('/admin/deletefaculty/<int:id>',methods=['POST','GET'])
def delete_faculty(id):
    if 'username' not in session:
        flash('Please Login First','danger')
        return redirect(url_for('admin_login'))
    facult = Faculty.query.get_or_404(id)
    
    # Check for linked products before attempting to delete the category
    linked_school = Student_Register.query.filter_by(faculty_id=id).count()

    if linked_school > 0:
        # There are products linked to this category, so do not delete
        flash(f'The Faculty {facult.name} cannot be deleted because it is linked to existing products.', 'warning')
        return redirect(url_for('view_faculty'))
    
    # Proceed with deletion if no linked products
    if request.method == 'POST':
        try:
            db.session.delete(facult)
            db.session.commit()
            flash(f'Faculty {facult.name} has been deleted successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting category: {str(e)}', 'danger')

    return redirect(url_for('view_faculty'))


@app.route('/admin/department',methods=['POST','GET'])
def department():
    if 'username' not in session:
        flash('Please Login First','danger')
        return redirect(url_for('admin_login'))
    if request.method=='POST':
        depart=request.form.get('depart')
        depart=Department(name=depart)
        db.session.add(depart)
        db.session.commit()
        flash('Department Added Successfully','success')
    return render_template('/admin/department.html')


@app.route('/admin/view_department')
def view_department():
    if 'username' not in session:
        flash('Please Login First','danger')
        return redirect(url_for('admin_login'))
    depart=Department.query.all()
    return render_template('/admin/view_department.html',depart=depart)


@app.route('/admin/edit_department/<int:id>',methods=['POST','GET'])
def edit_department(id):
    if 'username' not in session:
        flash('Please Login First','danger')
        return redirect(url_for('admin_login'))
    depar=Department.query.get_or_404(id)
    if request.method=='POST':
        depar.name=request.form.get('dep')
        db.session.commit()
        flash(f'Programme {depar.name} updated successfully','success')
        return redirect(url_for('view_department'))
    return render_template('/admin/edit_department.html',depar=depar)


@app.route('/admin/deletedepartment/<int:id>',methods=['POST','GET'])
def delete_department(id):
    if 'username' not in session:
        flash('Please Login First','danger')
        return redirect(url_for('admin_login'))
    depar = Department.query.get_or_404(id)
    
    # Check for linked products before attempting to delete the category
    linked_school = Student_Register.query.filter_by(department_id=id).count()

    if linked_school > 0:
        # There are products linked to this category, so do not delete
        flash(f'The Department {depar.name} cannot be deleted because it is linked to existing products.', 'warning')
        return redirect(url_for('view_department'))
    
    # Proceed with deletion if no linked products
    if request.method == 'POST':
        try:
            db.session.delete(depar)
            db.session.commit()
            flash(f'Department {depar.name} has been deleted successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting category: {str(e)}', 'danger')

    return redirect(url_for('view_department'))

@app.route('/admin/sex',methods=['POST','GET'])
def sex():
    if 'username' not in session:
        flash('Please Login First','danger')
        return redirect(url_for('admin_login'))
    if request.method=='POST':
        sex=request.form.get('sex')
        sex=Sex(name=sex)
        db.session.add(sex)
        db.session.commit()
        flash('Sex Added Successfully','success')
    return render_template('/admin/sex.html')

@app.route('/admin/view_sex')
def view_sex():
    if 'username' not in session:
        flash('Please Login First','danger')
        return redirect(url_for('admin_login'))
    vex=Sex.query.all()
    return render_template('/admin/view_sex.html',vex=vex)

@app.route('/admin/edit_sex/<int:id>',methods=['POST','GET'])
def edit_sex(id):
    if 'username' not in session:
        flash('Please Login First','danger')
        return redirect(url_for('admin_login'))
    sexx=Sex.query.get_or_404(id)
    if request.method=='POST':
        sexx.name=request.form.get('segs')
        db.session.commit()
        flash(f'Programme {sexx.name} updated successfully','success')
        return redirect(url_for('view_sex'))
    return render_template('/admin/edit_sex.html',sexx=sexx)

@app.route('/admin/deletesex/<int:id>',methods=['POST','GET'])
def delete_sex(id):
    if 'username' not in session:
        flash('Please Login First','danger')
        return redirect(url_for('admin_login'))
    secx = Sex.query.get_or_404(id)
    
    # Check for linked products before attempting to delete the category
    linked_school = Student_Register.query.filter_by(sex_id=id).count()

    if linked_school > 0:
        # There are products linked to this category, so do not delete
        flash(f'The Gender {secx.name} cannot be deleted because it is linked to existing products.', 'warning')
        return redirect(url_for('view_sex'))
    
    # Proceed with deletion if no linked products
    if request.method == 'POST':
        try:
            db.session.delete(secx)
            db.session.commit()
            flash(f'Category {secx.name} has been deleted successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting category: {str(e)}', 'danger')

    return redirect(url_for('view_sex'))

@app.route('/admin/level',methods=['POST','GET'])
def level():
    if 'username' not in session:
        flash('please Login First','danger')
        return redirect(url_for('admin_login'))
    if request.method=='POST':
        level=request.form.get('level')
        level=Level(name=level)
        db.session.add(level)
        db.session.commit()
        flash('Level Added Successfully','success')
    return render_template('/admin/level.html')

@app.route('/student/view_level')
def view_level():
    if 'username' not in session:
        flash('Please Login First','danger')
        return redirect(url_for('admin_login'))
    lev=Level.query.all()
    return render_template('/admin/view_level.html',lev=lev)


@app.route('/admin/edit_level/<int:id>',methods=['POST','GET'])
def edit_level(id):
    if 'username' not in session:
        flash('Please Login First','danger')
        return redirect(url_for('admin_login'))
    levs=Level.query.get_or_404(id)
    if request.method=='POST':
        levs.name=request.form.get('levs')
        db.session.commit()
        flash(f'Level {levs.name} updated successfully','success')
        return redirect(url_for('view_level'))
    return render_template('/admin/edit_level.html',levs=levs)


@app.route('/admin/deletelevel/<int:id>',methods=['POST','GET'])
def delete_level(id):
    if 'username' not in session:
        flash('Please Login First','danger')
        return redirect(url_for('admin_login'))
    lev = Level.query.get_or_404(id)
    
    # Check for linked products before attempting to delete the category
    linked_school = Student_Register.query.filter_by(level_id=id).count()

    if linked_school > 0:
        # There are products linked to this category, so do not delete
        flash(f'The Gender {lev.name} cannot be deleted because it is linked to existing products.', 'warning')
        return redirect(url_for('view_level'))
    
    # Proceed with deletion if no linked products
    if request.method == 'POST':
        try:
            db.session.delete(lev)
            db.session.commit()
            flash(f'Level {lev.name} has been deleted successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting category: {str(e)}', 'danger')

    return redirect(url_for('view_level'))


@app.route('/admin/session',methods=['POST','GET'])
def sessions():
    if 'username' not in session:
        flash('please Login First','danger')
        return redirect(url_for('admin_login'))
    if request.method=='POST':
        sessions=request.form.get('session')
        sessions=Session(name=sessions)
        db.session.add(sessions)
        db.session.commit()
        flash('Session Added Successfully','success')
    return render_template('/admin/session.html')

@app.route('/admin/view_session')
def view_session():
    if 'username' not in session:
        flash('Please Login First','danger')
        return redirect(url_for('admin_login'))
    sess=Session.query.all()
    return render_template('/admin/view_session.html',sess=sess)

@app.route('/admin/edit_session/<int:id>',methods=['GET','POST'])
def edit_session(id):
    if 'username' not in session:
        flash('Please Login First','danger')
        return redirect(url_for('admin_login'))
    sess=Session.query.get_or_404(id)
    if request.method=='POST':
        sess.name=request.form.get('sess')
        db.session.commit()
        flash(f'Session {sess.name} updated successfully','success')
        return redirect(url_for('view_session'))
    return render_template('/admin/edit_session.html',sess=sess)

@app.route('/admin/deletesession/<int:id>',methods=['POST','GET'])
def delete_session(id):
    if 'username' not in session:
        flash('Please Login First','danger')
        return redirect(url_for('admin_login'))
    sess = Session.query.get_or_404(id)
    
    # Check for linked student before attempting to delete the session
    linked_school = Student_Register.query.filter_by(session_id=id).count()

    if linked_school > 0:
        # There are student linked to this session, so do not delete
        flash(f'The Session {sess.name} cannot be deleted because it is linked to existing student.', 'warning')
        return redirect(url_for('view_session'))
    
    # Proceed with deletion if no linked student
    if request.method == 'POST':
        try:
            db.session.delete(sess)
            db.session.commit()
            flash(f'Session {sess.name} has been deleted successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting session: {str(e)}', 'danger')

    return redirect(url_for('view_session'))

@app.route('/admin/add_course',methods=['POST','GET'])
def add_course():
    if 'username' not in session:
        flash('Please Login First','danger')
        return redirect(url_for('admin_login'))
    form=AddCourseForm()
    if form.validate_on_submit():
        new_course = Course(
            code=form.code.data,
            name=form.name.data,
            credit_hours=form.credit_hours.data
        )
        db.session.add(new_course)
        db.session.commit()
        flash('Course added successfully', 'success')
        return redirect(url_for('add_course'))
    return render_template('/admin/add_course.html',form=form)

@app.route('/admin/view_course')
def view_course():
    if 'username' not in session:
        flash('Please Login First','danger')
        return redirect(url_for('admin_login'))
    cour=Course.query.all()
    return render_template('/admin/view_course.html',cour=cour)


@app.route('/admin/edit_course/<int:id>',methods=['GET','POST'])
def edit_course(id):
    if 'username' not in session:
        flash('Please Login First','danger')
        return redirect(url_for('admin_login'))
    cour=Course.query.get_or_404(id)
    if request.method=='POST':
        cour.name=request.form.get('cour')
        db.session.commit()
        flash(f'Course {cour.name} updated successfully','success')
        return redirect(url_for('view_course'))
    return render_template('/admin/edit_course.html',cour=cour)

@app.route('/admin/deletecourse/<int:id>',methods=['POST','GET'])
def delete_course(id):
    if 'username' not in session:
        flash('Please Login First','danger')
        return redirect(url_for('admin_login'))
    cour = Course.query.get_or_404(id)
    
    # Check for linked student before attempting to delete the session
    linked_school = StudentCourse.query.filter_by(course_id=id).count()

    if linked_school > 0:
        # There are student linked to this StudentCourse, so do not delete
        flash(f'The Course {cour.name} cannot be deleted because it is linked to existing student.', 'warning')
        return redirect(url_for('view_course'))
    
    # Proceed with deletion if no linked student
    if request.method == 'POST':
        try:
            db.session.delete(cour)
            db.session.commit()
            flash(f'Course {cour.name} has been deleted successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting session: {str(e)}', 'danger')

    return redirect(url_for('view_course'))


@app.route('/admin/add_school_fee', methods=['GET', 'POST'])
def add_school_fee():
    if 'username' not in session:
        flash('Please Login First','danger')
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        programme_id = request.form.get('program_id')
        department_id = request.form.get('department_id')
        sessions_id=request.form.get('sessions_id')
        level_id=request.form.get('level_id')
        amount = request.form.get('amount')
        description = request.form.get('description')

        # Validate inputs
        if not programme_id or not department_id or not sessions_id or not level_id or not amount:
            flash("All fields are required.", "error")
            return redirect(url_for('add_school_fee'))

        # Create and save the new school fee record
        new_fee = SchoolFee(
            programme_id=programme_id,
            department_id=department_id,
            session_id=sessions_id,
            level_id=level_id,
            amount=amount,
            description=description,
        )
        db.session.add(new_fee)
        db.session.commit()

        flash("School fee added successfully!", "success")
        return redirect(url_for('add_school_fee'))

    # Fetch all programs and departments for dropdowns
    programs = Programme.query.all()
    departments = Department.query.all()
    sessions=Session.query.all()
    levels=Level.query.all()
    return render_template('admin/add_school_fee.html',programs=programs, departments=departments,sessions=sessions,levels=levels)


@app.route('/admin/view_school_fee')
def view_school_fee():
    if 'username' not in session:
        flash('Please Login First','danger')
        return redirect(url_for('admin_login'))
    schoo=SchoolFee.query.all()
    return render_template('/admin/view_school_fee.html',schoo=schoo)


@app.route('/admin/edit_school_fee/<int:id>',methods=['GET','POST'])
def edit_school_fee(id):
    if 'username' not in session:
        flash('Please Login First')
        return redirect(url_for('admin_login'))
    schfee=SchoolFee.query.get_or_404(id)
    progss=Programme.query.all()
    departss=Department.query.all()
    levss=Level.query.all()
    sesc=Session.query.all()
    prog=request.form.get('prog')
    depart=request.form.get('depart')
    lev=request.form.get('lev')
    sess=request.form.get('sess')
    if request.method=='POST':
        schfee.amount=request.form.get('amt')
        schfee.description=request.form.get('desc')
        schfee.programme_id=prog
        schfee.department_id=depart
        schfee.level_id=lev
        schfee.session_id=sess
        db.session.commit()
        flash(f'School fee updated successfully','success')
        return redirect(url_for('view_school_fee'))
    return render_template('/admin/edit_school_fee.html',schfee=schfee,progss=progss,departss=departss,levss=levss,sesc=sesc)


@app.route('/admin/deleteschool_fee/<int:id>',methods=['POST','GET'])
def delete_school_fee(id):
    if 'username' not in session:
        flash('Please Login First','danger')
        return redirect(url_for('admin_login'))
    sch = SchoolFee.query.get_or_404(id)
    
    # Check for linked student before attempting to delete the session
    linked_school = Payment.query.filter_by(school_fee_id=id).count()

    if linked_school >0:
        # There are student linked to this StudentCourse, so do not delete
        flash(f'The School fee {sch.name} cannot be deleted because it is linked to existing payment.', 'warning')
        return redirect(url_for('view_school_fee'))
    
    # Proceed with deletion if no linked student
    if request.method == 'POST':
        try:
            db.session.delete(sch)
            db.session.commit()
            flash(f'School {sch.amount} has been deleted successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting session: {str(e)}', 'danger')

    return redirect(url_for('view_school_fee'))


@app.route('/admin/category',methods=['POST','GET'])
def category():
    if 'username' not in session:
        flash('Please Login First','danger')
        return redirect(url_for('admin_login'))
    if request.method=='POST':
        cate=request.form.get('cat')
        cate=Category(name=cate)
        db.session.add(cate)
        db.session.commit()
        flash(f'The category {cate.name} is added successfully','success')
    return render_template('/admin/category.html')


@app.route('/admin/view_category')
def view_category():
    if 'username' not in session:
        flash('Please Login First','danger')
        return redirect(url_for('admin_login'))
    cat=Category.query.all()
    return render_template('/admin/view_category.html',cat=cat)

@app.route('/admin/edit_category/<int:id>',methods=['POST','GET'])
def edit_category(id):
    if 'username' not in session:
        flash('Please Login First','danger')
        return redirect(url_for('admin_login'))
    cats=Category.query.get_or_404(id)
    if request.method=='POST':
        cats.name=request.form.get('cats')
        db.session.commit()
        flash(f'Category {cats.name} is updated succesfully','success')
        return redirect(url_for('view_category'))
    return render_template('/admin/edit_category.html',cats=cats)

@app.route('/admin/deletecategory/<int:id>',methods=['POST','GET'])
def delete_category(id):
    if 'username' not in session:
        flash('Please Login First','danger')
        return redirect(url_for('admin_login'))
    dele=Category.query.get_or_404(id)

    # Check for linked category before attempting to delete the session
    linked_category = Post.query.filter_by(category_id=id).count()

    if linked_category >0:
        # There are category linked to this Post, so do not delete
        flash(f'The Category {dele.name} cannot be deleted because it is linked to existing Post.', 'warning')
        return redirect(url_for('view_category'))
    
    # Proceed with deletion if no linked post
    if request.method == 'POST':
        try:
            db.session.delete(dele)
            db.session.commit()
            flash(f'Category {dele.name} has been deleted successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting session: {str(e)}', 'danger')

    return redirect(url_for('view_category'))

@app.route('/admin/create_post', methods=['POST', 'GET'])
def create_post():
    if 'username' not in session:
        flash('Please Login First')
        return redirect(url_for('admin_login'))
    
    categories = Category.query.all()
    categ = request.form.get('category')
    form = BlogPost()
    
    if form.validate_on_submit() and request.method == 'POST':
        title = form.title.data
        content = form.content.data
        category = categ
        pic = photos.save(request.files.get('image'), name=secrets.token_hex(10) + '.')
        date_posted = datetime.now()
        
        # Retrieve the admin's ID based on the username stored in the session
        admin = Admin_Register.query.filter_by(username=session['username']).first()
        if not admin:
            flash('Admin not found', 'danger')
            return redirect(url_for('create_post'))
        
        post = Post(
            title=title,
            content=content,
            category_id=category,
            image=pic,
            author_id=admin.id,  # Use the admin's ID here
            date_posted=date_posted
        )
        db.session.add(post)
        db.session.commit()
        flash('Blog Post Added Successfully', 'success')
        return redirect(url_for('view_post'))
    
    return render_template('/admin/create_post.html', form=form, categories=categories)

@app.route('/admin/view_post')
def view_post():
    if 'username' not in session:
        flash('Please Login First','danger')
        return redirect(url_for('admin_login'))
    pos=Post.query.all()
    return render_template('/admin/view_post.html',pos=pos)


@app.route('/edit_post/<int:id>',methods=['GET','POST'])
def edit_posts(id):
    if 'username' not in session:
        flash('Please Login First','danger')
        return redirect(url_for('admin_login'))
    categories=Category.query.all()
    post=Post.query.get_or_404(id)
    category=request.form.get('category')
    form=BlogPost()
    if  form.validate_on_submit() and request.method=='POST':
        post.title=form.title.data
        post.content=form.content.data
        post.category_id=category
        if request.files.get('image'):
            try:
                os.unlink(os.path.join(current_app.root_path,'static/pictures/' + post.image))
                post.image = photos.save(request.files.get('image'),name=secrets.token_hex(10) + '.')
            except:
                post.image = photos.save(request.files.get('image'),name=secrets.token_hex(10) + '.')
        db.session.commit()
        return redirect(url_for('view_post'))
    elif request.method=='GET':
        form.title.data=post.title
        form.content.data=post.content
    return render_template('/admin/edit_post.html',form=form,post=post,categories=categories)

@app.route('/delete_post/<int:id>',methods=['POST','GET'])
def delete_post(id):
    if 'username' not in session:
        flash('Please login first','danger')
        return redirect(url_for('admin_login'))
    post=Post.query.get_or_404(id)
    if request.method=='POST':
        if request.files.get('image'):
            try:
                os.unlink(os.path.join(current_app.root_path,'static/pictures/' + post.image))
            except Exception as e:
                print(e)
        db.session.delete(post)
        db.session.commit()
    return redirect(url_for('view_post'))
