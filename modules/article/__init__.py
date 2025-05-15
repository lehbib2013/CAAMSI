from flask import Blueprint

produits_bp = Blueprint('produits', __name__,  template_folder='templates/produits' )

from .views import product_views
