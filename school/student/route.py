from school import app,bcrypt,db,mail
from flask import render_template,session,flash,redirect,url_for,request

from school.admin.models import SchoolFee
from .models import Department, Student_Register,Programme,Faculty,Sex,StudentCourse,Course,Level,Session
from .forms import PaymentForm, RegisterStudent,VerificationForm,LoginAdmin,RegisterCourseForm
from flask_mail import Message
from flask_login import login_user,logout_user,current_user,login_required
import random
import string
import stripe

publishable_key= app.config['STRIPE_SECRET_KEY']

stripe.api_key= app.config['STRIPE_SECRET_KEY']


def send_verification_email(user_email, verification_code):
    with app.app_context():
        msg = Message('Email Verification',
                      recipients=[user_email],
                      body=f"Your verification code is {verification_code}.",
                      sender=app.config['MAIL_DEFAULT_SENDER'])
        mail.send(msg)

@app.route('/student_register',methods=['POST','GET'])
def student_register():
    programme=Programme.query.all()
    faculty=Faculty.query.all()
    department=Department.query.all()
    sex=Sex.query.all()
    form = RegisterStudent()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        first_name = form.first_name.data
        last_name = form.last_name.data
        other_name = form.other_name.data
        programme = request.form.get('programme')
        faculty = request.form.get('faculty')
        department = request.form.get('department')
        sex = request.form.get('sex')
        date_of_birth = form.date_of_birth.data
        email = form.email.data
        phone_no = form.phone_no.data
        residential_address = form.residential_address.data
        place_of_birth = form.place_of_birth.data
        state_of_origin = form.state_of_origin.data
        local_govt_area = form.local_govt_area.data
        
        # Generate a 6-digit random verification code
        verification_code = ''.join(random.choices(string.digits, k=6))
        
        # Create a new student register entry and set verification code
        register = Student_Register(first_name=first_name,
                                    last_name=last_name,
                                    other_name=other_name,
                                    programme_id=programme,
                                    faculty_id=faculty,
                                    department_id=department,
                                    sex_id=sex,
                                    date_of_birth=date_of_birth,
                                    email=email,
                                    phone_no=phone_no,
                                    residential_address=residential_address,
                                    place_of_birth=place_of_birth,
                                    state_of_origin=state_of_origin,
                                    local_govt_area=local_govt_area,
                                    password=hashed_password,
                                    verification_code=verification_code)  # Set verification code

        db.session.add(register)
        db.session.commit()  # Commit with verification code

        flash('Account registered successfully', 'success')

        # Send verification email
        send_verification_email(register.email, verification_code)

        flash('Account created! Please check your email for the verification code.', 'success')
        session['email'] = register.email  # Store email in session for later verification
        return redirect(url_for('verify_emails'))

    else:
        if form.errors:
            print('form errors:', form.errors)

    return render_template('student/register.html', form=form, programme=programme, faculty=faculty, department=department, sex=sex)


@app.route('/student/verify', methods=['GET', 'POST'])
def verify_emails():
    form = VerificationForm()
    if 'email' not in session:
        flash('No registration process found. Please register first.', 'warning')
        return redirect(url_for('student_register'))

    if form.validate_on_submit():
        # Retrieve the user by email from session
        student_reg = Student_Register.query.filter_by(email=session['email']).first()
        
        print(f"Input Code: {form.code.data}")  # Debugging: Print input code
        print(f"Stored Code: {student_reg.verification_code}")  # Debugging: Print stored code

        if student_reg and student_reg.verification_code == form.code.data.strip():  # Stripping spaces
            student_reg.verified = True  # Mark the account as verified
            student_reg.verification_code = None  # Clear the verification code after verification
            db.session.commit()
            flash('Your account has been verified!', 'success')
            session.pop('email', None)  # Remove email from session
            return redirect(url_for('student_login'))
        else:
            flash('Invalid verification code. Please try again.', 'danger')

    return render_template('/student/verify_email.html', form=form)




