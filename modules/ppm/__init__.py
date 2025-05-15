from flask import Blueprint

ppm_bp = Blueprint(
    'ppm',
    __name__,
    template_folder='pages',
    static_folder='static',
    static_url_path='/ppm/static'
)

# Import views and resources here
# from .views import ...
# from .resources import ...

# Dossiers créés manuellement :
# /Users/a2141/Desktop/CAAMSI/modules/PPM/pages/
# /Users/a2141/Desktop/CAAMSI/modules/PPM/views/
# /Users/a2141/Desktop/CAAMSI/modules/PPM/resources/
