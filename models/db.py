from sqlalchemy import (
    Column, Integer, String, Boolean, Float, LargeBinary, Date, DateTime,ForeignKey, Enum,JSON, Table, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import enum

Base = declarative_base()


# Database connection setup
DATABASE_URI = "mysql+mysqlconnector://root:google@localhost/caamsi" # Replace with your actual database URI
engine = create_engine(DATABASE_URI)

# Create a session factory
Session = sessionmaker(bind=engine)
# Enums for validation
class TypePassationEnum(enum.Enum):
    ENTENTE_DIRECTE = "Entente Directe"
    CONSULTATION_FOURNISSEURS = "Consultation des fournisseurs"

class StatutEnum(enum.Enum):
    PREPARATION ="En preparation"
    LANCE = "Lancement"
    OUVERT = "Ouverture"
    EVALUE = "Evaluation"
    INFRUCTUEUSE = "Infructeuse"
    ATTRIBUEPROVIS = "Attribution provisoire"
    ATTRIBUDEFINITIVE ="Attribution definitive"
    APPROBATIONCNCMP ="Approbation CNCMP"
    NUMEROTATION ="Numerotation"
    CONTRAT = "Contrat signe"
    RESILIE = "Resilie"

class CriteresQualificationEnum(enum.Enum):
    PAR_PRODUIT = "par produit"
    PAR_OFFRE = "par offre"


class Produit(Base):
    __tablename__ = 'produits'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    prix_achat = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)
    categorie = Column(String(100), nullable=True)
    peut_etre_vendu= Column(Boolean, default=True)
    def __repr__(self):
        return f"<Produit(id={self.id}, nom='{self.nom}', description='{self.description}', prix_achat={self.prix_achat}, stock={self.stock}, categorie='{self.categorie}', peut_etre_vendu={self.peut_etre_vendu})>"



class Fournisseur(Base):
    __tablename__ = 'fournisseurs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(255), nullable=False)
    NIF = Column(String(50), nullable=False, unique=False)
    sigle_image = Column(String(255), nullable=True)
    contact = Column(String(100), nullable=False)  # New field for contact
    address = Column(String(255), nullable=False)  # New field for address
    email = Column(String(255), nullable=False)  # New field for email
    trader = Column(Boolean, default=False)  # New field for trader
    list_noire = Column(Boolean, default=False)  # New field for list_noire
    etiquettes =  Column(JSON, nullable=True)  # New field for list_noire

    def __repr__(self):
        return f"<Fournisseur(id={self.id}, nom='{self.nom}', numero='{self.numero}', sigle_image='{self.sigle_image}', contact='{self.contact}', address='{self.address}', email='{self.email}')>"




    def __repr__(self):
        return f"<TypeMarche(id={self.id}, type_passation='{self.type_passation.value}', criteres_qualification='{self.criteres_qualification.value}')>"
class DecisionCSPMPEnum(enum.Enum):
    INFRUCTUEUX = "Infructueux"
    NOUVELLE_PROCEDURE = "Recours à une nouvelle procédure concurrentielle"
    GENERER_CONTRATS = "Générer des contrats sur la base fournies"

class Marche(Base):
    __tablename__ = 'marches'

    id = Column(Integer, primary_key=True, autoincrement=True)
    designation = Column(String(255), nullable=False)
    criteres_qualification = Column(Enum(CriteresQualificationEnum), nullable=False)
    type = Column(String(50))  # Discriminator column to differentiate subclasses
    cautions_presentees = Column(Boolean, default=False)  # Indique si les cautions ce bonne execution ont été exiges
    cautions_soumission = Column(Boolean, default=False)  # Indique si les cautions de soumission ont été exiges
    annulation = Column(Boolean, default=False)  # Indique si la consultation a été annulée
    # New fields for attribution
    pv_attribution = Column(LargeBinary, nullable=True)  # Procès-verbal d'attribution
    pv_attribution_filename = Column(String(255), nullable=True)  # Nom du fichier d'attribution
    cloture = Column(Boolean, default=False)
    decision_cspmp = Column(Enum(DecisionCSPMPEnum), nullable=True)
    # New fields
    contrat = Column(Boolean, default=False)  # Indicates if the contract is signed
    numerotation = Column(Boolean, default=False)  # Indicates if the numbering is done


    __mapper_args__ = {
        'polymorphic_on': type,  # Field used to differentiate subclasses
        'polymorphic_identity': 'marche'  # Identity for the base class
    }

    def __repr__(self):
        return (f"<Marche(id={self.id}, designation='{self.designation}', "
                f"date_reunion_demarrage={self.date_reunion_demarrage}, criteres_qualification='{self.criteres_qualification}')>")

