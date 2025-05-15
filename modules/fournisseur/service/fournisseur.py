from modules.fournisseur.repository.fournisseur import FournisseurRepository

class FournisseurService:
    def __init__(self, repository: FournisseurRepository):
        self.repository = repository

    def get_all_fournisseurs(self):
        return self.repository.select_all()