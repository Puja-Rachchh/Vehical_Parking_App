
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
 
    # Configuration
    app.config['SECRET_KEY'] = '1234'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    return app
