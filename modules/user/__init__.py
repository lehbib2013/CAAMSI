from flask import Blueprint

user_bp = Blueprint(
    'user',
    __name__,
    template_folder='pages',
    static_folder='static',
    static_url_path='/users/static'
)

# Import views and resources here
# from .views import ...
# from .resources import ...
