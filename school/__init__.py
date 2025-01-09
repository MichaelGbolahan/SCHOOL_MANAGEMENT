from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import IMAGES, UploadSet, configure_uploads
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_login import LoginManager
from flask_ckeditor import CKEditor
from flask_msearch import Search
from dotenv import load_dotenv
import os

load_dotenv()  # Load .env for local development

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# Database Configuration (PostgreSQL on Render, MySQL locally)
if os.environ.get('RENDER'):  # Check if running on Render
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI') #Get the postgres url from render environment variable
else:
    app.config['MYSQL_DATABASE_URI'] = os.environ.get('MYSQL_DATABASE_URI')  # Use DATABASE_URL from .env (MySQL)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Other Configuration (from environment variables - with defaults for local)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_secret_key')
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'static/pictures')

# Stripe Keys
app.config['PUBLISHABLE_KEY'] = os.environ.get('PUBLISHABLE_KEY')
app.config['STRIPE_SECRET_KEY'] = os.environ.get('STRIPE_SECRET_KEY')

if not app.config['PUBLISHABLE_KEY'] or not app.config['STRIPE_SECRET_KEY']:
    raise ValueError("Stripe publishable and secret keys must be set as environment variables.")

# Initialize extensions AFTER config is set
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
mail = Mail(app)
search = Search(db=db)
search.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'student_login'
login_manager.needs_refresh_message_category = 'danger'
login_manager.login_message = u'please login first'
ckeditor = CKEditor(app)


from school.public import route
from school.student import route,forms,models
from school.admin import route,models,forms
