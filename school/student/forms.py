from flask_wtf import FlaskForm
from wtforms import IntegerField,StringField,PasswordField,TextAreaField,SubmitField,SelectField,DecimalField
from wtforms.validators import DataRequired,Email,EqualTo,ValidationError,Length,NumberRange
from flask_wtf.file import FileField,FileAllowed
from .models import Student_Register

class RegisterStudent(FlaskForm):
    first_name=StringField('First Name',validators=[DataRequired()])
    last_name=StringField('Last Name',validators=[DataRequired()])
    other_name=StringField('Other Name',validators=[DataRequired()])
    session=StringField('Session')
    level=StringField('Level')
    date_of_birth=StringField('Date Of Birth',validators=[DataRequired()])
    email=StringField('Email',validators=[DataRequired(),Email()])
    phone_no=StringField('Phone No',validators=[DataRequired()])
    residential_address=StringField('Residential Address',validators=[DataRequired()])
    place_of_birth=StringField('Place Of Birth',validators=[DataRequired()])
    state_of_origin=StringField('State Of Origin',validators=[DataRequired()])
    local_govt_area=StringField('LGA',validators=[DataRequired()])
    parent_guardian_name=StringField('Parent Name')
    parent_guardian_address=StringField('Parent Address')
    parent_guardian_phone_no=StringField('Parent Phone No')
    password=PasswordField('Password',validators=[DataRequired(),EqualTo('confirm',message='password must match')])
    confirm=PasswordField('Repeat Password',validators=[DataRequired()])
    image = FileField('Image',validators=[FileAllowed(['jpg','jpeg','png','gif'])])
    submit=SubmitField('Register')

    def validate_username(self,last_name):
        reg=Student_Register.query.filter_by(last_name=last_name.data).first()
        if reg:
            raise ValidationError ('Last is already taken. please choose a defferent one')


    def validate_username(self,email):
        reg=Student_Register.query.filter_by(email=email.data).first()
        if reg:
            raise ValidationError ('email is already taken. please choose a defferent one')



class VerificationForm(FlaskForm):
    code = StringField('Verification Code', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Verify Email')


class LoginAdmin(FlaskForm):
    lastname=StringField('Lastname',validators=[DataRequired()])
    password=PasswordField('Password',validators=[DataRequired()])
    submit=SubmitField('Login')

class AddCourseForm(FlaskForm):
    code = StringField('Course Code', validators=[DataRequired(), Length(max=10)])
    name = StringField('Course Name', validators=[DataRequired(), Length(max=100)])
    credit_hours = IntegerField('Credit Hours', validators=[DataRequired(), NumberRange(min=1, max=10)])
    submit = SubmitField('Add Course')

class RegisterCourseForm(FlaskForm):
    course_id = SelectField('Course', choices=[], coerce=int, validators=[DataRequired()])
    submit = SubmitField('Register for Course')

class PaymentForm(FlaskForm):
    school_fee_id = SelectField('School Fee', choices=[], coerce=int)
    amount = DecimalField('Amount', places=2)
    submit = SubmitField('Pay Now')