# Table d'association entre Marche et Produit avec quantités
class MarcheProduit(Base):
    __tablename__ = 'marche_produit'

    id = Column(Integer, primary_key=True,nullable=False, autoincrement=True)
    marche_id = Column(Integer, ForeignKey('marches.id'), nullable=False)
    produit_id = Column(Integer, ForeignKey('produits.id'), nullable=False)
    quantite = Column(Float, nullable=False)  # Quantité du produit dans le marché


    marche = relationship("Marche", backref="marche_produits")
    produit = relationship("Produit", backref="marche_produits")
   

    def __repr__(self):
        return (f"<MarcheProduit(id={self.id}, marche_id={self.marche_id}, produit_id={self.produit_id}, "
                f"quantite={self.quantite})>")
    
class MarchePart(Base):
    __tablename__ = 'marche_parts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    marche_id = Column(Integer, ForeignKey('marches.id'), nullable=False)  # Link to the Marche
    produit_id = Column(Integer, ForeignKey('produits.id'), nullable=False)  # Link to the Produit
    quantite = Column(Float, nullable=False)  # Quantity for this part

    marche = relationship("Marche", backref="marche_parts")
    produit = relationship("Produit", backref="marche_parts")

    def __repr__(self):
        return (f"<MarchePart(id={self.id}, marche_id={self.marche_id}, produit_id={self.produit_id}, "
                f"quantite={self.quantite})>")
    
    def validate_quantities(self, session):
        """
        Validate that the sum of quantities in MarchePart matches the global quantity in MarcheProduit.
        """
        for produit in self.marche_produits:
            global_quantity = produit.quantite
            parts_quantity = session.query(func.sum(MarchePart.quantite)).filter_by(
                marche_id=self.id, produit_id=produit.produit_id
            ).scalar() or 0

            if parts_quantity != global_quantity:
                raise ValueError(
                    f"Quantities for product {produit.produit.nom} in Marche {self.id} do not match: "
                    f"Global quantity = {global_quantity}, Parts total = {parts_quantity}"
                )
    

class ConsultationFournisseurs(Marche):
    __tablename__ = 'consultation_fournisseurs'

    id = Column(Integer, ForeignKey('marches.id'), primary_key=True)
    liste_fournisseurs_consulter = Column(LargeBinary, nullable=True)
    liste_fournisseurs_consulter_filename = Column(String(255), nullable=True)
    voie_soumission = Column(String(255), nullable=False)
    date_lancement = Column(DateTime, nullable=True)
    date_limite_depot = Column(DateTime, nullable=True)
    demande_cotation = Column(LargeBinary, nullable=True)
    demande_cotation_filename = Column(String(255), nullable=True)
    numero_rfq = Column(String(255), nullable=True)
    evaluation = Column(Boolean, default=False)
    pv_evaluation = Column(LargeBinary, nullable=True)
    pv_evaluation_filename = Column(String(255), nullable=True)
    date_evaluation = Column(DateTime, nullable=True)
    pv_designation_comission_ad_hoc = Column(LargeBinary, nullable=True)
    pv_designation_comission_ad_hoc_filename = Column(String(255), nullable=True)
    ppm_ou_justificatif_achat = Column(LargeBinary, nullable=True)
    ppm_ou_justificatif_achat_filename = Column(String(255), nullable=True)
    
    statut = Column(Enum(StatutEnum), nullable=False, default=StatutEnum.OUVERT)  # New field for status
    # New fields
    infructure = Column(Boolean, default=False)  # Indique si la consultation est infructueuse
    

    # New fields for ouverture
    date_ouverture = Column(DateTime, nullable=True)  # Date of opening
    pv_ouverture = Column(LargeBinary, nullable=True)  # Opening report (binary data)
    pv_ouverture_filename = Column(String(255), nullable=True)  # Filename for the opening report

    __mapper_args__ = {
        'polymorphic_identity': 'consultation_fournisseurs'  # Identity for this subclass
    }

    def __repr__(self):
        return (f"<ConsultationFournisseurs(id={self.id}, voie_soumission='{self.voie_soumission}', "
                f"date_lancement={self.date_lancement}, date_limite_depot={self.date_limite_depot})>")
    

