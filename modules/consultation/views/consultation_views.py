from flask import jsonify, render_template, request, redirect, url_for, flash
from sqlalchemy import func
from models.db import AttributionMarche,CautionSoumission, CriteresQualificationEnum, Fournisseur, Marche, MarchePart, MarcheProduit, OffreFinanciere, OffreTechnique, Produit, Session, ConsultationFournisseurs, Soumission, StatutEnum
from modules.consultation import consultation_bp
from datetime import datetime, date
from flask_wtf.csrf import generate_csrf
from sqlalchemy.orm import joinedload
from flask import Response
from werkzeug.utils import secure_filename
import os

@consultation_bp.route('/', methods=['GET'])
def list_consultations():
    session = Session()
    try:
        # Eagerly load the marche_produits relationship
        consultations = session.query(ConsultationFournisseurs).options(joinedload(ConsultationFournisseurs.marche_produits)).all()
       

       
                
        return render_template('passation/consultations.html', consultations=consultations )
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'danger')
        return render_template('passation/consultations.html', consultations=[])
    finally:
        session.close()
@consultation_bp.route('/<int:consultation_id>', methods=['GET'])
def view_consultation(consultation_id):
    print(f"Received consultation_id: {consultation_id}")  # Debug statement
    session = Session()
    try:
        
        if consultation_id == 0:
            produits = session.query(Produit).all()
            fournisseurs = session.query(Fournisseur).all()  # Fetch all fournisseurs
            active_tab = 'details'
            print("you are here ...............")
            return render_template('passation/view_consultation.html', consultation=None, produits=produits, active_tab=active_tab)

        # Fetch the consultation and associated products
        consultation = session.query(ConsultationFournisseurs).options(joinedload(ConsultationFournisseurs.marche_produits)).get(consultation_id)
        if not consultation:
            flash('Consultation not found!', 'danger')
            return redirect(url_for('consultations.list_consultations'))

        produits = session.query(Produit).all()
        fournisseurs = session.query(Fournisseur).all() 
        active_tab = request.args.get('tab', 'details')
         # Get all statuses from StatutEnum
        #all_statuses = [status.value for status in StatutEnum]


        steps = [
            {"name": "Lancement", "done": consultation.demande_cotation and consultation.liste_fournisseurs_consulter and consultation.ppm_ou_justificatif_achat and consultation.pv_designation_comission_ad_hoc and consultation.numero_rfq and consultation.voie_soumission, "blocked": False},
            {"name": "Ouverture", "done": consultation.date_ouverture and consultation.pv_ouverture, "blocked": False},
            {"name": "Évaluation", "done": consultation.date_evaluation and consultation.pv_evaluation, "blocked": False},
            {"name": "Attribution provisoire", "done": consultation.pv_attribution_filename is not None and consultation.pv_attribution_filename != "","blocked": False},
            {"name": "Contrat", "done":  consultation.contrat, "blocked": False},
            {"name": "Numérotation", "done": consultation.numerotation, "blocked": False},
        ]

        # Bloquer les étapes supérieures si une étape inférieure n'est pas terminée
        for i in range(1, len(steps)):
           if not steps[i - 1]["done"]:
                steps[i]["blocked"] = True
        # Ajouter l'attribut 'archived'
        for i, step in enumerate(steps):
            if step["done"]:
                # Si ce n'est pas la dernière étape, archived est True
                if i < len(steps) - 1:
                    step["archived"] = True
                else:
                    # Si c'est la dernière étape et qu'elle est terminée, archived est False
                    step["archived"] = False
            else:
                # Si l'étape n'est pas terminée, archived est False
                step["archived"] = False

       
        # Get the current status of the consultation
        current_status = consultation.statut.value
        return render_template('passation/view_consultation.html', consultation=consultation, produits=produits, fournisseurs=fournisseurs, active_tab=active_tab,steps=steps,
            current_status=current_status)
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'danger')
        return redirect(url_for('consultations.list_consultations'))
    finally:
        session.close()

@consultation_bp.route('/<int:consultation_id>/add_products', methods=['POST'])
def add_products(consultation_id):
    session = Session()
    try:
        produit_id = request.form['produit_id']
        quantite = request.form['quantite']

        # Fetch the product details
        produit = session.query(Produit).get(produit_id)
        if not produit:
            return jsonify({'success': False, 'message': 'Produit introuvable!'})

        # Add the product to the consultation
        marche_produit = MarcheProduit(
            marche_id=consultation_id,
            produit_id=produit_id,
            quantite=quantite
        )
        session.add(marche_produit)
        session.commit()

        # Return the product details as JSON
        return jsonify({
            'success': True,
            'product': {
                'id': marche_produit.id,
                'nom': produit.nom,
                'quantite': marche_produit.quantite
            }
        })
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'message': str(e)})
    finally:
        session.close()



@consultation_bp.route('/delete_product', methods=['POST'])
def delete_product():
    data = request.get_json()
    session = Session()
    print("........produit id ......:" )
    print(data['produit_id'] )
    print(".......consultation_id....... :" )
    print(data['consultation_id'] )
    try:
        produit_id = data['produit_id']
        consultation_id = data['consultation_id']
        

        marche_produit = session.query(MarcheProduit).get(produit_id)
        if marche_produit:
            session.delete(marche_produit)
            session.commit()
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Produit non trouvé'})
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'message': str(e)})
    finally:
        session.close()

