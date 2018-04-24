from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_uploads import UploadSet,DEFAULTS, configure_uploads, ALL,IMAGES,TEXT,AllExcept

from config import config

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
photos = UploadSet('photos', IMAGES)
text=UploadSet("text",DEFAULTS)
All_FILE=AllExcept(('vhd', 'iso','vmdk','raw','qcow2'))
all_file=UploadSet("allfile",All_FILE)
def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd()+"/app/files/"
    app.config['UPLOADED_TEXT_DEST'] = os.getcwd()+"/app/files/"
    app.config['UPLOADED_ALLFILE_DEST']=os.getcwd()+"/app/files/"
    print app.config['UPLOADED_PHOTOS_DEST']
    configure_uploads(app, photos)
    configure_uploads(app,text)
    configure_uploads(app,all_file)
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app
