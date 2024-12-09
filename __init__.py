from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
   
    
    with app.app_context():
        # Registrar rutas
        from . import routes
        return app
