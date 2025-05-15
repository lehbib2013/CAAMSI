from flask import Blueprint

lc_bp = Blueprint(
    'lc',
    __name__,
    template_folder='pages',
    static_folder='static',
    static_url_path='/lc-et-logistique/static'
)

# Import views and resources here
# from .views import ...
# from .resources import ...