@consultation_bp.route('/edit_product', methods=['POST'])
def edit_product():
    data = request.get_json()
    session = Session()
    try:
        produit_id = data['produit_id']
        quantite = data['quantite']
        consultation_id = data['consultation_id']

        marche_produit = session.query(MarcheProduit).get(produit_id)
        if marche_produit:
            marche_produit.quantite = quantite
            session.commit()
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Produit non trouvé'})
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'message': str(e)})
    finally:
        session.close()

  #   render roducts of MarcheProduit
@consultation_bp.route('/<int:consultation_id>/products', methods=['GET'])
def get_products(consultation_id):
    session = Session()
    try:
        consultation = session.query(ConsultationFournisseurs).get(consultation_id)
        if not consultation:
            return '', 404  # Return 404 if consultation is not found

        # Render only the table rows as a partial template
        return render_template('passation/products_table.html', consultation=consultation)
    finally:
        session.close()

@consultation_bp.route('/add', methods=['GET', 'POST'])
def add_consultation():
    session = Session()
    try:
        if request.method == 'POST':
            # Handle form submission logic here
            designation = request.form['designation']
            voie_soumission = request.form['voie_soumission']
            criteres_qualification = request.form['criteres_qualification']
            numero_rfq = request.form['numero_rfq']
            date_lancement = request.form['date_lancement']

            # Handle file uploads
            liste_fournisseurs = request.files['liste_fournisseurs']
            demande_cotation = request.files['demande_cotation']
            ppm_justificatif = request.files['ppm_justificatif']
            commission_ad_hoc = request.files['commission_ad_hoc']
            
            

            # Save file data as binary (if files are uploaded)
            liste_fournisseurs_data = liste_fournisseurs.read() if liste_fournisseurs else None
            demande_cotation_data = demande_cotation.read() if demande_cotation else None
            ppm_justificatif_data = ppm_justificatif.read() if ppm_justificatif else None
            commission_ad_hoc_data = commission_ad_hoc.read() if commission_ad_hoc else None
            

            # Create a new ConsultationFournisseurs object
            consultation = ConsultationFournisseurs(
                designation=designation,
                voie_soumission=voie_soumission,
                criteres_qualification=CriteresQualificationEnum[criteres_qualification],  # Convert to Enum
                numero_rfq=numero_rfq,
                date_lancement=date_lancement,
                liste_fournisseurs_consulter=liste_fournisseurs_data,
                demande_cotation=demande_cotation_data,
                ppm_ou_justificatif_achat=ppm_justificatif_data,
                pv_designation_comission_ad_hoc=commission_ad_hoc_data,
                
            )
            session.add(consultation)
            session.commit()
            flash('Consultation ajoutée avec succès!', 'success')
            return redirect(url_for('consultations.view_consultation', consultation_id=consultation.id, tab='products'))
        # Pass CSRF token to the template
        # csrf_token = generate_csrf()
        # Pass an empty placeholder for consultation and a list of products
        produits = session.query(Produit).all()
        return render_template('passation/add_consultation.html')
       # return jsonify({'success': True, 'consultation_id': consultation.id})
    except Exception as e:
        session.rollback()
        #flash(f'Erreur: {str(e)}', 'danger')
        flash(f'Erreur: {str(e)}', 'danger')
        return redirect(url_for('consultations.list_consultations'))
        #return jsonify({'success': False, 'message': str(e)})
    finally:
        session.close()




@consultation_bp.route('/delete/<int:id>', methods=['POST'])
def delete_consultation(id):
    session = Session()
    try:
        # Fetch the consultation
        consultation = session.query(ConsultationFournisseurs).get(id)
        if not consultation:
            flash('Consultation not found!', 'danger')
            return redirect(url_for('consultations.list_consultations'))

        # Delete associated rows in MarcheProduit
        session.query(MarcheProduit).filter_by(marche_id=id).delete()

        # Delete the consultation
        session.delete(consultation)
        session.commit()
        flash('Consultation deleted successfully!', 'success')
    except Exception as e:
        session.rollback()
        flash(f'Error deleting consultation: {str(e)}', 'danger')
    finally:
        session.close()
    return redirect(url_for('consultations.list_consultations'))

