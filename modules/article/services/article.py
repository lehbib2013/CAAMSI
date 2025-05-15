from modules.article.repository.article import ProduitRepository
class FournisseurService:
    def __init__(self, repository: ProduitRepository):
        self.repository = repository

    def get_all_produits(self):
        return self.repository.select_all()