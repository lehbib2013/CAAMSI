from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from .routes import register_blueprints

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Initialisation des extensions
    db.init_app(app)
    CORS(app)
    #register_blueprints()

    from .models import init_models
    Product = init_models(db)
# Importation des routes
    from .routes.products import product_bp
    app.register_blueprint(product_bp, url_prefix='/api/products')
    
    return app