@consultation_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_consultation(id):
    session = Session()
    consultation = session.query(ConsultationFournisseurs).get(id)
    if not consultation:
        flash('Consultation not found!', 'danger')
        return redirect(url_for('consultations.list_consultations'))
   
   # Ensure date_lancement is a datetime object when rendering the form
    if consultation.date_lancement and isinstance(consultation.date_lancement, date):
        consultation.date_lancement = datetime.combine(consultation.date_lancement, datetime.min.time())

    if request.method == 'POST':
        try:
            # Retrieve form data
            consultation.designation = request.form['designation']
            consultation.voie_soumission = request.form['voie_soumission']
            consultation.criteres_qualification = CriteresQualificationEnum[request.form['criteres_qualification']]
            consultation.numero_rfq = request.form['numero_rfq']
            
            #consultation.date_lancement = request.form['date_lancement']
           # Parse and update date_lancement
            # Parse and update date_lancement
            date_lancement = request.form['date_lancement']
            if date_lancement:
                consultation.date_lancement = datetime.strptime(date_lancement, '%Y-%m-%dT%H:%M')
            print("date_lancement......................")
            print(consultation.date_lancement)

            # Handle file uploads
            liste_fournisseurs = request.files['liste_fournisseurs']
            demande_cotation = request.files['demande_cotation']
            ppm_justificatif = request.files['ppm_justificatif']
            commission_ad_hoc = request.files['commission_ad_hoc']
            
            
            # Update file data if new files are uploaded
            if liste_fournisseurs:
                consultation.liste_fournisseurs_consulter = liste_fournisseurs.read()
            if demande_cotation:
                consultation.demande_cotation = demande_cotation.read()
            if ppm_justificatif:
                consultation.ppm_ou_justificatif_achat = ppm_justificatif.read()
            if commission_ad_hoc:
                consultation.pv_designation_comission_ad_hoc = commission_ad_hoc.read()

            if (consultation.demande_cotation and consultation.liste_fournisseurs_consulter and
                consultation.ppm_ou_justificatif_achat and consultation.pv_designation_comission_ad_hoc and
                consultation.numero_rfq and consultation.voie_soumission):
                consultation.statut = StatutEnum.LANCE


  # Lancement : demande de cotation, list des fournisseur a consulter,Justif  ppm, note service comission ad hoc, numero refq + voie de la soumission
  # ouverture : date ouvertur , pv ouverture   
  # Evaluation : date evaluation + pv evaluation
  # INFRUCTEUSE : decalaration infructure
  # attribution provisoire : pv attribution
  # attribution definitive : presentation des cautions si presentation_cautions est est true, otherwise l attribution definitive sera true meme que attribution provisoire en meme temps
  # nnulation: c est une case a cocher et si ca exist, il faut  faire paraitre u step graphic et sinon il faut le disparaitre
  # contrat : c est une case a cocher 
  # numerotation  c est une case a cocher evenement de numerotation

  #  
  # 
        
            #consultation.infructure = 'infructure' in request.form
            #consultation.cautions_presentees = 'cautions_presentees' in request.form
            #consultation.annulation = 'annulation' in request.form

            # Update note field
            consultation.note = request.form['note']
            
            # Commit changes
            session.commit()
            flash('Consultation updated successfully!', 'success')
        except Exception as e:
            session.rollback()
            flash(f'Error updating consultation: {str(e)}', 'danger')
        finally:
            session.close()
        return redirect(url_for('consultations.list_consultations'))

    session.close()
    return render_template('passation/edit_consultation.html', consultation=consultation)


@consultation_bp.route('/<int:id>/update_ouverture', methods=['POST'])
def update_ouverture(id):
    session = Session()
    try:
        # Fetch the consultation by ID
        consultation = session.query(ConsultationFournisseurs).get(id)
        if not consultation:
            flash('Consultation not found!', 'danger')
            return redirect(url_for('consultations.view_consultation', consultation_id=id))

        # Update the date_ouverture field
        date_ouverture = request.form.get('date_ouverture')
        if date_ouverture:
            consultation.date_ouverture = date_ouverture

        # Handle file upload for pv_ouverture
        pv_ouverture = request.files.get('pv_ouverture')
        if pv_ouverture:
            consultation.pv_ouverture = pv_ouverture.read()
            consultation.pv_ouverture_filename = pv_ouverture.filename
        if consultation.date_ouverture and consultation.pv_ouverture:
            consultation.statut = StatutEnum.OUVERT
        if consultation.date_ouverture and consultation.pv_ouverture:
            consultation.statut = StatutEnum.OUVERT

        # Commit the changes to the database
        session.commit()
        flash('Informations sur l\'ouverture mises à jour avec succès!', 'success')
    except Exception as e:
        session.rollback()
        flash(f'Erreur lors de la mise à jour des informations d\'ouverture: {str(e)}', 'danger')
    finally:
        session.close()

    return redirect(url_for('consultations.view_consultation', consultation_id=id, tab='ouverture'))


@consultation_bp.route('/<int:id>/download_pv_ouverture', methods=['GET'])
def download_pv_ouverture(id):
    session = Session()
    try:
        consultation = session.query(ConsultationFournisseurs).get(id)
        if not consultation or not consultation.pv_ouverture:
            flash('Fichier introuvable!', 'danger')
            return redirect(url_for('consultations.view_consultation', consultation_id=id))

        # Envoyer le fichier au client
        return Response(
            consultation.pv_ouverture,
            mimetype='application/octet-stream',
            headers={
                'Content-Disposition': f'attachment;filename={consultation.pv_ouverture_filename}'
            }
        )
    finally:
        session.close()

@consultation_bp.route('/<int:id>/update_evaluation', methods=['POST'])
def update_evaluation(id):
    session = Session()
    try:
        consultation = session.query(ConsultationFournisseurs).get(id)
        if not consultation:
            flash('Consultation introuvable!', 'danger')
            return redirect(url_for('consultations.view_consultation', consultation_id=id))

        # Mettre à jour la date d'évaluation
        date_evaluation = request.form.get('date_evaluation')
        if date_evaluation:
            consultation.date_evaluation = date_evaluation

        # Gérer le fichier pv_evaluation
        pv_evaluation = request.files.get('pv_evaluation')
        if pv_evaluation:
            consultation.pv_evaluation = pv_evaluation.read()
            consultation.pv_evaluation_filename = pv_evaluation.filename
        # Vérifier les conditions pour Évaluation
        if consultation.date_evaluation and consultation.pv_evaluation:
            consultation.statut = StatutEnum.EVALUE
        session.commit()
        flash('Évaluation mise à jour avec succès!', 'success')
    except Exception as e:
        session.rollback()
        flash(f'Erreur lors de la mise à jour de l\'évaluation: {str(e)}', 'danger')
    finally:
        session.close()

    return redirect(url_for('consultations.view_consultation', consultation_id=id, tab='evaluation'))

