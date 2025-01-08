from school import db,login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def user_loader(user_id):
    return Admin_Register.query.get(user_id)


class Admin_Register(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(50),unique=False)
    username = db.Column(db.String(50),unique=True)
    email = db.Column(db.String(50),unique=True)
    password = db.Column(db.String(200),unique=False)
    verified = db.Column(db.Boolean,default=False)
    verification_code = db.Column(db.String(6),nullable=True)

    def __repr__(self):
        return '<Admin_Register %r>' % self.name


class SchoolFee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.String(255), nullable=True)

    # Foreign keys
    programme_id = db.Column(db.Integer, db.ForeignKey('programme.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    level_id = db.Column(db.Integer, db.ForeignKey('level.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)

    # Relationships
    programme = db.relationship('Programme', backref='schoolfee')
    department = db.relationship('Department', backref='schoolfee')
    level = db.relationship('Level', backref='schoolfee')
    session = db.relationship('Session', backref='schoolfee')


class Category(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=False)

    def __repr__(self):
        return '<name %r>' % self.name


class Post(db.Model):
    __searchable__=['title','content']
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer,db.ForeignKey('category.id'),nullable=False)
    category=db.relationship('Category',backref='category',lazy=True)
    image = db.Column(db.String(100))
    author_id = db.Column(db.Integer, db.ForeignKey('admin__register.id'), nullable=False)
    author = db.relationship('Admin_Register',backref='author',lazy=True)
    date_posted = db.Column(db.DateTime,nullable=False,default=datetime.utcnow)

    def __repr__(self):
        return '<title %r>' % self.title
