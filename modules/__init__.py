from flask import Flask
import tomli 
from modules.user import user_bp
from modules.budget import budget_bp
from modules.exercice import exercice_bp
from modules.pa import pa_bp
from datetime import datetime
from modules.depot import depot_bp
from modules.ppm import ppm_bp
from modules.fournisseur import fournisseur_bp
from modules.entente import entente_bp
from modules.consultation import consultation_bp
from modules.contrat import contrat_bp
from modules.LC import lc_bp
from flask_cors import CORS
from flask_migrate import Migrate
from models.db import Base
from modules.fournisseur.views.fournisseur_views import fournisseur_bp
from modules.article import produits_bp
from flask_wtf.csrf import CSRFProtect

def create_app(config_path=None):
    app = Flask(__name__, template_folder='..//templates', static_folder='../static')
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    # csrf = CSRFProtect()
    app.secret_key = 'your-unique-secret-key' 
    # csrf.init_app(app)
    CORS(app)
    if config_path:
        with open(config_path, 'rb') as f:
            app.config.update(tomli.load(f))
    with app.app_context():
        app.register_blueprint(user_bp, url_prefix='/user')
        app.register_blueprint(budget_bp, url_prefix='/budget')
        app.register_blueprint(exercice_bp, url_prefix='/exercice')
        app.register_blueprint(pa_bp, url_prefix='/pa')
        app.register_blueprint(produits_bp, url_prefix='/produits')
        app.register_blueprint(depot_bp, url_prefix='/depot')
        app.register_blueprint(ppm_bp, url_prefix='/ppm')
        app.register_blueprint(entente_bp, url_prefix='/ententes')
        app.register_blueprint(consultation_bp, url_prefix='/consultations')
        app.register_blueprint(contrat_bp, url_prefix='/contrat')
        app.register_blueprint(lc_bp, url_prefix='/lc')
        app.register_blueprint(fournisseur_bp, url_prefix='/fournisseurs')

    @app.context_processor
    def inject_breadcrumbs():
        from flask import request
        breadcrumbs = []
        path_segments = request.path.strip('/').split('/')
        for i, segment in enumerate(path_segments):
            url = '/' + '/'.join(path_segments[:i + 1])
            breadcrumbs.append({'name': segment.capitalize(), 'url': url})
        return {'breadcrumbs': breadcrumbs}
    
    @app.template_filter('datetimeformat')
    def datetimeformat(value, format='%Y-%m-%dT%H:%M'):
        if isinstance(value, datetime):
            return value.strftime(format)
        return value
    migrate = Migrate(app, Base)
    
    return app