@app.route('/student/resend_code', methods=['GET'])
def resend_verification_code():
    if 'email' not in session:
        flash('No registration process found. Please register first.', 'warning')
        return redirect(url_for('student_register'))

    # Retrieve the student record from the session's email
    student_reg = Student_Register.query.filter_by(email=session['email']).first()

    if not student_reg:
        flash('Account not found. Please register first.', 'danger')
        return redirect(url_for('student_register'))

    if student_reg.verified:
        flash('Your account is already verified!', 'info')
        return redirect(url_for('student_login'))

    # Generate a new 6-digit random verification code
    new_verification_code = ''.join(random.choices(string.digits, k=6))

    # Update the verification code in the database
    student_reg.verification_code = new_verification_code
    db.session.commit()

    # Resend verification email
    send_verification_email(student_reg.email, new_verification_code)

    flash('A new verification code has been sent to your email.', 'success')
    return redirect(url_for('verify_emails'))


@app.route('/student_login',methods=['POST','GET'])
def student_login():
    form=LoginAdmin()
    if form.validate_on_submit():
        student=Student_Register.query.filter_by(last_name=form.lastname.data).first()
        if student:
            if bcrypt.check_password_hash(student.password,form.password.data):
                login_user(student)
                session['last_name']=student.last_name
                flash('Login Successfully','success')
                return redirect(url_for('student_dashboard'))
            else:
                flash('Wrong Password Try Again','danger')
        else:
            flash('That User Does Not Exist','danger')
    return render_template('/student/login.html',form=form)

@app.route('/student/student_dashboard')
def student_dashboard():
    if 'last_name' not in session:
        flash('Please log in first', 'warning')
        return redirect(url_for('student_login'))
    return render_template('/student/home_dashboard.html',last_name=session['last_name'])

@app.route('/student/student_biodata')
def student_biodata():
    # Check if the user is authenticated by checking if 'last_name' is in the session
    if 'last_name' not in session:
        flash('Please log in first', 'warning')
        return redirect(url_for('student_login'))
    
    # Now that we know the user is authenticated, we can safely access current_user.id
    # But since you are using the session to store last_name, we need to fetch the user by last_name instead of current_user
    student = Student_Register.query.filter_by(last_name=session['last_name']).first()
    
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('student_login'))

    return render_template('/student/biodata.html', stu=student,last_name=session['last_name'])