@consultation_bp.route('/<int:id>/update_infructueuse', methods=['POST'])
def update_infructueuse(id):
    session = Session()
    try:
        consultation = session.query(ConsultationFournisseurs).get(id)
        if not consultation:
            flash('Consultation introuvable!', 'danger')
            return redirect(url_for('consultations.view_consultation', consultation_id=id))

        # Mettre à jour le champ infructure
        consultation.infructure = 'infructure' in request.form

        # Vérifier les conditions pour l'étape "Infructueuse"
        if consultation.infructure:
            consultation.statut = StatutEnum.INFRUCTUEUSE

        session.commit()
        flash('Statut mis à jour à "Infructueuse" avec succès!', 'success')
    except Exception as e:
        session.rollback()
        flash(f'Erreur lors de la mise à jour du statut "Infructueuse": {str(e)}', 'danger')
    finally:
        session.close()

    return redirect(url_for('consultations.view_consultation', consultation_id=id, tab='infructueuse'))

@consultation_bp.route('/<int:id>/update_attribution_provisoire', methods=['POST'])
def update_attribution_provisoire(id):
    session = Session()
    try:
        consultation = session.query(ConsultationFournisseurs).get(id)
        if not consultation:
            flash('Consultation introuvable!', 'danger')
            return redirect(url_for('consultations.view_consultation', consultation_id=id))

        # Gérer le fichier pv_attribution
        pv_attribution = request.files.get('pv_attribution')
        if pv_attribution:
            consultation.pv_attribution = pv_attribution.read()
            consultation.pv_attribution_filename = pv_attribution.filename

        # Vérifier les conditions pour l'étape "Attribution provisoire"
        if consultation.pv_attribution:
            consultation.statut = StatutEnum.ATTRIBUEPROVIS
        if consultation.cautions_presentees == False:
            consultation.statut = StatutEnum.ATTRIBUDEFINITIVE

        session.commit()
        flash('Statut mis à jour à "Attribution provisoire" avec succès!', 'success')
    except Exception as e:
        session.rollback()
        flash(f'Erreur lors de la mise à jour du statut "Attribution provisoire": {str(e)}', 'danger')
    finally:
        session.close()

    return redirect(url_for('consultations.view_consultation', consultation_id=id, tab='attribution'))


@consultation_bp.route('/<int:id>/update_annulation', methods=['POST'])
def update_annulation(id):
    session = Session()
    try:
        consultation = session.query(ConsultationFournisseurs).get(id)
        if not consultation:
            flash('Consultation introuvable!', 'danger')
            return redirect(url_for('consultations.view_consultation', consultation_id=id))

        # Mettre à jour le champ annulation
        consultation.annulation = 'annulation' in request.form
        # Vérifier les conditions pour l'étape "Annulation"
        if consultation.annulation:
            consultation.statut = StatutEnum.ANNULATION

        session.commit()
        flash('Annulation mise à jour avec succès!', 'success')
    except Exception as e:
        session.rollback()
        flash(f'Erreur lors de la mise à jour de l\'annulation: {str(e)}', 'danger')
    finally:
        session.close()

    return redirect(url_for('consultations.view_consultation', consultation_id=id, tab='annulation'))

@consultation_bp.route('/<int:id>/update_attribution', methods=['POST'])
def update_attribution(id):
    session = Session()
    try:
        consultation = session.query(ConsultationFournisseurs).get(id)
        if not consultation:
            flash('Consultation introuvable!', 'danger')
            return redirect(url_for('consultations.view_consultation', consultation_id=id))

        # Gérer le fichier pv_attribution
        pv_attribution = request.files.get('pv_attribution')
        if pv_attribution:
            consultation.pv_attribution = pv_attribution.read()
            consultation.pv_attribution_filename = pv_attribution.filename

        # Vérifier les conditions pour l'étape "Attribution provisoire"
        if consultation.pv_attribution:
            consultation.statut = StatutEnum.ATTRIBUEPROVIS
        if consultation.presentation_caution == False:
            consultation.statut = StatutEnum.ATTRIBUDEFINITIVE


        session.commit()
        flash('Statut mis à jour à "Attribution provisoire" avec succès!', 'success')
    except Exception as e:
        session.rollback()
        flash(f'Erreur lors de la mise à jour du statut "Attribution provisoire": {str(e)}', 'danger')
    finally:
        session.close()

    return redirect(url_for('consultations.view_consultation', consultation_id=id, tab='contrat'))


@consultation_bp.route('/<int:id>/update_contrat', methods=['POST'])
def update_contrat(id):
    session = Session()
    try:
        consultation = session.query(ConsultationFournisseurs).get(id)
        if not consultation:
            flash('Consultation introuvable!', 'danger')
            return redirect(url_for('consultations.view_consultation', consultation_id=id))

        # Mettre à jour le champ contrat
        consultation.contrat = 'contrat' in request.form

        # Vérifier les conditions pour l'étape "Contrat"
        if consultation.contrat:
            consultation.statut = StatutEnum.CONTRAT

        session.commit()
        flash('Statut mis à jour à "Contrat" avec succès!', 'success')
    except Exception as e:
        session.rollback()
        flash(f'Erreur lors de la mise à jour du statut "Contrat": {str(e)}', 'danger')
    finally:
        session.close()

    return redirect(url_for('consultations.view_consultation', consultation_id=id, tab='numerotation'))



