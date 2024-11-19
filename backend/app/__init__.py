from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Initialisation des extensions
    db.init_app(app)
    CORS(app)
    
    # Importation des routes
    from .routes.products import product_bp
    app.register_blueprint(product_bp, url_prefix='/api/products')
    
    return app