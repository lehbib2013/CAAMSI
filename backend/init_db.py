from app import db, create_app

# Créer l'application Flask
app = create_app()

# Initialiser la base de données
with app.app_context():
    db.create_all()
    print("Base de données initialisée avec succès.")