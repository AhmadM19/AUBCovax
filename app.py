from flask import Flask
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from config import SECRET_KEY,DATABASE_URL

app = Flask(__name__)

app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL

ma = Marshmallow(app)

bcrypt = Bcrypt(app)

CORS(app)

app.app_context().push()

db = SQLAlchemy(app)

from routes.auth import auth_bp
app.register_blueprint(auth_bp)

from routes.reservationRoutes import reservations_bp
app.register_blueprint(reservations_bp)

from routes.userRoutes import users_bp
app.register_blueprint(users_bp)
