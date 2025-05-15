from flask import Blueprint

exercice_bp = Blueprint(
    'exercice',
    __name__,
    template_folder='pages',
    static_folder='static',
    static_url_path='/exercices/static'
)

# Import views and resources here
# from .views import ...
# from .resources import ...
