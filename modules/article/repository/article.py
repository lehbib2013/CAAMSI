from models.db import Produit  # Adjust the import path based on your project structure
from sqlalchemy.orm import Session

class ProduitRepository:
    def __init__(self, session: Session):
        self.session = session

    def insert(self, produit: Produit):
        self.session.add(produit)
        self.session.commit()

    def update(self, produit: Produit):
        self.session.merge(produit)
        self.session.commit()

    def delete(self, produit_id: int):
        produit = self.session.query(Produit).get(produit_id)
        if produit:
            self.session.delete(produit)
            self.session.commit()

    def select_all(self):
        self.session.expire_all()  # Clear the session cache
        return self.session.query(Produit).all()

    def select_one(self, produit_id: int):
        print("Executing select_one query...")
        return self.session.query(Produit).get(produit_id)