@consultation_bp.route('/<int:id>/update_resiliation', methods=['POST'])
def update_resiliationt(id):
    session = Session()
    try:
        consultation = session.query(ConsultationFournisseurs).get(id)
    except Exception as e:
        session.rollback()
        flash(f'Erreur lors de la mise à jour de la resiliation {str(e)}', 'danger')
    finally:
        session.close()

    return redirect(url_for('consultations.view_resiliation', consultation_id=id, tab='resiliation'))

@consultation_bp.route('/<int:id>/update_numerotation', methods=['POST'])
def update_numerotation(id):
    session = Session()
    try:
        consultation = session.query(ConsultationFournisseurs).get(id)
        if not consultation:
            flash('Consultation introuvable!', 'danger')
            return redirect(url_for('consultations.view_consultation', consultation_id=id))

        # Mettre à jour le champ numerotation
        consultation.numerotation = 'numerotation' in request.form

        # Vérifier les conditions pour l'étape "Numérotation"
        if consultation.numerotation:
            consultation.statut = StatutEnum.NUMEROTATION

        session.commit()
        flash('Statut mis à jour à "Numérotation" avec succès!', 'success')
    except Exception as e:
        session.rollback()
        flash(f'Erreur lors de la mise à jour du statut "Numérotation": {str(e)}', 'danger')
    finally:
        session.close()

    return redirect(url_for('consultations.view_consultation', consultation_id=id, tab='numerotation'))



# backend pour la partie soumission


@consultation_bp.route('/<int:id>/soumissions', methods=['GET'])
def get_soumissions(id):
    session = Session()
    try:
        soumissions = session.query(Soumission).filter_by(consultation_fournisseurs_id=id).all()
        return jsonify([{
            'id': s.id,
            'fournisseur': s.fournisseur.nom,
            'fournisseur_id': s.fournisseur_id,  # Include fournisseur_id
            'montant_total': s.montant_total,
            
        } for s in soumissions])
    finally:
        session.close()

@consultation_bp.route('/<int:id>/soumissions/add', methods=['POST'])
def add_soumission(id):
    session = Session()
    try:
        fournisseur_id = request.form['fournisseur_id']
        montant_total = request.form['montant_total']
        

        soumission = Soumission(
            consultation_fournisseurs_id=id,
            fournisseur_id=fournisseur_id,
            montant_total=0
        )
        session.add(soumission)
        session.commit()
                # Step 3: Retrieve the related Consultation object
        consultation = session.query(ConsultationFournisseurs).get(id)
        if not consultation:
            session.rollback()
            return jsonify({'success': False, 'error': 'Consultation not found.'}), 404

        # Step 4: Access all MarcheProduit associated with the Consultation
        marche_produits = session.query(MarcheProduit).filter_by(marche_id=id).all()


        # Step 5: Iterate over each MarcheProduit and create related objects
        for marche_produit in marche_produits:
            # Create and link an OffreTechnique object
            offre_technique = OffreTechnique(
                soumission_id=soumission.id,
                produit_id=marche_produit.produit_id,
                specifications=""
            )
            session.add(offre_technique)

            # Create and link an OffreFinanciere object
            offre_financiere = OffreFinanciere(
                soumission_id=soumission.id,
                produit_id=marche_produit.produit_id,
                prix_unitaire=0,
                unite_monetaire='MRU',
                qte=marche_produit.quantite ,
                taux_echange=1,
                prix_unitaire_mru= 0,
                prix_total=marche_produit.quantite * 0 ,
                ordre_classement=0,
                exclure=False,
            )
        
            session.add(offre_financiere)

            # Check if cautions_soumission is True and create a CautionDeSoumission object
            if consultation.cautions_soumission:
                caution_de_soumission = CautionSoumission(
                    soumission_id=soumission.id,
                    marche_produit_id=marche_produit.id,
                    montant=marche_produit.quantite * 50  # Example calculation, replace with actual logic
                )
                session.add(caution_de_soumission)

        # Step 6: Commit all changes to the database
        session.commit()
        return redirect(url_for('consultations.view_consultation', consultation_id=id, tab='ouverture'))
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'error': str(e)})
    finally:
        session.close()



@consultation_bp.route('/soumissions/<int:soumission_id>/delete', methods=['POST'])
def delete_soumission(soumission_id):
    session = Session()
    try:
        # Fetch the soumission by ID
        soumission = session.query(Soumission).get(soumission_id)
        if not soumission:
            flash('Soumission introuvable.', 'danger')
            return jsonify({'success': False, 'message': 'Soumission introuvable.'}), 404
        # Delete related objects
        session.query(OffreTechnique).filter_by(soumission_id=soumission_id).delete()
        session.query(OffreFinanciere).filter_by(soumission_id=soumission_id).delete()
        session.query(CautionSoumission).filter_by(soumission_id=soumission_id).delete()

        # Delete the soumission
        session.delete(soumission)
        session.commit()
        flash('Soumission supprimée avec succès.', 'success')
        return jsonify({'success': True}), 200
    except Exception as e:
        session.rollback()
        flash(f'Erreur lors de la suppression de la soumission : {str(e)}', 'danger')
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        session.close()

@consultation_bp.route('/<int:id>/products-soumisssion', methods=['GET'])
def get_products_soumission(id):
    session = Session()
    try:
        products = session.query(MarcheProduit).filter_by(marche_id=id).all()
        return jsonify([{
            'id': p.id,
            'name': p.produit.name,
            'specifications': p.specifications
        } for p in products])
    finally:
        session.close()