@app.route('/student/edit_biodata/<int:id>', methods=['POST', 'GET'])
def edit_biodata(id):
    # Check if user is logged in
    if 'last_name' not in session:
        flash('Please Login First', 'warning')
        return redirect(url_for('student_login'))

    # Fetch the student record
    student = Student_Register.query.get_or_404(id)

    # Fetch dropdown options
    levels = Level.query.all()
    sessions = Session.query.all()

    # Capture form data
    if request.method == 'POST':
        # Print debugging information
        print("Received Form Data:")
        print("Level:", request.form.get('level'))
        print("Session:", request.form.get('sessions'))
        print("Parent Guardian Name:", request.form.get('parent_guardian_name'))
        print("Parent Guardian Address:", request.form.get('parent_guardian_address'))
        print("Parent Guardian Phone No:", request.form.get('parent_guardian_phone_no'))

        # Update fields only if new data is provided
        if request.form.get('parent_guardian_name'):
            student.parent_guardian_name = request.form.get('parent_guardian_name')
        if request.form.get('parent_guardian_address'):
            student.parent_guardian_address = request.form.get('parent_guardian_address')
        if request.form.get('parent_guardian_phone_no'):
            student.parent_guardian_phone_no = request.form.get('parent_guardian_phone_no')
        if request.form.get('level'):
            student.level_id = int(request.form.get('level'))
        if request.form.get('sessions'):
            student.session_id = int(request.form.get('sessions'))

        try:
            db.session.commit()
            flash('Biodata updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            print("Database Commit Error:", e)
            flash('Failed to update biodata. Please try again.', 'danger')

        return redirect(url_for('student_biodata'))

    return render_template(
        '/student/edit_biodata.html', 
        student=student, 
        levels=levels, 
        sessions=sessions,
        last_name=session['last_name']
    )


@app.route('/student/student_fees_payment')
def student_fees_payment():
    # Retrieve the logged-in student using session['last_name']
    student = Student_Register.query.filter_by(last_name=session.get('last_name')).first()

    # Check if the student exists
    if not student:
        flash('Student not found', 'danger')
        return redirect(url_for('student_login'))

    # Query the SchoolFee table using the student's program, level, and session
    school_fee = SchoolFee.query.filter_by(
        programme_id=student.programme_id,  # Use the correct foreign key column
        level_id=student.level_id,          # Use the correct foreign key column
        session_id=student.session_id       # Use the correct foreign key column
    ).first()

    # Check if a matching school fee record exists
    if not school_fee:
        flash('No school fee record found for your details.', 'warning')
        return redirect(url_for('student_dashboard'))

    # Convert school fee amount to cents for Stripe payment processing
    try:
        amount_in_cents = int(float(school_fee.amount) * 100)  # Ensure correct formatting for Stripe
    except (ValueError, TypeError):
        flash('Invalid school fee amount.', 'danger')
        return redirect(url_for('student_dashboard'))

    # Pass necessary data to the template
    return render_template(
        '/student/fees_payment.html',
        student=student,
        school_fee=school_fee,
        amount=school_fee.amount,  # Access the fee amount directly
        amount_in_cents=amount_in_cents,  # Amount in cents for Stripe
        last_name=session['last_name']  # Retain last_name for session context
    )



    
@app.route('/payment', methods=['POST'])
def payment():
    amount = int(float(request.form.get('amount')) * 100)  # Convert amount to cents for Stripe

    try:
        # Create a Stripe customer
        customer = stripe.Customer.create(
            email=request.form['stripeEmail'],  # Customer email from Stripe form
            source=request.form['stripeToken'],  # Stripe token generated from the form
        )

        # Create a charge for the customer
        charge = stripe.Charge.create(
            customer=customer.id,  # Stripe customer ID
            description='School Fee Payment',  # Payment description
            amount=amount,  # Payment amount in cents
            currency='ngn',  # Payment currency
        )

        # Update school fee status in the database
        if 'last_name' not in session:
            flash('Please log in before making a payment.', 'danger')
            return redirect(url_for('student_login'))

        # Fetch the student record
        student = Student_Register.query.filter_by(last_name=session['last_name']).first()
        if not student:
            flash('Student record not found.', 'danger')
            return redirect(url_for('student_fees_payment'))

        # Fetch the school fee record
        school_fee = SchoolFee.query.filter_by(
            programme_id=student.programme.name,
            level=student.level.name,
            session_id=student.session.name
        ).first()

        if school_fee:
            school_fee.status = 'Paid'  # Mark the school fee as paid
            db.session.commit()
            flash('Payment successful!', 'success')
            return redirect(url_for('thanks'))
        else:
            flash('School fee record not found.', 'danger')
            return redirect(url_for('student_fees_payment'))

    except stripe.error.StripeError as e:
        # Handle errors from Stripe
        flash(f"Payment error: {e.user_message}", 'danger')
        return redirect(url_for('student_fees_payment'))  # Redirect to the payment page

    except Exception as e:
        # Handle unexpected errors
        flash(f"An unexpected error occurred: {str(e)}", 'danger')
        return redirect(url_for('student_fees_payment'))

@app.route('/student/thanks')
def thanks():
    if 'last_name' not in session:
        flash('Please Login First', 'warning')
        return redirect(url_for('student_login'))
    return render_template('/student/thanks.html')





@app.route('/student/register_course', methods=['GET', 'POST'])
def register_course():
    # Check if 'last_name' is in session to verify if the student is logged in
    if 'last_name' not in session:
        flash('Please log in first to register for courses.', 'warning')
        return redirect(url_for('student_login'))  # Redirect to login if not authenticated

    # Retrieve student by last_name from session
    student = Student_Register.query.filter_by(last_name=session['last_name']).first()
    if not student:
        flash('Student not found. Please log in again.', 'danger')
        return redirect(url_for('student_login'))

    form = RegisterCourseForm()
    form.course_id.choices = [(course.id, course.name) for course in Course.query.all()]

    if form.validate_on_submit():
        # Register the course for the student
        student_course = StudentCourse(
            student_register_id=student.id,  # Use retrieved student's ID
            course_id=form.course_id.data
        )
        db.session.add(student_course)
        db.session.commit()
        flash('Course registered successfully', 'success')
        return redirect(url_for('register_course'))
    
    return render_template('/student/register_course.html', form=form,last_name=session['last_name'])



