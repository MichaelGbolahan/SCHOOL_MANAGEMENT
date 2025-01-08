from school import db, login_manager
from flask_login import UserMixin

class Programme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

class Faculty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

class Sex(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)


class Level(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)


class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)


class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    credit_hours = db.Column(db.Integer, nullable=False)

    # Relationship to get all students in this course
    student_courses = db.relationship('StudentCourse', back_populates='course')

class StudentCourse(db.Model):
    __tablename__ = 'student_course'
    id = db.Column(db.Integer, primary_key=True)
    student_register_id = db.Column(db.Integer, db.ForeignKey('student_register.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)  # Corrected ForeignKey reference
    date_registered = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relationships
    course = db.relationship('Course', back_populates='student_courses')
    student = db.relationship('Student_Register', back_populates='registered_courses')

@login_manager.user_loader
def user_loader(user_id):
    return Student_Register.query.get(user_id)

class Student_Register(db.Model, UserMixin):
    __tablename__ = 'student_register'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), unique=False)
    last_name = db.Column(db.String(50), unique=False)
    other_name = db.Column(db.String(50), unique=False)
    programme_id = db.Column(db.Integer, db.ForeignKey('programme.id'), nullable=False)
    programme = db.relationship('Programme', backref=db.backref('school', lazy=True))
    session = db.Column(db.String(60), unique=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    faculty = db.relationship('Faculty', backref=db.backref('faculty', lazy=True))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    department = db.relationship('Department', backref=db.backref('department', lazy=True))
    level_id = db.Column(db.Integer, db.ForeignKey('level.id'), nullable=False)  # Changed from TEXT to VARCHAR
    level = db.relationship('Level', backref=db.backref('level', lazy=True))
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    session = db.relationship('Session', backref=db.backref('session', lazy=True))
    sex_id = db.Column(db.Integer, db.ForeignKey('sex.id'), nullable=False)
    sex = db.relationship('Sex', backref=db.backref('sex', lazy=True))
    date_of_birth = db.Column(db.String(50), unique=False)  # Changed from TEXT to VARCHAR
    email = db.Column(db.String(50), unique=True)
    phone_no = db.Column(db.String(20), nullable=False)
    residential_address = db.Column(db.String(150), unique=False)  # Changed from TEXT to VARCHAR
    place_of_birth = db.Column(db.String(100), unique=False)
    state_of_origin = db.Column(db.String(100), unique=False)
    local_govt_area = db.Column(db.String(100), unique=False)
    parent_guardian_name = db.Column(db.String(100), unique=False)
    parent_guardian_address = db.Column(db.String(150), unique=False)  # Changed from TEXT to VARCHAR
    parent_guardian_phone_no = db.Column(db.String(20))
    password = db.Column(db.String(200), unique=False)
    profile = db.Column(db.String(180), unique=False, nullable=False, default='profile.jpg')
    verified = db.Column(db.Boolean, default=False)
    verification_code = db.Column(db.String(6), nullable=True)
    registered_courses = db.relationship('StudentCourse', back_populates='student')
    payments = db.relationship('Payment', backref='student', lazy=True)

    def __repr__(self):
        return '<Student_Register %r>' % self.first_name


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_register.id'), nullable=False)
    school_fee_id = db.Column(db.Integer, db.ForeignKey('school_fee.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.DateTime, nullable=False)