@consultation_bp.route('/soumissions/<int:soumission_id>/edit', methods=['POST'])
def edit_soumission(soumission_id):
    session = Session()
    try:
        soumission = session.query(Soumission).get(soumission_id)
        if not soumission:
            flash('Soumission introuvable.', 'danger')
            return redirect(url_for('consultations.view_consultation', consultation_id=soumission.consultation_fournisseurs_id, tab='ouverture'))

        # Update fields
        soumission.fournisseur_id = request.form['fournisseur_id']
        soumission.montant_total = request.form['montant_total']
       

        # Handle file upload
        if 'soumission_document' in request.files:
            soumission_document = request.files['soumission_document']
            if soumission_document.filename != '':
                filename = secure_filename(soumission_document.filename)
                file_path = os.path.join('static/uploads/soumissions', filename)
                soumission_document.save(file_path)
                soumission.document_path = file_path

        session.commit()
        flash('Soumission modifiée avec succès.', 'success')
        return redirect(url_for('consultations.view_consultation', consultation_id=soumission.consultation_fournisseurs_id, tab='ouverture'))
    except Exception as e:
        session.rollback()
        flash(f'Erreur lors de la modification de la soumission : {str(e)}', 'danger')
        return redirect(url_for('consultations.view_consultation', consultation_id=soumission.consultation_fournisseurs_id, tab='ouverture'))
    finally:
        session.close()


@consultation_bp.route('/soumissions/<int:soumission_id>/offres_techniques', methods=['GET'])
def get_offres_techniques(soumission_id):
    session = Session()
    try:
        # Fetch the Offres Techniques for the given soumission_id
        offres_techniques = session.query(OffreTechnique).filter_by(soumission_id=soumission_id).all()
        if not offres_techniques:
            return jsonify({'success': False, 'error': 'No technical offers found for this soumission.'}), 404

        # Return the data as JSON
        return jsonify([{
            'id': offre.id,
            'produit': offre.produit.nom if offre.produit else 'Unknown',
            'specifications': offre.specifications
            
        } for offre in offres_techniques])
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()



@consultation_bp.route('/soumissions/<int:soumission_id>/offres_financieres', methods=['GET'])
def get_offres_financieres(soumission_id):
    session = Session()
    try:
        offres_financieres = session.query(OffreFinanciere).filter_by(soumission_id=soumission_id).all()
        if not offres_financieres:
            return jsonify({'success': False, 'error': 'No financial offers found for this soumission.'}), 404
        return jsonify([{
            'id': offre.id,
            'produit': offre.produit.nom if offre.produit else 'Unknown',
            'prix_unitaire': offre.prix_unitaire,
            'unite_monetaire': offre.unite_monetaire,
            'taux_echange': offre.taux_echange,
            'prix_unitaire_mru': offre.prix_unitaire_mru,
            'qte': offre.qte,
            'prix_total': offre.prix_total,
            'total': offre.prix_total
        } for offre in offres_financieres])
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()

@consultation_bp.route('/soumissions/offres_financieres/<int:offre_id>/update', methods=['POST'])
def update_offre_financiere(offre_id):
    session = Session()
    try:
        data = request.get_json()
        offre = session.query(OffreFinanciere).get(offre_id)
        if not offre:
            return jsonify({'success': False, 'error': 'Offre not found'}), 404

        # Update the fields
        offre.qte = data.get('qte', offre.qte)
        offre.prix_unitaire = data.get('prix_unitaire', offre.prix_unitaire)
        offre.unite_monetaire = data.get('unite_monetaire', offre.unite_monetaire)
        offre.taux_echange = data.get('taux_echange', offre.taux_echange)
        offre.prix_unitaire_mru = data.get('prix_unitaire_mru', offre.prix_unitaire_mru)
        offre.prix_total = data.get('prix_total', offre.qte * offre.prix_unitaire * offre.taux_echange)
        # Update the total of the associated Soumission
        soumission_id = offre.soumission_id
        total = session.query(OffreFinanciere).filter_by(soumission_id=soumission_id).with_entities(
            func.sum(OffreFinanciere.prix_total)
        ).scalar()
        
        soumission = session.query(Soumission).get(soumission_id)
        if soumission:
            soumission.montant_total = total
            
        session.commit()
        return jsonify({'success': True, 'message': 'Offre updated successfully'})
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()

@consultation_bp.route('/soumissions/offres_techniques/<int:offre_id>/update', methods=['POST'])
def update_offre_technique(offre_id):
    session = Session()
    try:
        data = request.get_json()
        offre = session.query(OffreTechnique).get(offre_id)
        if not offre:
            return jsonify({'success': False, 'error': 'Offre not found'}), 404

        # Update the specifications field
        offre.specifications = data.get('specifications', offre.specifications)

        session.commit()
        return jsonify({'success': True, 'message': 'Offre updated successfully'})
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()


# LOTS Implementation

@consultation_bp.route('/marches/<int:marche_id>/add_part', methods=['POST'])
def add_marche_part(marche_id):
    session = Session()
    try:
        data = request.get_json()
        produit_id = data.get('produit_id')
        quantite = data.get('quantite')

        # Validate input
        if not produit_id or not quantite:
            return jsonify({'success': False, 'error': 'Produit ID and quantity are required'}), 400

        # Check if the product exists in the Marche
        marche_produit = session.query(MarcheProduit).filter_by(marche_id=marche_id, produit_id=produit_id).first()
        if not marche_produit:
            return jsonify({'success': False, 'error': 'Product not found in this Marche'}), 404

        # Add the part
        marche_part = MarchePart(marche_id=marche_id, produit_id=produit_id, quantite=quantite)
        session.add(marche_part)
        session.commit()

        # Validate quantities
        marche = session.query(Marche).get(marche_id)
        try:
            marche.validate_quantities(session)
        except ValueError as e:
            session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 400

        return jsonify({'success': True, 'message': 'Part added successfully'})
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()

