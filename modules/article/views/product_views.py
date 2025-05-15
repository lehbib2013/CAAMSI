from flask import render_template, request, redirect, url_for, flash
from models.db import Session, Produit
from flask import Response,render_template, request, redirect, url_for, flash, jsonify
from modules.article import produits_bp
from models.db import Fournisseur, Session
from modules.fournisseur.repository.fournisseur import FournisseurRepository
from modules.fournisseur.service.fournisseur import FournisseurService
from sqlalchemy import create_engine
import os
from werkzeug.utils import secure_filename
from io import BytesIO
from fpdf import FPDF
import pandas as pd
from docx import Document

session = Session()

@produits_bp.route('/', methods=['GET'])
def list_produits():
    search_query = request.args.get('search', '').strip()
    query = session.query(Produit)
    if search_query:
        query = query.filter(Produit.nom.ilike(f'%{search_query}%'))
    produits = query.all()
    print("produits")
    print(produits)
    return render_template('produits/liste_produits.html', produits=produits)

@produits_bp.route('/ajouter', methods=['GET', 'POST'])
def ajouter_produit():
    if request.method == 'POST':
        nom = request.form.get('nom')
        description = request.form.get('description')
        prix_achat = float(request.form.get('prix_achat'))
        stock = int(request.form.get('stock'))
        categorie = request.form.get('categorie')
        disponible = request.form.get('disponible') == 'on'

        produit = Produit(
            nom=nom,
            description=description,
            prix_achat=prix_achat,
            stock=stock,
            categorie=categorie,
            disponible=disponible
        )
        try:
            session.add(produit)
            session.commit()
            flash('Produit ajouté avec succès!', 'success')
            return redirect(url_for('produits.list_produits'))
        except Exception as e:
            session.rollback()
            flash(f'Erreur: {str(e)}', 'danger')

    return render_template('produits/ajouter_produit.html')

@produits_bp.route('/produits/<int:id>/edit', methods=['GET', 'POST'])
def edit_produit(id):
    produit = session.query(Produit).get(id)
    if not produit:
        flash('Produit introuvable.', 'error')
        return redirect(url_for('produits.list_produits'))

    if request.method == 'POST':
        produit.nom = request.form.get('nom')
        produit.description = request.form.get('description')
        produit.prix_achat = float(request.form.get('prix_achat'))
        produit.stock = int(request.form.get('stock'))
        produit.categorie = request.form.get('categorie')
        produit.disponible = request.form.get('disponible') == 'on'

        try:
            session.commit()
            flash('Produit modifié avec succès.', 'success')
            return redirect(url_for('produits.list_produits'))
        except Exception as e:
            session.rollback()
            flash(f'Erreur lors de la mise à jour: {str(e)}', 'danger')

    return render_template('produits/edit_produit.html', produit=produit)

@produits_bp.route('/produits/<int:id>/delete', methods=['POST'])
def delete_produit(id):
    produit = session.query(Produit).get(id)
    if not produit:
        flash('Produit introuvable.', 'error')
        return redirect(url_for('produits.list_produits'))

    try:
        session.delete(produit)
        session.commit()
        flash('Produit supprimé avec succès.', 'success')
    except Exception as e:
        session.rollback()
        flash(f'Erreur lors de la suppression: {str(e)}', 'danger')

    return redirect(url_for('produits.list_produits'))