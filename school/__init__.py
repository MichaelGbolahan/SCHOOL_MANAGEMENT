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
load_dotenv()


# Base directory
basedir = os.path.abspath(os.path.dirname(__file__))

app=Flask(__name__)

# Load the configuration file from Render's secret path
config_path = "/etc/secrets/config.cfg"  # This path matches what you set in Render
if os.path.exists(config_path):
    app.config.from_pyfile(config_path)
else:
    raise FileNotFoundError(f"Config file not found at {config_path}")

# Initialize CKEditor
ckeditor = CKEditor(app)





app.config.from_pyfile('config.cfg')
app.config.from_pyfile('config.cfg')
app.config.from_pyfile('config.cfg')
app.config.from_pyfile('config.cfg')
app.config.from_pyfile('config.cfg')
app.config.from_pyfile('config.cfg')
app.config.from_pyfile('config.cfg')
app.config.from_pyfile('config.cfg')
app.config.from_pyfile('config.cfg')
app.config.from_pyfile('config.cfg')
app.config.from_pyfile('config.cfg')
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'static/pictures')

# Upload configuration
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

stripe_publishable_key = app.config['PUBLISHABLE_KEY']
stripe_secret_key = app.config['STRIPE_SECRET_KEY']


db=SQLAlchemy(app)
migrate=Migrate(app,db)
bcrypt=Bcrypt(app)
mail = Mail(app)

search = Search(db=db)
search.init_app(app)  # Ensure `search.init_app` is called after `db` initialization


login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'student_login'
login_manager.needs_refresh_message_category = 'danger'
login_manager.login_message = u'please login first' 


from school.public import route
from school.student import route,forms,models
from school.admin import route,forms,models