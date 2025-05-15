from flask import Blueprint

budget_bp = Blueprint(
    'budget',
    __name__,
    template_folder='pages',
    static_folder='static',
    static_url_path='/budget/static'
)

# Import views and resources here
# from .views import ...
# from .resources import ...

# Dossiers créés manuellement :
# /Users/a2141/Desktop/CAAMSI/modules/Budget/pages/
# /Users/a2141/Desktop/CAAMSI/modules/Budget/views/
# /Users/a2141/Desktop/CAAMSI/modules/Budget/resources/
