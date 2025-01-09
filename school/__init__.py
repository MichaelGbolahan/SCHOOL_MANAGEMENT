from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import IMAGES, UploadSet, configure_uploads
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_login import LoginManager
from flask_ckeditor import CKEditor
from flask_msearch import Search
from dotenv import load_dotenv
import os

# Load environment variables from .env file
# Ensure you have a .env file containing sensitive configurations
load_dotenv()

# Base directory: set to the project root
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Config file path
config_path = os.path.join(basedir, 'school', 'config.cfg')

# Ensure config file exists
if os.path.exists(config_path):
    app = Flask(__name__)
    app.config.from_pyfile(config_path)
else:
    raise FileNotFoundError(f"Config file not found at {config_path}")

# Initialize CKEditor
ckeditor = CKEditor(app)

# Upload configuration
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'static/pictures')
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

# Stripe keys
stripe_publishable_key = app.config['PUBLISHABLE_KEY']
stripe_secret_key = app.config['STRIPE_SECRET_KEY']

# Database setup
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
mail = Mail(app)

# Full-text search setup
search = Search(db=db)
search.init_app(app)

# User login management
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'student_login'
login_manager.needs_refresh_message_category = 'danger'
login_manager.login_message = u'please login first'

# Import blueprints (routes)
from school.public import route
from school.student import route, forms, models
from school.admin import route, forms, models