class AttributionMarche(Base):
    __tablename__ = 'attributions_marches'

    id = Column(Integer, primary_key=True, autoincrement=True)
    marche_id = Column(Integer, ForeignKey('marches.id'), nullable=False)  # Lié au marché
    fournisseur_id = Column(Integer, ForeignKey('fournisseurs.id'), nullable=False)  # Lié au fournisseur
    produit_id = Column(Integer, ForeignKey('produits.id'), nullable=False)  # Lié au produit
    quantite = Column(Float, nullable=False)  # Quantité attribuée
    prix_unitaire = Column(Float, nullable=False)  # Prix unitaire
    prix_total = Column(Float, nullable=False)  # Prix total (calculé)
    offre_technique = Column(LargeBinary, nullable=True)  # Offre technique (PDF)
    offre_technique_filename = Column(String(255), nullable=True)  # Nom du fichier de l'offre technique
    offre_financiere = Column(LargeBinary, nullable=True)  # Offre financière (PDF)
    offre_financiere_filename = Column(String(255), nullable=True)  # Nom du fichier de l'offre financière
    caution_bonne_execution = Column(LargeBinary, nullable=True)  # Caution de bonne exécution (PDF)
    caution_bonne_execution_filename = Column(String(255), nullable=True)  # Nom du fichier de la caution

    # Relations
    marche = relationship("Marche", backref="attributions_marches")
    fournisseur = relationship("Fournisseur", backref="attributions_marches")
    produit = relationship("Produit", backref="attributions_marches")

    def __repr__(self):
        return (f"<AttributionMarche(id={self.id}, marche_id={self.marche_id}, fournisseur_id={self.fournisseur_id}, "
                f"produit_id={self.produit_id}, quantite={self.quantite}, prix_unitaire={self.prix_unitaire}, "
                f"prix_total={self.prix_total})>")
    


class EntenteDirecte(Marche):
    __tablename__ = 'entente_directe'

    id = Column(Integer, ForeignKey('marches.id'), primary_key=True)
    pv_negociation = Column(LargeBinary, nullable=True)  # PV de négociation
    pv_negociation_filename = Column(String(255), nullable=True)
    offre_technique = Column(LargeBinary, nullable=True)  # Offre technique
    offre_technique_filename = Column(String(255), nullable=True)
    offre_financiere = Column(LargeBinary, nullable=True)  # Offre financière
    offre_financiere_filename = Column(String(255), nullable=True)
    justificatif_recours = Column(LargeBinary, nullable=True)  # Justificatif de recours
    justificatif_recours_filename = Column(String(255), nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'entente_directe'  # Identity for this subclass
    }

    def __repr__(self):
        return (f"<EntenteDirecte(id={self.id}, pv_negociation_filename='{self.pv_negociation_filename}', "
                f"offre_technique_filename='{self.offre_technique_filename}', "
                f"offre_financiere_filename='{self.offre_financiere_filename}')>")    


# Classe Soumission
class Soumission(Base):
    __tablename__ = 'soumissions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fournisseur_id = Column(Integer, ForeignKey('fournisseurs.id'), nullable=False)
    consultation_fournisseurs_id = Column(Integer, ForeignKey('consultation_fournisseurs.id'), nullable=False)  # Updated to link to ConsultationFournisseurs
    soumission_document = Column(LargeBinary, nullable=True)
    soumission_document_filename = Column(String(255), nullable=True)
    montant_total = Column(Float, nullable=True)  # Nouveau champ pour le montant total
    ordre_classement = Column(Integer, nullable=True)  # Nouveau champ pour l'ordre de classement

    fournisseur = relationship("Fournisseur", backref="soumissions")
    consultation_fournisseurs = relationship("ConsultationFournisseurs", backref="soumissions")  # Updated relationship

    def __repr__(self):
        return (f"<Soumission(id={self.id}, fournisseur_id={self.fournisseur_id}, "
                f"consultation_fournisseurs_id={self.consultation_fournisseurs_id}, "
                f"montant_total={self.montant_total}, ordre_classement={self.ordre_classement})>")    
# Classe OffreTechnique
class OffreTechnique(Base):
    __tablename__ = 'offres_techniques'

    id = Column(Integer, primary_key=True, autoincrement=True)
    soumission_id = Column(Integer, ForeignKey('soumissions.id'), nullable=False)
    produit_id = Column(Integer, ForeignKey('produits.id'), nullable=False)
    specifications = Column(String(500), nullable=True)
    exclure = Column(Boolean, default=False)  # New field to indicate exclusion

    soumission = relationship("Soumission", backref="offres_techniques")
    produit = relationship("Produit", backref="offres_techniques")

    def __repr__(self):
        return f"<OffreTechnique(id={self.id}, soumission_id={self.soumission_id}, produit_id={self.produit_id})>"

