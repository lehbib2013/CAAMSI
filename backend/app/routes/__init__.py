from flask import Blueprint

# Importation des blueprints depuis leurs modules respectifs
from .products import product_bp

# Liste des blueprints pour centraliser l'enregistrement
def register_blueprints(app):
    """
    Enregistre tous les blueprints de l'application.
    """
    app.register_blueprint(product_bp, url_prefix='/api/products')

# Exemple : Ajoutez d'autres blueprints ici si nécessaire
# from .users import user_bp
# app.register_blueprint(user_bp, url_prefix='/api/users')