@consultation_bp.route('/marches/<int:marche_id>/update_part/<int:part_id>', methods=['POST'])
def update_marche_part(marche_id, part_id):
    session = Session()
    try:
        data = request.get_json()
        quantite = data.get('quantite')

        # Validate input
        if not quantite:
            return jsonify({'success': False, 'error': 'Quantity is required'}), 400

        # Update the part
        marche_part = session.query(MarchePart).filter_by(id=part_id, marche_id=marche_id).first()
        if not marche_part:
            return jsonify({'success': False, 'error': 'Part not found'}), 404

        marche_part.quantite = quantite
        session.commit()

        # Validate quantities
        marche = session.query(Marche).get(marche_id)
        try:
            marche.validate_quantities(session)
        except ValueError as e:
            session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 400

        return jsonify({'success': True, 'message': 'Part updated successfully'})
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()



# classement des offres

@consultation_bp.route('/marches/<int:marche_id>/offres_financieres', methods=['GET'])
def compare_offres_financieres(marche_id):
    session = Session()
    attributed = False
    try:
        # Fetch the Marche
        marche = session.query(Marche).filter_by(id=marche_id).first()
        if not marche:
            print("Marche not found.")  # Debugging log
            return jsonify({'success': False, 'error': 'Marche not found'}), 404

        # Initialize a list to store attributions
        attributions = []

        # Check the criteres_qualification
        if marche.criteres_qualification == CriteresQualificationEnum.PAR_PRODUIT:
            # Group financial offers by produit_id and sort by ascending prix_unitaire_mru
            offres = (
                session.query(OffreFinanciere, Produit.nom.label('produit_nom'))
                .join(Soumission)
                .join(Produit, OffreFinanciere.produit_id == Produit.id) 
                .filter(Soumission.consultation_fournisseurs_id == marche_id)
                .order_by(OffreFinanciere.produit_id, OffreFinanciere.prix_unitaire_mru.asc())
                .all()
            )
            print(f"Found {len(offres)} financial offers.")  # Debugging log
            grouped_offres = {}
            for offre, produit_nom in offres:
                produit_id = offre.produit_id
                if produit_id not in grouped_offres:
                    grouped_offres[produit_id] = []
                grouped_offres[produit_id].append((offre, produit_nom))

            # Process attributions for each produit_id
            for produit_id, offres_list in grouped_offres.items():
                for offre, produit_nom in offres_list:
                    # Initialize existing_attribution to None
                    existing_attribution = None

                    # Check if the offer is excluded
                    if offre.exclure:
                        attributed = True
                    else:
                        # Check if an attribution already exists
                        existing_attribution = session.query(AttributionMarche).filter_by(
                            marche_id=marche_id,
                            fournisseur_id=offre.soumission.fournisseur_id,
                            produit_id=produit_id
                        ).first()

                        if existing_attribution:
                            print(f"Updating existing attribution ID: {existing_attribution.id}")  # Debugging log
                            # Update the existing attribution
                            existing_attribution.quantite = offre.qte
                            existing_attribution.prix_unitaire = offre.prix_unitaire_mru
                            existing_attribution.prix_total = offre.prix_total
                            existing_attribution.offre_technique = offre.soumission.soumission_document
                            existing_attribution.offre_technique_filename = offre.soumission.soumission_document_filename
                            existing_attribution.offre_financiere = offre.soumission.soumission_document
                            existing_attribution.offre_financiere_filename = offre.soumission.soumission_document_filename
                        else:
                            print(f"Creating new attribution for offer ID: {offre.id}")  # Debugging log
                            # Create a new attribution
                            new_attribution = AttributionMarche(
                                marche_id=marche_id,
                                fournisseur_id=offre.soumission.fournisseur_id,
                                produit_id=produit_id,
                                quantite=offre.qte,
                                prix_unitaire=offre.prix_unitaire_mru,
                                prix_total=offre.prix_total,
                                offre_technique=offre.soumission.soumission_document,
                                offre_technique_filename=offre.soumission.soumission_document_filename,
                                offre_financiere=offre.soumission.soumission_document,
                                offre_financiere_filename=offre.soumission.soumission_document_filename
                            )
                            session.add(new_attribution)
                            # Assign new_attribution to existing_attribution for consistency
                            existing_attribution = new_attribution

                    # Append the attribution details to the response
                    attributions.append({
                        'produit_id': produit_id,
                        'fournisseur_id': offre.soumission.fournisseur_id,
                        'produit_nom': produit_nom, 
                        'quantite': offre.qte,
                        'prix_unitaire': offre.prix_unitaire_mru,
                        'prix_total': offre.prix_total,
                        'offre_technique': offre.soumission.soumission_document,
                        'offre_technique_filename': offre.soumission.soumission_document_filename,
                        'offre_financiere': offre.soumission.soumission_document,
                        'offre_financiere_filename': offre.soumission.soumission_document_filename,
                        'exclure': offre.exclure,
                        'offre_id': offre.id,
                        'attribution_id': existing_attribution.id if existing_attribution else None,
                        'attributed': True if existing_attribution else False,
                        'marche_id': marche_id
                    })

        elif marche.criteres_qualification == CriteresQualificationEnum.PAR_OFFRE:
            # Sort soumissions by ascending montant_total
            soumissions = (
                session.query(Soumission)
                .filter(Soumission.consultation_fournisseurs_id == marche_id)
                .order_by(Soumission.montant_total.asc())
                .all()
            )

            # Save attributions for each soumission
            for soumission in soumissions:
                attribution = AttributionMarche(
                    marche_id=marche_id,
                    fournisseur_id=soumission.fournisseur_id,
                    produit_id=None,
                    quantite=None,
                    prix_unitaire=None,
                    prix_total=soumission.montant_total,
                    offre_technique=soumission.soumission_document,
                    offre_technique_filename=soumission.soumission_document_filename,
                    offre_financiere=soumission.soumission_document,
                    offre_financiere_filename=soumission.soumission_document_filename
                )
                session.add(attribution)
                attributions.append({
                    'fournisseur_id': soumission.fournisseur_id,
                    'montant_total': soumission.montant_total
                })

        else:
            return jsonify({'success': False, 'error': 'Invalid criteres_qualification'}), 400

        # Commit the attributions to the database
        session.commit()

        return jsonify({'success': True, 'data': attributions})
    except Exception as e:
        session.rollback()
        print(f"Error occurred: {str(e)}")  # Debugging log
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()