# Classe OffreFinanciere
class OffreFinanciere(Base):
    __tablename__ = 'offres_financieres'

    id = Column(Integer, primary_key=True, autoincrement=True)
    soumission_id = Column(Integer, ForeignKey('soumissions.id'), nullable=False)
    produit_id = Column(Integer, ForeignKey('produits.id'), nullable=False)

    prix_unitaire = Column(Float, nullable=False)
    unite_monetaire = Column(String(255), nullable=True)  # True for MRU, False for other currencies
    taux_echange = Column(Float, nullable=True)  # Exchange rate (nullable for MRU)
    prix_unitaire_mru = Column(Float, nullable=False)  # Calculated price in MRU
    qte = Column(Float, nullable=False)
    prix_total = Column(Float, nullable=False)
    
    
    ordre_classement = Column(Integer, nullable=True)  # Nouveau champ pour l'ordre de classement
    exclure = Column(Boolean, default=False)  # New field to indicate exclusion

    soumission = relationship("Soumission", backref="offres_financieres")
    produit = relationship("Produit", backref="offres_financieres")

    def __repr__(self):
        return (f"<OffreFinanciere(id={self.id}, soumission_id={self.soumission_id}, produit_id={self.produit_id}, "
                f"prix_unitaire={self.prix_unitaire}, unite_monetaire={self.unite_monetaire}, "
                f"taux_echange={self.taux_echange}, prix_unitaire_mru={self.prix_unitaire_mru}, "
                f"qte={self.qte}, prix_total={self.prix_total})>")
    
    # Method to calculate `taux_echange` and `prix_unitaire_mru`
    def calculate_prix_unitaire_mru(self):
        if self.unite_monetaire:  # True for MRU
            self.taux_echange = 1
            self.prix_unitaire_mru = self.prix_unitaire
        else:  # False for other currencies
            if not self.taux_echange:
                raise ValueError("Taux d'échange must be defined for non-MRU currencies.")
            self.prix_unitaire_mru = self.taux_echange * self.prix_unitaire


class Caution(Base):
    __tablename__ = 'cautions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    montant = Column(Float, nullable=False)  # Montant de la caution
    date_validite = Column(Date, nullable=True)  # Date de validité (facultative si jusqu'à main levée)
    jusqu_a_main_levee = Column(Boolean, default=False)  # Indique si la caution est valable jusqu'à main levée
    caution_pdf = Column(LargeBinary, nullable=True)  # Fichier PDF de la caution
    caution_pdf_filename = Column(String(255), nullable=True)  # Nom du fichier PDF de la caution
    is_fournie = Column(Boolean, default=False) # Si ke soumissionnaire a fournie une caution
    type_caution = Column(String(50), nullable=False)  # Type de caution (soumission ou bonne exécution)

    __mapper_args__ = {
        'polymorphic_on': type_caution,  # Discriminator column
        'polymorphic_identity': 'caution'  # Identity for the base class
    }

    def __repr__(self):
        return (f"<Caution(id={self.id}, montant={self.montant}, date_validite={self.date_validite}, "
                f"jusqu_a_main_levee={self.jusqu_a_main_levee}, caution_pdf_filename='{self.caution_pdf_filename}', "
                f"type_caution='{self.type_caution}')>")
    

class CautionSoumission(Caution):
    __tablename__ = 'cautions_soumissions'

    id = Column(Integer, ForeignKey('cautions.id'), primary_key=True)
    soumission_id = Column(Integer, ForeignKey('soumissions.id'), nullable=False)  # Lié à la soumission

    soumission = relationship("Soumission", backref="cautions_soumissions")

    __mapper_args__ = {
        'polymorphic_identity': 'caution_soumission'  # Identity for this subclass
    }

    def __repr__(self):
        return (f"<CautionSoumission(id={self.id}, soumission_id={self.soumission_id}, montant={self.montant}, "
                f"date_validite={self.date_validite}, caution_pdf_filename='{self.caution_pdf_filename}')>")
    
class CautionBonneExecution(Caution):
    __tablename__ = 'cautions_bonne_execution'

    id = Column(Integer, ForeignKey('cautions.id'), primary_key=True)
    attribution_id = Column(Integer, ForeignKey('attributions_marches.id'), nullable=False)  # Lié à l'attribution de marché

    attribution = relationship("AttributionMarche", backref="cautions_bonne_execution")

    __mapper_args__ = {
        'polymorphic_identity': 'caution_bonne_execution'  # Identity for this subclass
    }

    def __repr__(self):
        return (f"<CautionBonneExecution(id={self.id}, attribution_id={self.attribution_id}, montant={self.montant}, "
                f"date_validite={self.date_validite}, caution_pdf_filename='{self.caution_pdf_filename}')>")
    

