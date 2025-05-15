from flask import Blueprint

pa_bp = Blueprint(
    'pa',
    __name__,
    template_folder='pages',
    static_folder='static',
    static_url_path='/programmes-d-achat/static'
)

# Import views and resources here
# from .views import ...
# from .resources import ...
