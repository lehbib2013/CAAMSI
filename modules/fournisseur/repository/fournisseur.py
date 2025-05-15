from sqlalchemy.orm import Session
from models.db import Fournisseur

class FournisseurRepository:
    def __init__(self, session: Session):
        self.session = session

    def insert(self, fournisseur: Fournisseur):
        self.session.add(fournisseur)
        self.session.commit()

    def update(self, fournisseur: Fournisseur):
        self.session.merge(fournisseur)
        self.session.commit()

    def delete(self, fournisseur_id: int):
        fournisseur = self.session.query(Fournisseur).get(fournisseur_id)
        if fournisseur:
            self.session.delete(fournisseur)
            self.session.commit()

    def select_all(self):
        self.session.expire_all()  # Clear the session cache
        return self.session.query(Fournisseur).all()

    def select_one(self, fournisseur_id: int):
        print("Executing select_all query...")
        return self.session.query(Fournisseur).get(fournisseur_id)