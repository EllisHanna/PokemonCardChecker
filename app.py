from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS
from models import db, User
from routes import main
from flask_migrate import Migrate

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = "SECRET_KEY"

db.init_app(app)
migrate = Migrate(app, db)

CORS(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

app.register_blueprint(main)

if __name__ == "__main__":
    app.run(debug=True)