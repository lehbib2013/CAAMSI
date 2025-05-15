from datetime import datetime
from flask import render_template, request, redirect, url_for, flash
from models.db import CriteresQualificationEnum, Session, EntenteDirecte, StatutEnum
from modules.entente import entente_bp

@entente_bp.route('/', methods=['GET'])
def list_ententes():
    session = Session()
    ententes = session.query(EntenteDirecte).all()
    session.close()
    return render_template('ententes.html', ententes=ententes)

@entente_bp.route('/add', methods=['GET', 'POST'])
def add_entente():
    if request.method == 'POST':
        session = Session()
        try:
            # Debug: Log the received form data
            print("Form Data:", request.form)
            print("Files:", request.files)

            # Retrieve form data
            designation = request.form.get('designation')
            criteres_qualification = request.form.get('criteres_qualification')
           
            # Validate required fields
            if not designation or not criteres_qualification:
                flash('Les champs "Désignation" et "Critères de qualification" sont obligatoires.', 'danger')
                return redirect(url_for('ententes.add_entente'))

            # Map criteres_qualification to Enum
            criteres_qualification = CriteresQualificationEnum[criteres_qualification]

            # Handle file uploads
            pv_negociation = request.files['pv_negociation'].read() if 'pv_negociation' in request.files and request.files['pv_negociation'] else None
            pv_negociation_filename = request.files['pv_negociation'].filename if 'pv_negociation' in request.files and request.files['pv_negociation'] else None
            offre_technique = request.files['offre_technique'].read() if 'offre_technique' in request.files and request.files['offre_technique'] else None
            offre_technique_filename = request.files['offre_technique'].filename if 'offre_technique' in request.files and request.files['offre_technique'] else None
            offre_financiere = request.files['offre_financiere'].read() if 'offre_financiere' in request.files and request.files['offre_financiere'] else None
            offre_financiere_filename = request.files['offre_financiere'].filename if 'offre_financiere' in request.files and request.files['offre_financiere'] else None
            justificatif_recours = request.files['justificatif_recours'].read() if 'justificatif_recours' in request.files and request.files['justificatif_recours'] else None
            justificatif_recours_filename = request.files['justificatif_recours'].filename if 'justificatif_recours' in request.files and request.files['justificatif_recours'] else None

            # Create a new EntenteDirecte
            entente = EntenteDirecte(
                designation=designation,
                criteres_qualification=criteres_qualification,
               
                pv_negociation=pv_negociation,
                pv_negociation_filename=pv_negociation_filename,
                offre_technique=offre_technique,
                offre_technique_filename=offre_technique_filename,
                offre_financiere=offre_financiere,
                offre_financiere_filename=offre_financiere_filename,
                justificatif_recours=justificatif_recours,
                justificatif_recours_filename=justificatif_recours_filename
            )
            session.add(entente)
            session.commit()
            flash('Entente Directe ajoutée avec succès!', 'success')
        except Exception as e:
            session.rollback()
            flash(f'Erreur: {str(e)}', 'danger')
        finally:
            session.close()
        return redirect(url_for('ententes.list_ententes'))
    return render_template('passation/add_entente.html')

@entente_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_entente(id):
    session = Session()
    entente = session.query(EntenteDirecte).get(id)
    if not entente:
        flash('Entente Directe introuvable!', 'danger')
        return redirect(url_for('ententes.list_ententes'))

    if request.method == 'POST':
        try:
            entente.designation = request.form['designation']
            entente.criteres_qualification = CriteresQualificationEnum[request.form['criteres_qualification']]
            if 'pv_negociation' in request.files and request.files['pv_negociation']:
                entente.pv_negociation = request.files['pv_negociation'].read()
                entente.pv_negociation_filename = request.files['pv_negociation'].filename
            if 'offre_technique' in request.files and request.files['offre_technique']:
                entente.offre_technique = request.files['offre_technique'].read()
                entente.offre_technique_filename = request.files['offre_technique'].filename
            if 'offre_financiere' in request.files and request.files['offre_financiere']:
                entente.offre_financiere = request.files['offre_financiere'].read()
                entente.offre_financiere_filename = request.files['offre_financiere'].filename
            if 'justificatif_recours' in request.files and request.files['justificatif_recours']:
                entente.justificatif_recours = request.files['justificatif_recours'].read()
                entente.justificatif_recours_filename = request.files['justificatif_recours'].filename
            session.commit()
            flash('Entente Directe modifiée avec succès!', 'success')
        except Exception as e:
            session.rollback()
            flash(f'Erreur: {str(e)}', 'danger')
        finally:
            session.close()
        return redirect(url_for('ententes.list_ententes'))
    session.close()
    return render_template('passation/edit_entente.html', entente=entente)


@entente_bp.route('/delete/<int:id>', methods=['POST'])
def delete_entente(id):
    session = Session()
    entente = session.query(EntenteDirecte).get(id)
    session.delete(entente)
    session.commit()
    session.close()
    flash('Entente deleted successfully!')
    return redirect(url_for('entente.list_ententes'))