from flask import Blueprint, request, jsonify
from ..models import Product
from .. import db

product_bp = Blueprint('products', __name__)

# Récupérer tous les produits
@product_bp.route('/', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{"id": p.id, "name": p.name, "price": p.price, "stock": p.stock} for p in products])

# Ajouter un produit
@product_bp.route('/', methods=['POST'])
def add_product():
    data = request.json
    new_product = Product(name=data['name'], price=data['price'], stock=data['stock'])
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message": "Produit ajouté avec succès!"}), 201