class Contrat(Base):
    __tablename__ = 'contrats'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fournisseur_id = Column(Integer, ForeignKey('fournisseurs.id'), nullable=False)
    marche_id = Column(Integer, ForeignKey('marches.id'), nullable=False)  # Links to either ConsultationFournisseurs or EntenteDirecte
    date_signature = Column(Date, nullable=False)  # Date of signature
    date_approbation = Column(Date, nullable=True)  # Date of approval
    date_notification = Column(Date, nullable=True)  # Date of notification
    mode_paiement = Column(Enum('Lettre de Crédit', 'Virement Bancaire', name='mode_paiement_enum'), nullable=False)  # Payment mode
    contrat_pdf = Column(LargeBinary, nullable=True)  # PDF file for the signed contract
    contrat_pdf_filename = Column(String(255), nullable=True)  # Filename for the signed contract

    fournisseur = relationship("Fournisseur", backref="contrats")
    marche = relationship("Marche", backref="contrats")
    produits = relationship("ProduitContrat", backref="contrat")  # Relationship to products in the contract

    def __repr__(self):
        return (f"<Contrat(id={self.id}, fournisseur_id={self.fournisseur_id}, marche_id={self.marche_id}, "
                f"date_signature={self.date_signature}, mode_paiement='{self.mode_paiement}')>")


class ProduitContrat(Base):
    __tablename__ = 'produits_contrats'

    id = Column(Integer, primary_key=True, autoincrement=True)
    contrat_id = Column(Integer, ForeignKey('contrats.id'), nullable=False)  # Links to the Contrat
    produit_id = Column(Integer, ForeignKey('produits.id'), nullable=False)  # Links to the Produit
    quantite = Column(Float, nullable=False)  # Quantity of the product in the contract
    marge = Column(Float, default=5.0)  # Margin of +/- 5%
    prix_unitaire = Column(Float, nullable=False)  # Unit price of the product

    produit = relationship("Produit", backref="produits_contrats")

    def __repr__(self):
        return (f"<ProduitContrat(id={self.id}, contrat_id={self.contrat_id}, produit_id={self.produit_id}, "
                f"quantite={self.quantite}, prix_unitaire={self.prix_unitaire})>")
    

class LettreDeCredit(Base):
    __tablename__ = 'lettres_de_credit'

    id = Column(Integer, primary_key=True, autoincrement=True)
    contrat_id = Column(Integer, ForeignKey('contrats.id'), nullable=False)  # Links to the Contrat
    duree_paiement = Column(String(255), nullable=False)  # Payment duration
    conditions_livraison = Column(String(500), nullable=False)  # Delivery conditions
    lettre_ouverture = Column(LargeBinary, nullable=True)  # Opening letter (PDF or image)
    lettre_ouverture_filename = Column(String(255), nullable=True)  # Filename for the opening letter
    lc_pdf = Column(LargeBinary, nullable=True)  # PDF file for the LC
    lc_pdf_filename = Column(String(255), nullable=True)  # Filename for the LC

    contrat = relationship("Contrat", backref="lettres_de_credit")

    def __repr__(self):
        return (f"<LettreDeCredit(id={self.id}, contrat_id={self.contrat_id}, "
                f"duree_paiement='{self.duree_paiement}', conditions_livraison='{self.conditions_livraison}')>")
    
class Livraison(Base):
    __tablename__ = 'livraisons'

    id = Column(Integer, primary_key=True, autoincrement=True)
    contrat_id = Column(Integer, ForeignKey('contrats.id'), nullable=False)  # Links to the Contrat
    produit_id = Column(Integer, ForeignKey('produits.id'), nullable=False)  # Links to the delivered product
    quantite_livree = Column(Float, nullable=False)  # Delivered quantity
    

    contrat = relationship("Contrat", backref="livraisons")
    produit = relationship("Produit", backref="livraisons")

    def __repr__(self):
        return (f"<Livraison(id={self.id}, contrat_id={self.contrat_id}, produit_id={self.produit_id}, "
                f"quantite_livree={self.quantite_livree}, marge={self.marge})>")
    
class PVReception(Base):
    __tablename__ = 'pv_receptions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    contrat_id = Column(Integer, ForeignKey('contrats.id'), nullable=False)  # Links to the Contrat
    pv_reception = Column(LargeBinary, nullable=False)  # Reception report (PDF or image)
    pv_reception_filename = Column(String(255), nullable=False)  # Filename for the reception report

    contrat = relationship("Contrat", backref="pv_receptions")

    def __repr__(self):
        return (f"<PVReception(id={self.id}, contrat_id={self.contrat_id}, "
                f"pv_reception_filename='{self.pv_reception_filename}')>")