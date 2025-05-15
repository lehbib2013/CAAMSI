from modules.fournisseur.models.db import Base, engine

# Create all tables defined in the models
if __name__ == "__main__":
    print("Creating database tables...")
    Base.metadata.create_all(engine)
    print("Database tables created successfully.")