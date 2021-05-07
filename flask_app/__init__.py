

import json
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail

with open('/etc/gymsite_config.json') as config_file:
        config = json.load(config_file)

# app quick start with database

# innit app
app = Flask(__name__)
# innit database file
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gymsite.db'
# set secret key for forms
app.config['SECRET_KEY'] = config.get('SECRET_KEY')
# connect db to app
db = SQLAlchemy(app)\
# innit login manager
login_manager = LoginManager()
# connect login manaager to app
login_manager.init_app(app)
# connect Bcrypt to app
login_manager.login_view = 'login'
encrypt = Bcrypt(app)
# innit Mail app
app.config['MAIL_SERVER']= 'smtp.gmail.com'
app.config['MAIL_PORT']= '465'
app.config['MAIL_USERNAME']= config.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD']= config.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS']=False
app.config['MAIL_USE_SSL']=True
mail = Mail(app)


#import routes
from .routes import(
    workouts, workout_details,create_workout, upcoming_workouts,
    create_movement,update_movement,
    create_component, component_detail, update_component, delete_component,
    logout,register, login, reset_request, reset_password
    )