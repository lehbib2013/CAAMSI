from flask import Blueprint

fournisseur_bp = Blueprint(
    'fournisseurs',
    __name__,
     template_folder='templates/fournisseurs' 

)

from .views import fournisseur_views