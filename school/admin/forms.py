from flask_wtf import FlaskForm
from wtforms import IntegerField,StringField,PasswordField,TextAreaField,SubmitField,DecimalField
from wtforms.validators import DataRequired,Email,EqualTo,ValidationError,Length,NumberRange
from flask_wtf.file import FileField,FileAllowed
from flask_ckeditor import CKEditorField
from .models import Admin_Register

class RegisterAdmin(FlaskForm):
    name=StringField('Name',validators=[DataRequired()])
    username=StringField('Username',validators=[DataRequired()])
    email=StringField('Email',validators=[DataRequired(),Email()])
    password=PasswordField('Password',validators=[DataRequired(),EqualTo('confirm',message='password must match')])
    confirm=PasswordField('Repeat Password',validators=[DataRequired()])
    submit=SubmitField('Register')

    def validate_username(self,username):
        reg=Admin_Register.query.filter_by(username=username.data).first()
        if reg:
            raise ValidationError ('username is already taken. please choose a defferent one')


    def validate_username(self,email):
        reg=Admin_Register.query.filter_by(email=email.data).first()
        if reg:
            raise ValidationError ('username is already taken. please choose a defferent one')


class VerificationForm(FlaskForm):
    code = StringField('Verification Code', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Verify Email')


class LoginAdmin(FlaskForm):
    username=StringField('Username',validators=[DataRequired()])
    password=PasswordField('Password',validators=[DataRequired()])
    submit=SubmitField('Login')


class BlogPost(FlaskForm):
    title=StringField('Title',validators=[DataRequired()])
    content=CKEditorField('Content',validators=[DataRequired()])
    image=FileField('Image',validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Image only please!')])
    submit=SubmitField('Submit')

    def __init__(self,*args,**kwargs):
        super(BlogPost,self).__init__(*args,**kwargs)


