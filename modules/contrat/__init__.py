from flask import Blueprint

contrat_bp = Blueprint(
    'contrat',
    __name__,
    template_folder='pages',
    static_folder='static',
    static_url_path='/contrats/static'
)

# Import views and resources here
# from .views import ...
# from .resources import ...
