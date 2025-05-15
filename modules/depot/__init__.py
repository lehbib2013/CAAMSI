from flask import Blueprint

depot_bp = Blueprint(
    'depot',
    __name__,
    template_folder='pages',
    static_folder='static',
    static_url_path='/les-depots/static'
)

# Import views and resources here
# from .views import ...
# from .resources import ...
