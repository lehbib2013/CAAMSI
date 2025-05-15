from flask import Blueprint

consultation_bp = Blueprint('consultations', __name__, template_folder='../../templates/passation')

from .views import consultation_views