@consultation_bp.route('/marches/<int:marche_id>/attributions', methods=['POST'])
def create_or_update_attribution(marche_id):
    session = Session()
    try:
        data = request.get_json()


        # Find the corresponding Soumission using marche_id and fournisseur_id
        soumission = (
            session.query(Soumission)
            .filter_by(
                consultation_fournisseurs_id=marche_id,
                fournisseur_id=data['fournisseur_id']
            )
            .first()
        )

        if not soumission:
            print("Corresponding soumission not found.")  # Debugging log
            return jsonify({'success': False, 'error': 'Corresponding soumission not found'}), 404

        # Find the corresponding OffreFinanciere using soumission_id and produit_id
        offre = (
            session.query(OffreFinanciere)
            .filter_by(
                soumission_id=soumission.id,
                produit_id=data['produit_id']
            )
            .first()
        )

        if not offre:
            print("Corresponding offer not found.")  # Debugging log
            return jsonify({'success': False, 'error': 'Corresponding offer not found'}), 404

        # Update the offer's exclure field to False
        offre.exclure = False
        print(f"Updated offer ID {offre.id} with exclure = false")  # Debugging log

        # Commit the changes
        session.commit()
        return redirect(url_for('consultations.compare_offres_financieres', marche_id = marche_id))
    #jsonify({'success': True, 'message': 'Attribution created or updated successfully, and offer updated!'})
    except Exception as e:
        session.rollback()
        print(f"Error occurred: {str(e)}")  # Debugging log
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()

@consultation_bp.route('/soumissions/offres_financieres/<int:offre_id>/updateex', methods=['POST'])
def update_offre_financiere_eval(offre_id):
    session = Session()
    try:
        data = request.get_json()
        offre = session.query(OffreFinanciere).get(offre_id)
        if not offre:
            return jsonify({'success': False, 'error': 'Offre not found'}), 404

        # Update the exclure field
        offre.exclure = data.get('exclure', offre.exclure)

        session.commit()
        return jsonify({'success': True, 'message': 'Offre updated successfully'})
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()


@consultation_bp.route('/marches/attributions/<int:attribution_id>/delete', methods=['DELETE'])
def delete_attribution(attribution_id):
    session = Session()
    try:
        print(f"Attempting to delete attribution with ID: {attribution_id}")  # Debugging log

        # Query the AttributionMarche table directly using the attribution_id
        attribution = session.query(AttributionMarche).filter_by(id=attribution_id).first()

        if not attribution:
            print("Attribution not found for the given ID.")  # Debugging log
            return jsonify({'success': False, 'error': 'Attribution not found for the given ID'}), 404

        print(f"Found attribution with ID: {attribution.id}")  # Debugging log

        # Find the corresponding Soumission using marche_id and fournisseur_id
        soumission = (
            session.query(Soumission)
            .filter_by(
                consultation_fournisseurs_id=attribution.marche_id,
                fournisseur_id=attribution.fournisseur_id
            )
            .first()
        )

        if not soumission:
            print("Corresponding soumission not found.")  # Debugging log
            return jsonify({'success': False, 'error': 'Corresponding soumission not found'}), 404

        print(f"Found soumission with ID: {soumission.id}")  # Debugging log

        # Find the corresponding OffreFinanciere using soumission_id and produit_id
        offre = (
            session.query(OffreFinanciere)
            .filter_by(
                soumission_id=soumission.id,
                produit_id=attribution.produit_id
            )
            .first()
        )

        if not offre:
            print("Corresponding offer not found.")  # Debugging log
            return jsonify({'success': False, 'error': 'Corresponding offer not found'}), 404

        # Update the offer's exclure field
        offre.exclure = True
        print(f"Updated offer ID {offre.id} with exclure = true")  # Debugging log

        # Delete the attribution
        session.delete(attribution)
        session.commit()
        print("Attribution deleted and offer updated successfully.")  # Debugging log
        return jsonify({'success': True, 'message': 'Attribution deleted and offer updated successfully!'})
       # return jsonify({'success': True, 'message': 'Attribution deleted and offer updated successfully!'})
    except Exception as e:
        session.rollback()
        print(f"Error occurred: {str(e)}")  # Debugging log
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()