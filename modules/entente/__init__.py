from flask import Blueprint

entente_bp = Blueprint('ententes', __name__, template_folder='../../templates/passation')

from .views import ententes_views