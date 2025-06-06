from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
import smtplib
from flask import Blueprint,request, jsonify,current_app,current_app as app,send_file
from service.dashboard import dashboard
from service.FacturePatient import insert_patient, get_id_patient, insert_facture, update_facture, delete_facture, get_facture, list_facture, get_code_facture, get_info_comptabilisation
from service.parametres import liste_operateur, liste_des_agences, liste_des_profils, liste_des_services, liste_des_parametres, modifier_des_agences, modifier_param
from service.comptabilisationOperation import pvgComptabilisationVersement, pvgComptabilisationOperationsFacture, pvgComptabilisationOperations, pvgComptabilisationOperationsCaisse
from service.edition import recu_edition,ExtourneOperation,ExtourneFacture, brouillard_caisse_edition,editionPatient, journal_edition, gd_livre_edition, balance_edition,point_par_acte_edition,formation_edition,solde_edition
from service.auth import connexion_utilisateur
from service.journee_de_travail_et_exercice import valeur_scalaire_requete_max, valeur_scalaire_requete_count, insert_journee_travail, table_libelle_date_systeme_serveur, liste_journee_travail, update_journee_travail_statut
from service.ChargementCombos import pvgSoldeCompteClient, pvgTableLabelAvecSolde, pvgComboTypeTiers,pvgComboJournal,get_solde_mouvement_comptable,pvgPeriodiciteDateDebutFin,pvgComboCompte,pvgComboTypeshemacomptable,pvgComboAssurance,pvgComboAssure,pvgComboActe,pvgComboModeReglement,pvgComboperiode,pvgComboTableLabelAgence,pvgComboOperateur,pvgComboExercice,pvgComboPeriodicite, pvgComboSexe, pvgComboProfession, liste_des_familles_operations, liste_des_operations, pvgComboPays, pvgComboVille,pvgComboOperateurCaisse,solde_du_compte
from service.auth import connexion_utilisateur,pvgUserChangePasswordfist,pvgUserDemandePassword
from service.Utilisateurs import creation_profil,update_profil,delete_profil,update_compte_utilisateur,insert_operateur,delete_compte_utilisateur,Activation_DesActivation_utilisateur
from service.Patient import ListePatient,insertpatient,deletepatient,ListeComptePatient
from service.Guichet import pvgComboTypeshemacomptableVersement,pvgChargerDansDataSetSC_SCHEMACOMPTABLECODE,pvgComboTypespiece
from models.models import clsObjetEnvoi
from datetime import datetime
import traceback
from utils import connect_database
from config import MYSQL_REPONSE
import random
import os
from tools.toolCodeFacture import generer_code_facture
from tools.toolDate import parse_datetime
from tools.toolJournee import test_journee_fermee,test_journee_fermeeVersement
api_bp = Blueprint('api', __name__)



################################################################
#                        GESTION DES PATIENTS                  #
################################################################
@api_bp.route('/insert_patient', methods=['POST'])
def pvginsert_patient():
    # Récupérer les données du corps de la requête
    request_data = request.json

    for row in request_data['Objet']:
        patient_info = {}

        try:
            # Validation des chaînes de caractères
            patient_info['PT_IDPATIENT'] = str(row.get('PT_IDPATIENT', ''))
            patient_info['PT_CODEPATIENT'] = str(row.get('PT_CODEPATIENT', ''))
            patient_info['PT_MATRICULE'] = str(row.get('PT_MATRICULE', ''))
            patient_info['AG_CODEAGENCE'] = str(row.get('AG_CODEAGENCE', ''))
            patient_info['PT_NOMPRENOMS'] = str(row.get('PT_NOMPRENOMS', ''))
            patient_info['PT_CONTACT'] = str(row.get('PT_CONTACT', ''))
            patient_info['PT_EMAIL'] = str(row.get('PT_EMAIL', ''))
            patient_info['PT_DATENAISSANCE'] = str(row.get('PT_DATENAISSANCE', ''))
            patient_info['PT_DATESAISIE'] = str(row.get('PT_DATESAISIE', ''))
            patient_info['PT_LIEUHABITATION'] = str(row.get('PT_LIEUHABITATION', ''))
            patient_info['PF_CODEPROFESSION'] = str(row.get('PF_CODEPROFESSION', ''))
            patient_info['SX_CODESEXE'] = str(row.get('SX_CODESEXE', ''))
            patient_info['STAT_CODESTATUT'] = str(row.get('STAT_CODESTATUT', ''))
            patient_info['OP_CODEOPERATEUR'] = str(row.get('OP_CODEOPERATEUR', ''))
            patient_info['PL_CODENUMCOMPTE'] = str(row.get('PL_CODENUMCOMPTE', ''))
            patient_info['TYPEOPERATION'] = str(row.get('TYPEOPERATION', ''))
            
            AG_CODEAGENCE = None
            JT_DATEJOURNEETRAVAIL = None
            OP_CODEOPERATEUR = None
            if request_data['Objet'][0]['clsObjetEnvoi'].get('OE_A', ''):
                AG_CODEAGENCE = str(request_data['Objet'][0]['clsObjetEnvoi'].get('OE_A', '')) 
            if request_data['Objet'][0]['clsObjetEnvoi'].get('OE_J', ''):
                JT_DATEJOURNEETRAVAIL  = str(request_data['Objet'][0]['clsObjetEnvoi'].get('OE_J', ''))
            if request_data['Objet'][0]['clsObjetEnvoi'].get('OE_Y', ''):
                OP_CODEOPERATEUR  = str(request_data['Objet'][0]['clsObjetEnvoi'].get('OE_Y', '')) 

            # Préparer les paramètres pour la fonction
            if AG_CODEAGENCE and JT_DATEJOURNEETRAVAIL and OP_CODEOPERATEUR:
                vpp_critere = (AG_CODEAGENCE, JT_DATEJOURNEETRAVAIL, OP_CODEOPERATEUR)
            elif AG_CODEAGENCE and JT_DATEJOURNEETRAVAIL:
                vpp_critere = (AG_CODEAGENCE, JT_DATEJOURNEETRAVAIL)
            elif AG_CODEAGENCE:
                vpp_critere = (AG_CODEAGENCE,)
            else:
                vpp_critere = ()
            

        except ValueError as e:
            # Retourner un message d'erreur en cas de problème de type de données
            return jsonify({"SL_MESSAGE": f"Erreur de type de données : {str(e)}", "SL_RESULTAT": 'FALSE'}), 200
        
        except Exception as e:
            # Retourner un message d'erreur en cas d'exception générale
            return jsonify({"SL_MESSAGE": f"Erreur inattendue : {str(e)}", "SL_RESULTAT": 'FALSE'}), 200

        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion:
                cursor = db_connexion.cursor()
                cursor.execute("BEGIN TRANSACTION")
                
                response = test_journee_fermee(cursor, *vpp_critere)

                if response[0]['NBRE'] == 0:
                    return jsonify({"SL_MESSAGE": 'Cette journée a été déjà fermée ou non encore ouverte !' ,"SL_RESULTAT": 'FALSE'})
        
                # Appeler la fonction d'insertion dans la base de données
                reponse = insertpatient(cursor, patient_info)
                
                # Valider la transaction
                # cursor.commit()
                get_commit(cursor,request_data)

            return jsonify({"SL_MESSAGE": "Insertion réussie!", "SL_RESULTAT": 'TRUE'}), 200

        except Exception as e:
            cursor.rollback()
            return jsonify({"SL_MESSAGE": f" {str(e)}", "SL_RESULTAT": 'FALSE'}), 200

        #finally:
            cursor.close()

            
            
@api_bp.route('/deletepatient', methods=['POST'])
def pvgdeletepatient():
    # Récupérer les données du corps de la requête
    request_data = request.json

    for row in request_data['Objet']:
        patient_info = {}

        try:
            # Validation des chaînes de caractères
            patient_info['PT_IDPATIENT'] = str(row.get('PT_IDPATIENT', ''))
            
        except ValueError as e:
            # Retourner un message d'erreur en cas de problème de type de données
            return jsonify({"SL_MESSAGE": f"Erreur de type de données : {str(e)}", "SL_RESULTAT": 'FALSE'}), 200
        
        except Exception as e:
            # Retourner un message d'erreur en cas d'exception générale
            return jsonify({"SL_MESSAGE": f"Erreur inattendue : {str(e)}", "SL_RESULTAT": 'FALSE'}), 200

        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion:
                cursor = db_connexion.cursor()
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction d'insertion dans la base de données
                reponse = deletepatient(cursor, patient_info)
                
                # Valider la transaction
                cursor.commit()

            return jsonify({"SL_MESSAGE": "Suppression réussie!", "SL_RESULTAT": 'TRUE'}), 200

        except Exception as e:
            cursor.rollback()
            return jsonify({"SL_MESSAGE": f" {str(e)}", "SL_RESULTAT": 'FALSE'}), 200

        #finally:
            cursor.close()  

@api_bp.route('/ListeComptePatient', methods=['POST'])
def pvgComptePatient():
    request_data = request.json
    
    if 'Objet' not in request_data:
        return jsonify({"SL_MESSAGE": "Données manquantes.code erreur (300) voir le noeud Objet", "SL_RESULTAT": 'FALSE'})
    
    for row in request_data['Objet']:
        Patient_info = {}

        # Validation et récupération des données pour la suppression
        Patient_info['AG_CODEAGENCE'] = str(row.get('AG_CODEAGENCE'))
        Patient_info['PT_CODEPATIENT'] = str(row.get('PT_CODEPATIENT'))
        Patient_info['TC_CODETYPETIERS'] = str(row.get('TC_CODETYPETIERS'))
        Patient_info['DATEDEBUT'] = str(row.get('DATEDEBUT'))
        Patient_info['DATEFIN'] = str(row.get('DATEFIN'))
        Patient_info['PT_MATRICULE'] = str(row.get('PT_MATRICULE'))
        Patient_info['PT_NOMPRENOMS'] = str(row.get('PT_NOMPRENOMS'))
        Patient_info['STAT_CODESTATUT'] = str(row.get('STAT_CODESTATUT'))
        Patient_info['PT_CONTACT'] = str(row.get('PT_CONTACT'))
        

        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = ListeComptePatient(db_connexion, Patient_info)
            
            if len(response) > 0:
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify([{"SL_MESSAGE": "Aucuns élement trouvé !!!", "SL_RESULTAT": 'FALSE'}])
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors du chargement : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close() 


@api_bp.route('/ListePatient', methods=['POST'])
def pvgListePatient():
    request_data = request.json
    
    if 'Objet' not in request_data:
        return jsonify({"SL_MESSAGE": "Données manquantes.code erreur (300) voir le noeud Objet", "SL_RESULTAT": 'FALSE'})
    
    for row in request_data['Objet']:
        Patient_info = {}

        # Validation et récupération des données pour la suppression
        Patient_info['AG_CODEAGENCE'] = str(row.get('AG_CODEAGENCE'))
        Patient_info['PT_CODEPATIENT'] = str(row.get('PT_CODEPATIENT'))
        Patient_info['DATEDEBUT'] = str(row.get('DATEDEBUT'))
        Patient_info['DATEFIN'] = str(row.get('DATEFIN'))
        Patient_info['PT_MATRICULE'] = str(row.get('PT_MATRICULE'))
        Patient_info['PT_NOMPRENOMS'] = str(row.get('PT_NOMPRENOMS'))
        Patient_info['STAT_CODESTATUT'] = str(row.get('STAT_CODESTATUT'))
        Patient_info['PT_CONTACT'] = str(row.get('PT_CONTACT'))
        

        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = ListePatient(db_connexion, Patient_info)
            
            if len(response) > 0:
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify([{"SL_MESSAGE": "Aucuns élement trouvé !!!", "SL_RESULTAT": 'FALSE'}])
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors du chargement : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()  
################################################################
#                        GESTION DES PATIENTS                  #
################################################################
################################################################
#                        GESTION DES FACTURES                                                                  #
################################################################

@api_bp.route('/creation_facture', methods=['POST'])
def pvgCreationFacture():
    # Récupérer les données du corps de la requête
    request_data = request.json
    
    if 'Objet' not in request_data:
        return jsonify({"SL_MESSAGE": "Données manquantes. Code erreur (300) voir le noeud Objet", "SL_RESULTAT": 'FALSE'})

    for row in request_data['Objet']:
        objet_facture = {}
        objet_facture['PT_CODEPATIENT'] = str(row.get('PT_CODEPATIENT', ''))
        objet_facture['PT_IDPATIENT'] = str(row.get('PT_IDPATIENT', ''))
        objet_facture['PT_MATRICULE'] = str(row.get('PT_MATRICULE', ''))
        objet_facture['AG_CODEAGENCE'] = str(row.get('AG_CODEAGENCE', ''))
        objet_facture['PT_NOMPRENOMS'] = str(row.get('PT_NOMPRENOMS', ''))
        objet_facture['PT_CONTACT'] = str(row.get('PT_CONTACT', ''))
        objet_facture['PT_EMAIL'] = str(row.get('PT_EMAIL', ''))
        objet_facture['PT_DATENAISSANCE'] = str(row.get('PT_DATENAISSANCE', ''))
        objet_facture['PT_DATESAISIE'] = str(row.get('PT_DATESAISIE', ''))
        objet_facture['PT_LIEUHABITATION'] = str(row.get('PT_LIEUHABITATION', ''))
        objet_facture['PF_CODEPROFESSION'] = str(row.get('PF_CODEPROFESSION', ''))
        objet_facture['SX_CODESEXE'] = str(row.get('SX_CODESEXE', ''))
        objet_facture['STAT_CODESTATUT'] = str(row.get('STAT_CODESTATUT', ''))
        objet_facture['OP_CODEOPERATEUR'] = str(row.get('OP_CODEOPERATEUR', ''))
        objet_facture['PL_CODENUMCOMPTE'] = str(row.get('PL_CODENUMCOMPTE', ''))
        # objet_facture['AS_CODEASSURANCE'] = str(row.get('AS_CODEASSURANCE', ''))
        objet_facture['MC_DATESAISIE'] = str(row.get('PT_DATESAISIE', ''))
        objet_facture['FT_ANNULATION'] = str(row.get('FT_ANNULATION', ''))
        objet_facture['TYPEOPERATION'] = str(row.get('TYPEOPERATION', ''))
        # objet_facture['ACT_CODEACTE'] = str(row.get('ACT_CODEACTE', ''))
        
        AG_CODEAGENCE = None
        JT_DATEJOURNEETRAVAIL = None
        OP_CODEOPERATEUR = None
        if request_data['Objet'][0]['clsObjetEnvoi'].get('OE_A', ''):
           AG_CODEAGENCE = str(request_data['Objet'][0]['clsObjetEnvoi'].get('OE_A', '')) 
        if request_data['Objet'][0]['clsObjetEnvoi'].get('OE_J', ''):
           JT_DATEJOURNEETRAVAIL  = str(request_data['Objet'][0]['clsObjetEnvoi'].get('OE_J', ''))
        if request_data['Objet'][0]['clsObjetEnvoi'].get('OE_Y', ''):
           OP_CODEOPERATEUR  = str(request_data['Objet'][0]['clsObjetEnvoi'].get('OE_Y', '')) 

        # Préparer les paramètres pour la fonction
        if AG_CODEAGENCE and JT_DATEJOURNEETRAVAIL and OP_CODEOPERATEUR:
            vpp_critere = (AG_CODEAGENCE, JT_DATEJOURNEETRAVAIL, OP_CODEOPERATEUR)
        elif AG_CODEAGENCE and JT_DATEJOURNEETRAVAIL:
            vpp_critere = (AG_CODEAGENCE, JT_DATEJOURNEETRAVAIL)
        elif AG_CODEAGENCE:
            vpp_critere = (AG_CODEAGENCE,)
        else:
            vpp_critere = ()
  
    # Connexion à la base de données
    db_connexion = connect_database()
    
    try:
        # with db_connexion.cursor() as cursor:
        cursor = db_connexion.cursor()
        cursor.execute("BEGIN TRANSACTION")

        response = test_journee_fermee(cursor, *vpp_critere)

        if response[0]['NBRE'] == 0:
            return jsonify({"SL_MESSAGE": 'Cette journée a été déjà fermée ou non encore ouverte !' ,"SL_RESULTAT": 'FALSE'})

        if objet_facture['TYPEOPERATION'] != '7':
            try:
                # creer le patient
                insert_patient(cursor, objet_facture)
            except ValueError as e:
                result = {}

                result['SL_MESSAGE'] = e
                result['SL_RESULTAT'] = "FALSE"
                # Ajouter le dictionnaire à la liste des résultats
                response.append(result)
        
                cursor.execute("ROLLBACK")
                return jsonify(response)
            
            # recuperer lid du patient
            id_patient = get_id_patient(cursor, objet_facture['OP_CODEOPERATEUR'])
            objet_facture['PT_IDPATIENT'] = id_patient[0]['PT_IDPATIENT']
        
        # creer la facture du patient
        try:
            # generer le code de la facture
            # objet_facture['FT_CODEFACTURE'] = generer_code_facture(objet_facture['AG_CODEAGENCE'])
            objet_facture['FT_CODEFACTURE'] = get_code_facture(cursor, objet_facture['AG_CODEAGENCE'], objet_facture['OP_CODEOPERATEUR'])
        except ValueError as e:
            result = {}

            result['SL_MESSAGE'] = e
            result['SL_RESULTAT'] = "FALSE"
            # Ajouter le dictionnaire à la liste des résultats
            response.append(result)

            cursor.execute("ROLLBACK")
            return jsonify(response)
        
        # creation de la facture
        insert_facture(cursor, objet_facture)
        
        # Consigner les mouvements
        clsmouvement_infos = []
        for row in request_data['Objet'][0]['TABLEMODEREGLEMENT']:
            objet_mode_reglement = {}
            try:
                objet_mode_reglement['MR_CODEMODEREGLEMENT'] = str(row.get('MR_CODEMODEREGLEMENT', ''))
                objet_mode_reglement['AG_CODEAGENCE'] = str(objet_facture['AG_CODEAGENCE'])
                objet_mode_reglement['MC_DATEPIECE'] = str(objet_facture['PT_DATESAISIE'])
                objet_mode_reglement['MC_NUMPIECE'] = str(row.get('MC_NUMPIECE', ''))
                objet_mode_reglement['MC_NUMSEQUENCE'] = str(row.get('MC_NUMSEQUENCE', ''))
                objet_mode_reglement['PT_IDPATIENT'] = str(objet_facture['PT_IDPATIENT'])
                objet_mode_reglement['FT_CODEFACTURE'] = str(objet_facture['FT_CODEFACTURE'])
                objet_mode_reglement['OP_CODEOPERATEUR'] = str(objet_facture['OP_CODEOPERATEUR'])
                objet_mode_reglement['MC_MONTANTDEBIT'] = row.get('MC_MONTANTDEBIT', '')
                objet_mode_reglement['MC_MONTANTCREDIT'] = row.get('MC_MONTANTCREDIT', '')
                objet_mode_reglement['MC_DATESAISIE'] = str(objet_facture['PT_DATESAISIE'])
                objet_mode_reglement['MC_ANNULATION'] = str(row.get('MC_ANNULATION', ''))
                objet_mode_reglement['JO_CODEJOURNAL'] = str(row.get('JO_CODEJOURNAL', ''))
                objet_mode_reglement['MC_REFERENCEPIECE'] = str(row.get('MC_REFERENCEPIECE', ''))
                objet_mode_reglement['MC_LIBELLEOPERATION'] = str(row.get('MC_LIBELLEOPERATION', ''))
                objet_mode_reglement['PL_CODENUMCOMPTE'] = str(objet_facture['PL_CODENUMCOMPTE'])
                objet_mode_reglement['MC_NOMTIERS'] = str(row.get('MC_NOMTIERS', ''))
                objet_mode_reglement['MC_CONTACTTIERS'] = str(row.get('MC_CONTACTTIERS', ''))
                objet_mode_reglement['MC_EMAILTIERS'] = str(row.get('MC_EMAILTIERS', ''))
                objet_mode_reglement['MC_NUMPIECETIERS'] = str(row.get('MC_NUMPIECETIERS', ''))
                objet_mode_reglement['MC_TERMINAL'] = str(row.get('MC_TERMINAL', ''))
                objet_mode_reglement['MC_AUTRE'] = str(row.get('MC_AUTRE', ''))
                objet_mode_reglement['MC_AUTRE1'] = str(row.get('MC_AUTRE1', ''))
                objet_mode_reglement['MC_AUTRE2'] = str(row.get('MC_AUTRE2', ''))
                objet_mode_reglement['MC_AUTRE3'] = str(row.get('MC_AUTRE3', ''))
                objet_mode_reglement['TS_CODETYPESCHEMACOMPTABLE'] = str(row.get('TS_CODETYPESCHEMACOMPTABLE', ''))
                objet_mode_reglement['MC_SENSBILLETAGE'] = str(row.get('MC_SENSBILLETAGE', ''))
                objet_mode_reglement['MC_LIBELLEBANQUE'] = str(row.get('MC_LIBELLEBANQUE', ''))
                objet_mode_reglement['MC_MONTANT_FACTURE'] = row.get('MC_MONTANT_FACTURE', '')
                objet_mode_reglement['MC_MONTANT_CONSTATIONFACTURE'] = row.get('MC_MONTANT_CONSTATIONFACTURE', '')
                objet_mode_reglement['ACT_CODEACTE'] = str(row.get('ACT_CODEACTE'))
                objet_mode_reglement['AS_CODEASSURANCE'] = str(row.get('AS_CODEASSURANCE'))
                clsmouvement_infos.append(objet_mode_reglement) 
            except ValueError as e:
                # Retourner un message d'erreur en cas de problème de type de données
                return jsonify({"SL_MESSAGE": f"Erreur de type de données : {str(e)}", "SL_RESULTAT": 'FALSE'}), 400
            except Exception as e:
                # Retourner un message d'erreur en cas d'exception générale
                return jsonify({"SL_MESSAGE": f"Erreur inattendue : {str(e)}", "SL_RESULTAT": 'FALSE'}), 200

        try:
            # Appeler la fonction d'insertion dans la base de données
            response = pvgComptabilisationOperations(cursor, clsmouvement_infos)
                        
            # Retourner la réponse au client
            if response['SL_RESULTAT'] == "TRUE":
                #cursor.close()
                return jsonify({"NUMEROBORDEREAUREGLEMENT":str(response['NUMEROBORDEREAU']),"MC_LIBELLEOPERATION":str(response['MC_LIBELLEOPERATION']),"SL_MESSAGE":"Comptabilisation éffectuée avec success !" + response['MESSAGEAPI'] ,"SL_RESULTAT": 'TRUE'}) 
            else:
                ##cursor.close()
                return jsonify({"SL_MESSAGE":response['SL_MESSAGE'] ,"SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            cursor.rollback()
            return jsonify({"SL_MESSAGE": f"Erreur lors de l'insertion : {str(e)}", "SL_RESULTAT": 'FALSE'}), 200
    except Exception as e:
            cursor.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
    """ #finally:
        #cursor.close() """

@api_bp.route('/ReglementFacture', methods=['POST'])
def pvgReglementFacture():
    # Récupérer les données du corps de la requête
    request_data = request.json
    
    if 'Objet' not in request_data:
        return jsonify({"SL_MESSAGE": "Données manquantes. Code erreur (300) voir le noeud Objet", "SL_RESULTAT": 'FALSE'})

    # Connexion à la base de données
    db_connexion = connect_database()
    
    try:
        # with db_connexion.cursor() as cursor:
        cursor = db_connexion.cursor()
        cursor.execute("BEGIN TRANSACTION")

        for row in request_data['Objet']:
            AG_CODEAGENCE = None
            JT_DATEJOURNEETRAVAIL = None
            OP_CODEOPERATEUR = None
            if request_data['Objet'][0]['clsObjetEnvoi'].get('OE_A', ''):
                AG_CODEAGENCE = str(request_data['Objet'][0]['clsObjetEnvoi'].get('OE_A', '')) 
            if request_data['Objet'][0]['clsObjetEnvoi'].get('OE_J', ''):
                JT_DATEJOURNEETRAVAIL  = str(request_data['Objet'][0]['clsObjetEnvoi'].get('OE_J', ''))
            if request_data['Objet'][0]['clsObjetEnvoi'].get('OE_Y', ''):
                OP_CODEOPERATEUR  = str(request_data['Objet'][0]['clsObjetEnvoi'].get('OE_Y', '')) 

            # Préparer les paramètres pour la fonction
            if AG_CODEAGENCE and JT_DATEJOURNEETRAVAIL and OP_CODEOPERATEUR:
                vpp_critere = (AG_CODEAGENCE, JT_DATEJOURNEETRAVAIL, OP_CODEOPERATEUR)
            elif AG_CODEAGENCE and JT_DATEJOURNEETRAVAIL:
                vpp_critere = (AG_CODEAGENCE, JT_DATEJOURNEETRAVAIL)
            elif AG_CODEAGENCE:
                vpp_critere = (AG_CODEAGENCE,)
            else:
                vpp_critere = ()
                
                
            response = test_journee_fermee(cursor, *vpp_critere)

            if response[0]['NBRE'] == 0:
                return jsonify({"SL_MESSAGE": 'Cette journée a été déjà fermée ou non encore ouverte !' ,"SL_RESULTAT": 'FALSE'})
        
        
        # Consigner les mouvements
        clsmouvement_infos = []
        for row in request_data['Objet']:
            objet_mode_reglement = {}
            try:
                objet_mode_reglement['MR_CODEMODEREGLEMENT'] = str(row.get('MR_CODEMODEREGLEMENT', ''))
                objet_mode_reglement['AG_CODEAGENCE'] = str(row.get('AG_CODEAGENCE', ''))
                objet_mode_reglement['MC_DATEPIECE'] = str(row.get('PT_DATESAISIE', ''))
                objet_mode_reglement['MC_NUMPIECE'] = str(row.get('MC_NUMPIECE', ''))
                objet_mode_reglement['MC_NUMSEQUENCE'] = str(row.get('MC_NUMSEQUENCE', ''))
                objet_mode_reglement['PT_IDPATIENT'] = str(row.get('PT_IDPATIENT', '')) 
                objet_mode_reglement['FT_CODEFACTURE'] = str(row.get('FT_CODEFACTURE', '')) 
                objet_mode_reglement['OP_CODEOPERATEUR'] = str(row.get('OP_CODEOPERATEUR', '')) 
                objet_mode_reglement['MC_MONTANTDEBIT'] = row.get('MC_MONTANTDEBIT', '')
                objet_mode_reglement['MC_MONTANTCREDIT'] = row.get('MC_MONTANTCREDIT', '')
                objet_mode_reglement['MC_DATESAISIE'] = str(row.get('PT_DATESAISIE', ''))  
                objet_mode_reglement['MC_ANNULATION'] = str(row.get('MC_ANNULATION', ''))
                objet_mode_reglement['JO_CODEJOURNAL'] = str(row.get('JO_CODEJOURNAL', ''))
                objet_mode_reglement['MC_REFERENCEPIECE'] = str(row.get('MC_REFERENCEPIECE', ''))
                objet_mode_reglement['MC_LIBELLEOPERATION'] = str(row.get('MC_LIBELLEOPERATION', ''))
                objet_mode_reglement['PL_CODENUMCOMPTE'] = str(row.get('PL_CODENUMCOMPTE', '')) 
                objet_mode_reglement['MC_NOMTIERS'] = str(row.get('MC_NOMTIERS', ''))
                objet_mode_reglement['MC_CONTACTTIERS'] = str(row.get('MC_CONTACTTIERS', ''))
                objet_mode_reglement['MC_EMAILTIERS'] = str(row.get('MC_EMAILTIERS', ''))
                objet_mode_reglement['MC_NUMPIECETIERS'] = str(row.get('MC_NUMPIECETIERS', ''))
                objet_mode_reglement['MC_TERMINAL'] = str(row.get('MC_TERMINAL', ''))
                objet_mode_reglement['MC_AUTRE'] = str(row.get('MC_AUTRE', ''))
                objet_mode_reglement['MC_AUTRE1'] = str(row.get('MC_AUTRE1', ''))
                objet_mode_reglement['MC_AUTRE2'] = str(row.get('MC_AUTRE2', ''))
                objet_mode_reglement['MC_AUTRE3'] = str(row.get('MC_AUTRE3', ''))
                objet_mode_reglement['TS_CODETYPESCHEMACOMPTABLE'] = str(row.get('TS_CODETYPESCHEMACOMPTABLE', ''))
                objet_mode_reglement['MC_SENSBILLETAGE'] = str(row.get('MC_SENSBILLETAGE', ''))
                objet_mode_reglement['MC_LIBELLEBANQUE'] = str(row.get('MC_LIBELLEBANQUE', ''))
                objet_mode_reglement['MC_MONTANT_FACTURE'] = row.get('MC_MONTANT_FACTURE', '')
                objet_mode_reglement['ACT_CODEACTE'] = str(row.get('ACT_CODEACTE', '')) 
                objet_mode_reglement['AS_CODEASSURANCE'] = str(row.get('AS_CODEASSURANCE', '')) 
                
                clsmouvement_infos.append(objet_mode_reglement) 
            except ValueError as e:
                # Retourner un message d'erreur en cas de problème de type de données
                return jsonify({"SL_MESSAGE": f"Erreur de type de données : {str(e)}", "SL_RESULTAT": 'FALSE'}), 400
            except Exception as e:
                # Retourner un message d'erreur en cas d'exception générale
                return jsonify({"SL_MESSAGE": f"Erreur inattendue : {str(e)}", "SL_RESULTAT": 'FALSE'}), 200

        try:
            # Appeler la fonction d'insertion dans la base de données
            response = pvgComptabilisationOperationsFacture(cursor, clsmouvement_infos)
                        
            # Retourner la réponse au client
            if response['SL_RESULTAT'] == "TRUE":
                #cursor.close()
                return jsonify({"NUMEROBORDEREAUREGLEMENT":str(response['NUMEROBORDEREAU']),"MC_LIBELLEOPERATION":str(response['MC_LIBELLEOPERATION']),"SL_MESSAGE":"Comptabilisation éffectuée avec success !" + response['MESSAGEAPI'] ,"SL_RESULTAT": 'TRUE'}) 
            else:
                ##cursor.close()
                return jsonify({"SL_MESSAGE":response['SL_MESSAGE'] ,"SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            cursor.rollback()
            return jsonify({"SL_MESSAGE": f"Erreur lors de l'insertion : {str(e)}", "SL_RESULTAT": 'FALSE'}), 200
    except Exception as e:
            cursor.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
    """ #finally:
        #cursor.close() """



@api_bp.route('/get_facture', methods=['POST'])
def pvgget_facture():
    request_data = request.json
    
    if 'Objet' not in request_data:
        return jsonify({"SL_MESSAGE": "Données manquantes. Code erreur (300) voir le noeud Objet", "SL_RESULTAT": 'FALSE'})
    
    if request_data['Objet']:
        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de la liste
                response = get_facture(db_connexion)
                
            if response:
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'}, response)
            else:
                return jsonify({"SL_MESSAGE": "Aucune facture trouvée !!!", "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()
            
            

@api_bp.route('/liste_facture_par_type', methods=['POST'])
def pvgGetFactureParType():
    request_data = request.json
    
    if 'Objet' not in request_data:
        return jsonify({"SL_MESSAGE": "Données manquantes.code erreur (300) voir le noeud Objet", "SL_RESULTAT": 'FALSE'})

    for row in request_data['Objet']:
        clsListeFacture = {}
        # Validation et récupération des données pour la suppression
        clsListeFacture['AG_CODEAGENCE'] = row.get('AG_CODEAGENCE')
        clsListeFacture['FT_CODEFACTURE'] = row.get('FT_CODEFACTURE')
        clsListeFacture['PT_IDPATIENT'] = row.get('PT_IDPATIENT')
        clsListeFacture['PT_NOMPRENOMS'] = row.get('PT_NOMPRENOMS')
        clsListeFacture['PT_CONTACT'] = row.get('PT_CONTACT')
        clsListeFacture['PT_MATRICULE'] = row.get('PT_MATRICULE')
        clsListeFacture['PT_CODEPATIENT'] = row.get('PT_CODEPATIENT')
        clsListeFacture['ACT_CODEACTE'] = row.get('ACT_CODEACTE')
        clsListeFacture['AS_CODEASSURANCE'] = row.get('AS_CODEASSURANCE')
        clsListeFacture['MC_DATESAISIE1'] = row.get('MC_DATESAISIE1')
        clsListeFacture['MC_DATESAISIE2'] = row.get('MC_DATESAISIE2')
        clsListeFacture['TYPEOPERATION'] = row.get('TYPEOPERATION')
        clsListeFacture['MONTANT1'] = row.get('MONTANT1')
        clsListeFacture['MONTANT2'] = row.get('MONTANT2')
        
        # required_keys = ['BI_CODEBIENS', 'BI_LIBELLEBIENS', 'TY_CODETYPENATUREBIENS', 'CODECRYPTAGE']

        # Vérifier si toutes les clés requises existent dans le dictionnaire
        # if not all(key in clsListeFacture for key in required_keys):
            # return jsonify({"SL_MESSAGE": "Données manquantes ou incorrectes. Code erreur (301)", "SL_RESULTAT": 'FALSE'})
        # Vérification que toutes les données obligatoires sont présentes
        #if not all([clsListeFacture['BI_CODEBIENS'], clsListeFacture['BI_LIBELLEBIENS'], clsListeFacture['TY_CODETYPENATUREBIENS'],clsListeFacture['CODECRYPTAGE'], clsListeFacture['TYPEOPERATION']]):
        #    return jsonify({"SL_MESSAGE": "Données manquantes ou incorrectes.code erreur (301)", "SL_RESULTAT": 'FALSE'})

        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression ou récupération
                response = list_facture(cursor, clsListeFacture)
                
                if len(response) > 0:
                    #cursor.execute("COMMIT")
                    return jsonify({"SL_MESSAGE": "Opération effectuée avec succès !!!", "SL_RESULTAT": 'TRUE'}, response)
                else:
                    result = {}
	
                    result['SL_MESSAGE'] = "Facture non trouvée ou autre erreur."
                    result['SL_RESULTAT'] = "FALSE"
                    # Ajouter le dictionnaire à la liste des résultats
                    response.append(result)
                    return jsonify(response)
                    #cursor.execute("ROLLBACK")
                    
        
        except Exception as e:
            cursor.rollback()
            return jsonify([{"SL_MESSAGE": "Erreur lors du chargement : " + str(e), "SL_RESULTAT": 'FALSE'}])
        
        #finally:
            #cursor.close()
            
################################################################
#                           GESTION DES FACTURES                                                                  #
################################################################




################################################################
#                            GESTION DES EDITIONS                                                                  #
################################################################

@api_bp.route('/ExtourneOperation', methods=['POST'])
def pvgExtourneOperation():
    request_data = request.json
    
    if 'Objet' not in request_data:
        return jsonify({"SL_MESSAGE": "Données manquantes.code erreur (300) voir le noeud Objet", "SL_RESULTAT": 'FALSE'})
    
    for row in request_data['Objet']:
        contrat_info = {}

        # Validation et récupération des données pour la suppression
        contrat_info['AG_CODEAGENCE'] = str(row.get('AG_CODEAGENCE', ''))
        contrat_info['MV_DATEPIECECOMPTABILISATION'] = str(row.get('MV_DATEPIECECOMPTABILISATION'))
        contrat_info['MV_DATEPIECE'] = str(row.get('MV_DATEPIECE', ''))
        contrat_info['MV_NUMPIECE1'] = str(row.get('MV_NUMPIECE1', ''))
        contrat_info['MV_NUMPIECE3'] = str(row.get('MV_NUMPIECE3'))
        contrat_info['OP_CODEOPERATEUR'] = str(row.get('OP_CODEOPERATEUR', ''))
        contrat_info['TYPEOPERATION'] = str(row.get('TYPEOPERATION', ''))
        
        AG_CODEAGENCE = None
        JT_DATEJOURNEETRAVAIL = None
        OP_CODEOPERATEUR = None
        if request_data['Objet'][0]['clsObjetEnvoi'].get('OE_A', ''):
           AG_CODEAGENCE = str(request_data['Objet'][0]['clsObjetEnvoi'].get('OE_A', '')) 
        if request_data['Objet'][0]['clsObjetEnvoi'].get('OE_J', ''):
           JT_DATEJOURNEETRAVAIL  = str(request_data['Objet'][0]['clsObjetEnvoi'].get('OE_J', ''))
        if request_data['Objet'][0]['clsObjetEnvoi'].get('OE_Y', ''):
           OP_CODEOPERATEUR  = str(request_data['Objet'][0]['clsObjetEnvoi'].get('OE_Y', '')) 

        # Préparer les paramètres pour la fonction
        if AG_CODEAGENCE and JT_DATEJOURNEETRAVAIL and OP_CODEOPERATEUR:
            vpp_critere = (AG_CODEAGENCE, JT_DATEJOURNEETRAVAIL, OP_CODEOPERATEUR)
        elif AG_CODEAGENCE and JT_DATEJOURNEETRAVAIL:
            vpp_critere = (AG_CODEAGENCE, JT_DATEJOURNEETRAVAIL)
        elif AG_CODEAGENCE:
            vpp_critere = (AG_CODEAGENCE,)
        else:
            vpp_critere = ()
            
        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                response = test_journee_fermee(cursor, *vpp_critere)

                if response[0]['NBRE'] == 0:
                    return jsonify({"SL_MESSAGE": 'Cette journée a été déjà fermée ou non encore ouverte !' ,"SL_RESULTAT": 'FALSE'})
        
                # Appeler la fonction de suppression
                ExtourneOperation(cursor, str(row.get('AG_CODEAGENCE', '')), str(row.get('MV_DATEPIECECOMPTABILISATION')),str(row.get('MV_DATEPIECE', '')),
                                             str(row.get('MV_NUMPIECE1', '')), str(row.get('MV_NUMPIECE3')),str(row.get('OP_CODEOPERATEUR', '')),str(row.get('TYPEOPERATION', '')))
                user_infos = [
                {
                    'AG_CODEAGENCE':"1000",
                    'JT_STATUT':"O",
                },
                 {
                    'AG_CODEAGENCE':"1000",
                    'JT_STATUT':"O",
                }
                ]
                get_commit(cursor,user_infos)
            
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'})
            
        except Exception as e:
            cursor.rollback()
            return jsonify({"SL_MESSAGE":  str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #cursor.close()

@api_bp.route('/ExtourneFacture', methods=['POST'])
def pvgExtourneFacture():
    request_data = request.json
    
    if 'Objet' not in request_data:
        return jsonify({"SL_MESSAGE": "Données manquantes.code erreur (300) voir le noeud Objet", "SL_RESULTAT": 'FALSE'})
    
    for row in request_data['Objet']:
        contrat_info = {}

        # Validation et récupération des données pour la suppression
        contrat_info['AG_CODEAGENCE'] = str(row.get('AG_CODEAGENCE', ''))
        contrat_info['MV_DATEPIECECOMPTABILISATION'] = str(row.get('MV_DATEPIECECOMPTABILISATION'))
        contrat_info['MC_DATESAISIE'] = str(row.get('MC_DATESAISIE', ''))
        contrat_info['FT_CODEFACTURE'] = str(row.get('FT_CODEFACTURE', ''))
        contrat_info['MV_NUMPIECE3'] = str(row.get('MV_NUMPIECE3'))
        contrat_info['OP_CODEOPERATEUR'] = str(row.get('OP_CODEOPERATEUR', ''))
        contrat_info['TYPEOPERATION'] = str(row.get('TYPEOPERATION', ''))
        
        AG_CODEAGENCE = None
        JT_DATEJOURNEETRAVAIL = None
        OP_CODEOPERATEUR = None
        if request_data['Objet'][0]['clsObjetEnvoi'].get('OE_A', ''):
           AG_CODEAGENCE = str(request_data['Objet'][0]['clsObjetEnvoi'].get('OE_A', '')) 
        if request_data['Objet'][0]['clsObjetEnvoi'].get('OE_J', ''):
           JT_DATEJOURNEETRAVAIL  = str(request_data['Objet'][0]['clsObjetEnvoi'].get('OE_J', ''))
        if request_data['Objet'][0]['clsObjetEnvoi'].get('OE_Y', ''):
           OP_CODEOPERATEUR  = str(request_data['Objet'][0]['clsObjetEnvoi'].get('OE_Y', '')) 

        # Préparer les paramètres pour la fonction
        if AG_CODEAGENCE and JT_DATEJOURNEETRAVAIL and OP_CODEOPERATEUR:
            vpp_critere = (AG_CODEAGENCE, JT_DATEJOURNEETRAVAIL, OP_CODEOPERATEUR)
        elif AG_CODEAGENCE and JT_DATEJOURNEETRAVAIL:
            vpp_critere = (AG_CODEAGENCE, JT_DATEJOURNEETRAVAIL)
        elif AG_CODEAGENCE:
            vpp_critere = (AG_CODEAGENCE,)
        else:
            vpp_critere = ()
        
        # Vérification que toutes les données obligatoires sont présentes
        if not all([contrat_info['FT_CODEFACTURE'] 
                    ]):
            return jsonify({"SL_MESSAGE": "Données manquantes ou incorrectes.code erreur (301) FT_CODEFACTURE", "SL_RESULTAT": 'FALSE'}), 200    
        
        
        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                response = test_journee_fermee(cursor, *vpp_critere)

                if response[0]['NBRE'] == 0:
                    return jsonify({"SL_MESSAGE": 'Cette journée a été déjà fermée ou non encore ouverte !' ,"SL_RESULTAT": 'FALSE'})
                
                # Appeler la fonction de suppression
                ExtourneFacture(cursor, str(row.get('AG_CODEAGENCE', '')), str(row.get('MV_DATEPIECECOMPTABILISATION')),str(row.get('FT_CODEFACTURE', '')),str(row.get('MC_DATESAISIE', '')),
                                              str(row.get('MV_NUMPIECE3')),str(row.get('OP_CODEOPERATEUR', '')),str(row.get('TYPEOPERATION', '')))
                user_infos = [
                {
                    'AG_CODEAGENCE':"1000",
                    'JT_STATUT':"O",
                },
                {
                    'AG_CODEAGENCE':"1000",
                    'JT_STATUT':"O",
                }
                ]
                get_commit(cursor,user_infos)
            
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'})
            
        except Exception as e:
            cursor.rollback()
            return jsonify({"SL_MESSAGE":  str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #cursor.close()


@api_bp.route('/pvgSoldeCompteClient', methods=['POST'])
def SoldeCompteClient():
    request_data = request.json
    
    if 'Objet' not in request_data:
        return jsonify({"SL_MESSAGE": "Données manquantes.code erreur (300) voir le noeud Objet", "SL_RESULTAT": 'FALSE'})
    
    for row in request_data['Objet']:
        compte_info = {}
        
        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = pvgSoldeCompteClient(db_connexion, str(row.get('AG_CODEAGENCE', '')),str(row.get('PT_IDPATIENT', '')), str(row.get('PL_CODENUMCOMPTE')))
            
            if response:
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify([{"SL_MESSAGE": "Aucuns élement trouvé !!!", "SL_RESULTAT": 'FALSE'}])
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors du chargement : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()

@api_bp.route('/pvgTableLabelAvecSolde', methods=['POST'])
def TableLabelAvecSolde():
    request_data = request.json
    
    if 'Objet' not in request_data:
        return jsonify({"SL_MESSAGE": "Données manquantes.code erreur (300) voir le noeud Objet", "SL_RESULTAT": 'FALSE'})
    
    for row in request_data['Objet']:
        compte_info = {}

        # Validation et récupération des données pour la suppression
        #SO_CODESOCIETE,AG_CODEAGENCE,PL_NUMCOMPTE,MC_DATEPIECE
        compte_info['AG_CODEAGENCE'] = str(row.get('AG_CODEAGENCE', ''))
        compte_info['MC_DATEPIECE'] = str(row.get('MC_DATEPIECE'))
        compte_info['SO_CODESOCIETE'] = str(row.get('SO_CODESOCIETE', ''))
        compte_info['PL_NUMCOMPTE'] = str(row.get('PL_NUMCOMPTE', ''))

        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = pvgTableLabelAvecSolde(db_connexion,str(row.get('SO_CODESOCIETE', '')), str(row.get('AG_CODEAGENCE', '')),str(row.get('PL_NUMCOMPTE', '')), str(row.get('MC_DATEPIECE')))
            
            if len(response) > 0:
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify([{"SL_MESSAGE": "Aucuns élement trouvé !!!", "SL_RESULTAT": 'FALSE'}])
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors du chargement : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()

@api_bp.route('/recu_edition', methods=['POST'])
def pvgRecuEdition():
    request_data = request.json
    
    if 'Objet' not in request_data:
        return jsonify({"SL_MESSAGE": "Données manquantes.code erreur (300) voir le noeud Objet", "SL_RESULTAT": 'FALSE'})
    
    for row in request_data['Objet']:
        contrat_info = {}

        # Validation et récupération des données pour la suppression
        contrat_info['AG_CODEAGENCE'] = str(row.get('AG_CODEAGENCE', ''))
        contrat_info['MC_DATEPIECE'] = str(row.get('MC_DATEPIECE'))
        contrat_info['NUMEROBORDEREAU'] = str(row.get('NUMEROBORDEREAU', ''))

        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = recu_edition(db_connexion, str(row.get('AG_CODEAGENCE', '')), str(row.get('MC_DATEPIECE')),str(row.get('NUMEROBORDEREAU', '')))
            
            if len(response) > 0:
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": "Aucuns élement trouvé !!!", "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors du chargement : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()



@api_bp.route('/edition_solde', methods=['POST'])
def pvgSolde():
    request_data = request.json
    
    if 'Objet' not in request_data:
        return jsonify({"SL_MESSAGE": "Données manquantes.code erreur (300) voir le noeud Objet", "SL_RESULTAT": 'FALSE'})
    
    for row in request_data['Objet']:
        solde_info = {}

        # Validation et récupération des données pour la suppression
        solde_info['AG_CODEAGENCE'] = str(row.get('AG_CODEAGENCE', ''))
        solde_info['OP_CODEOPERATEUREDITION'] = str(row.get('OP_CODEOPERATEUREDITION'))
        solde_info['DATEDEBUT'] = str(row.get('DATEDEBUT', ''))
        solde_info['DATEFIN'] = str(row.get('DATEFIN', ''))
        solde_info['PT_IDPATIENT'] = str(row.get('PT_IDPATIENT', ''))
        solde_info['FT_CODEFACTURE'] = str(row.get('FT_CODEFACTURE', ''))

        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = solde_edition(cursor, solde_info)
            
            if len(response) > 0:
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": "Aucuns élement trouvé !!!", "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            cursor.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors du chargement : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #cursor.close()



@api_bp.route('/brouillard_de_caisse', methods=['POST'])
def pvgBrouillardCaisse():
    request_data = request.json
    
    if 'Objet' not in request_data:
        return jsonify({"SL_MESSAGE": "Données manquantes.code erreur (300) voir le noeud Objet", "SL_RESULTAT": 'FALSE'})
    
    for row in request_data['Objet']:
        broui_caisse_info = {}

        # Validation et récupération des données pour la suppression
        broui_caisse_info['AG_CODEAGENCE'] = str(row.get('AG_CODEAGENCE'))
        broui_caisse_info['OP_CODEOPERATEUR'] = str(row.get('OP_CODEOPERATEUR'))
        broui_caisse_info['TYPEBROUILLARD'] = str(row.get('TYPEBROUILLARD'))
        broui_caisse_info['DATEDEBUT'] = str(row.get('DATEDEBUT'))
        broui_caisse_info['DATEFIN'] = str(row.get('DATEFIN'))
        broui_caisse_info['TYPEETAT'] = str(row.get('TYPEETAT'))
        broui_caisse_info['TS_CODETYPESCHEMACOMPTABLE'] = str(row.get('TS_CODETYPESCHEMACOMPTABLE'))
        broui_caisse_info['OP_CODEOPERATEUREDITION'] = str(row.get('OP_CODEOPERATEUREDITION'))
        broui_caisse_info['MR_CODEMODEREGLEMENT'] = str(row.get('MR_CODEMODEREGLEMENT'))
        broui_caisse_info['ACT_CODEACTE'] = str(row.get('ACT_CODEACTE'))

        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = brouillard_caisse_edition(cursor, broui_caisse_info)
            
            if len(response) > 0:
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": "Aucuns élement trouvé !!!", "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            cursor.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors du chargement : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #cursor.close()



@api_bp.route('/journal', methods=['POST'])
def pvgJournal():
    request_data = request.json
    
    if 'Objet' not in request_data:
        return jsonify({"SL_MESSAGE": "Données manquantes.code erreur (300) voir le noeud Objet", "SL_RESULTAT": 'FALSE'})
    
    for row in request_data['Objet']:
        journal_info = {}

        # Validation et récupération des données pour la suppression
        journal_info['AG_CODEAGENCE'] = str(row.get('AG_CODEAGENCE'))
        journal_info['OP_CODEOPERATEUR'] = str(row.get('OP_CODEOPERATEUR'))
        journal_info['DATEDEBUT'] = str(row.get('DATEDEBUT'))
        journal_info['DATEFIN'] = str(row.get('DATEFIN'))
        journal_info['TYPEETAT'] = str(row.get('TYPEETAT'))
        journal_info['OP_CODEOPERATEUREDITION'] = str(row.get('OP_CODEOPERATEUREDITION'))
        journal_info['MR_CODEMODEREGLEMENT'] = str(row.get('MR_CODEMODEREGLEMENT'))
        journal_info['ACT_CODEACTE'] = str(row.get('ACT_CODEACTE'))
        journal_info['STAT_CODESTATUT'] = str(row.get('STAT_CODESTATUT'))
        journal_info['AS_CODEASSURANCE'] = str(row.get('AS_CODEASSURANCE'))
        journal_info['MONTANTDEBUT'] = str(row.get('MONTANTDEBUT'))
        journal_info['MONTANTFIN'] = str(row.get('MONTANTFIN'))
        journal_info['NUMBORDEREAU'] = str(row.get('NUMBORDEREAU'))
        journal_info['JO_CODEJOURNAL'] = str(row.get('JO_CODEJOURNAL'))
        journal_info['TS_CODETYPESCHEMACOMPTABLE'] = str(row.get('TS_CODETYPESCHEMACOMPTABLE'))

        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = journal_edition(db_connexion, journal_info)
            
            if len(response) > 0:
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": "Aucuns élement trouvé !!!", "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors du chargement : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()
     
     
     
@api_bp.route('/edition_pointparacte', methods=['POST'])
def pvgEditionPointParActe():
    request_data = request.json
    
    if 'Objet' not in request_data:
        return jsonify({"SL_MESSAGE": "Données manquantes.code erreur (300) voir le noeud Objet", "SL_RESULTAT": 'FALSE'})
    
    for row in request_data['Objet']:
        pt_par_acte_info = {}

        # Validation et récupération des données pour la suppression
        pt_par_acte_info['AG_CODEAGENCE'] = str(row.get('AG_CODEAGENCE'))
        pt_par_acte_info['OP_CODEOPERATEUREDITION'] = str(row.get('OP_CODEOPERATEUREDITION'))
        pt_par_acte_info['DATEDEBUT'] = str(row.get('DATEDEBUT'))
        pt_par_acte_info['DATEFIN'] = str(row.get('DATEFIN'))
        pt_par_acte_info['ACT_CODEACTE'] = str(row.get('ACT_CODEACTE'))
        pt_par_acte_info['MR_CODEMODEREGLEMENT'] = str(row.get('MR_CODEMODEREGLEMENT'))

        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = point_par_acte_edition(db_connexion, pt_par_acte_info)
            
            if len(response) > 0:
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": "Aucuns élement trouvé !!!", "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors du chargement : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()
  
  
  
@api_bp.route('/edition_formation', methods=['POST'])
def pvgEditionFormation():
    request_data = request.json
    
    if 'Objet' not in request_data:
        return jsonify({"SL_MESSAGE": "Données manquantes.code erreur (300) voir le noeud Objet", "SL_RESULTAT": 'FALSE'})
    
    for row in request_data['Objet']:
        formation_info = {}

        # Validation et récupération des données pour la suppression
        formation_info['AG_CODEAGENCE'] = str(row.get('AG_CODEAGENCE'))
        formation_info['DATEDEBUT'] = str(row.get('DATEDEBUT'))
        formation_info['DATEFIN'] = str(row.get('DATEFIN'))
        formation_info['TYPEETAT'] = str(row.get('TYPEETAT'))
        formation_info['OP_CODEOPERATEUREDITION'] = str(row.get('OP_CODEOPERATEUREDITION'))
        formation_info['OPTION'] = str(row.get('OPTION'))
        # formation_info['OPTIONAFFICHAGE'] = str(row.get('OPTIONAFFICHAGE'))

        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = formation_edition(db_connexion, formation_info)
            
            if len(response) > 0:
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": "Aucuns élement trouvé !!!", "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors du chargement : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()
            
            
  
@api_bp.route('/editionPatient', methods=['POST'])
def pvgeditionPatient():
    request_data = request.json
    
    if 'Objet' not in request_data:
        return jsonify({"SL_MESSAGE": "Données manquantes.code erreur (300) voir le noeud Objet", "SL_RESULTAT": 'FALSE'})
    
    for row in request_data['Objet']:
        editionPatient_info = {}

        # Validation et récupération des données pour la suppression
        editionPatient_info['AG_CODEAGENCE'] = str(row.get('AG_CODEAGENCE'))
        editionPatient_info['OP_CODEOPERATEUR'] = str(row.get('OP_CODEOPERATEUR'))
        editionPatient_info['DATEDEBUT'] = str(row.get('DATEDEBUT'))
        editionPatient_info['DATEFIN'] = str(row.get('DATEFIN'))
        editionPatient_info['TYPEETAT'] = str(row.get('TYPEETAT'))
        editionPatient_info['OP_CODEOPERATEUREDITION'] = str(row.get('OP_CODEOPERATEUREDITION'))
        editionPatient_info['STAT_CODESTATUT'] = str(row.get('STAT_CODESTATUT'))
        editionPatient_info['AS_CODEASSURANCE'] = str(row.get('AS_CODEASSURANCE'))
        editionPatient_info['SX_CODESEXE'] = str(row.get('SX_CODESEXE'))
        editionPatient_info['CODESTATUTSOLDE'] = str(row.get('CODESTATUTSOLDE'))
        

        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = editionPatient(db_connexion, editionPatient_info)
            
            if len(response) > 0:
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": "Aucuns élement trouvé !!!", "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors du chargement : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()  
  
@api_bp.route('/grand_livre', methods=['POST'])
def pvgGrandLivre():
    request_data = request.json
    
    if 'Objet' not in request_data:
        return jsonify({"SL_MESSAGE": "Données manquantes.code erreur (300) voir le noeud Objet", "SL_RESULTAT": 'FALSE'})
    
    for row in request_data['Objet']:
        gd_livre_info = {}

        # Validation et récupération des données pour la suppression
        gd_livre_info['AG_CODEAGENCE'] = str(row.get('AG_CODEAGENCE'))
        gd_livre_info['OP_CODEOPERATEUR'] = str(row.get('OP_CODEOPERATEUR'))
        gd_livre_info['DATEDEBUT'] = str(row.get('DATEDEBUT'))
        gd_livre_info['DATEFIN'] = str(row.get('DATEFIN'))
        gd_livre_info['TYPEETAT'] = str(row.get('TYPEETAT'))
        gd_livre_info['OP_CODEOPERATEUREDITION'] = str(row.get('OP_CODEOPERATEUREDITION'))
		
        gd_livre_info['NUMCOMPTEDEBUT'] = str(row.get('NUMCOMPTEDEBUT'))
        gd_livre_info['NUMCOMPTEFIN'] = str(row.get('NUMCOMPTEFIN'))

        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = gd_livre_edition(db_connexion, gd_livre_info)
            
            if len(response) > 0:
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": "Aucuns élement trouvé !!!", "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors du chargement : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()



@api_bp.route('/balance', methods=['POST'])
def pvgBalance():
    request_data = request.json
    
    if 'Objet' not in request_data:
        return jsonify({"SL_MESSAGE": "Données manquantes.code erreur (300) voir le noeud Objet", "SL_RESULTAT": 'FALSE'})
    
    for row in request_data['Objet']:
        balance_info = {}

        # Validation et récupération des données pour la suppression
        balance_info['AG_CODEAGENCE'] = str(row.get('AG_CODEAGENCE'))
        balance_info['OP_CODEOPERATEUR'] = str(row.get('OP_CODEOPERATEUR'))
        balance_info['DATEDEBUT'] = str(row.get('DATEDEBUT'))
        balance_info['DATEFIN'] = str(row.get('DATEFIN'))
        balance_info['TYPEETAT'] = str(row.get('TYPEETAT'))
        balance_info['OP_CODEOPERATEUREDITION'] = str(row.get('OP_CODEOPERATEUREDITION'))
		
        balance_info['PL_OPTION'] = str(row.get('PL_OPTION'))
        balance_info['NUMCOMPTEDEBUT'] = str(row.get('NUMCOMPTEDEBUT'))
        balance_info['NUMCOMPTEFIN'] = str(row.get('NUMCOMPTEFIN'))
        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = balance_edition(db_connexion, balance_info)
            
            if len(response) > 0:
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": "Aucuns élement trouvé !!!", "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors du chargement : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()
            
################################################################
#                   GESTION DES EDITIONS                                                                  #
################################################################



################################################################
#                        GESTION DASHBOARD                                                                  #
################################################################

@api_bp.route('/dashboard', methods=['POST'])
def pvgDashboard():
    request_data = request.json
    
    if 'Objet' not in request_data:
        return jsonify({"SL_MESSAGE": "Données manquantes.code erreur (300) voir le noeud Objet", "SL_RESULTAT": 'FALSE'})
    
    for row in request_data['Objet']:
        cls_dashboard = {}

        # Validation et récupération des données pour la suppression
        cls_dashboard['AG_CODEAGENCE'] = str(row.get('AG_CODEAGENCE', ''))
        cls_dashboard['OP_CODEOPERATEUR'] = str(row.get('OP_CODEOPERATEUR'))
        cls_dashboard['DATEDEBUT'] = str(row.get('DATEDEBUT', ''))
        cls_dashboard['DATEFIN'] = str(row.get('DATEFIN', ''))
        cls_dashboard['TYPEOPERATION'] = str(row.get('TYPEOPERATION', ''))

        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = dashboard(db_connexion, cls_dashboard)
            
            if len(response) > 0:
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": "Aucuns élement trouvé !!!", "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors du chargement : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()


@api_bp.route('/send_email', methods=['POST'])
def send_email():
    try:
        # Récupération de l'email et du fichier depuis FormData
        email = request.form.get('email')
        ag_email = request.form.get('ag_email')
        ag_email_mdp = request.form.get('ag_email_mdp')
        file = request.files.get('file')

        if not email or not file or not ag_email or not ag_email_mdp:
            return jsonify({'error': 'Email ou fichier manquant'}), 400
        
        if not ag_email or not ag_email_mdp:
            return jsonify({'error': 'Aucun email agence configuré'}), 400

        file_content = file.read()

        # Création de l'email
        msg = EmailMessage()
        msg['Subject'] = 'Votre rapport PDF'
        msg['From'] = ag_email
        msg['To'] = email
        msg.set_content("Bonjour,\n\nVoici le rapport PDF en pièce jointe.")

        msg.add_attachment(
            file_content,
            maintype='application',
            subtype='pdf',
            filename=file.filename
        )

        # Envoi de l'email via SMTP
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login(ag_email, ag_email_mdp)
            smtp.send_message(msg)

        return jsonify({'message': 'Email envoyé avec succès.'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
################################################################
#                      GESTION DASHBOARD                                                                  #
################################################################



################################################################
#                          GESTION DE L'AUTHENTIFICATION                                                        #
################################################################

#service de connexion
@api_bp.route('/login', methods=['POST'])
def pvgUserLogin():
    # Récupérer les données du corps de la requête
    request_data = request.json
    
    # Parcourir les éléments de la liste Objet
    for row in request_data['Objet']:
        clsInfoUsersconnect = {}
        clsInfoUsersconnect['OP_LOGIN'] = row['OP_LOGIN']
        clsInfoUsersconnect['OP_MOTPASSE'] = row['OP_MOTPASSE']
        
        # Récupérer la connexion à la base de données depuis current_app
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction avec les données récupérées
                response = connexion_utilisateur(cursor, clsInfoUsersconnect)
                
                # Valider la transaction si tout s'est bien passé
                cursor.commit()
            
            # Retourner la réponse au client
            if len(response) > 0:
                return jsonify({"SL_MESSAGE": "Connexion effectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response[0])
            else:
                return jsonify({"SL_MESSAGE": 'Login ou mot de passe incorrect', "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            cursor.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la connexion : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #cursor.close()                    


@api_bp.route('/pvgUserChangePasswordfist', methods=['POST'])
def UserChangePasswordfist():
    # Récupérer les données du corps de la requête
    request_data = request.json
    
    # Parcourir les éléments de la liste Objet
    for row in request_data['Objet']:
        clsUserChangePasswordfist = {}
        clsUserChangePasswordfist['PO_CODEPROFIL'] = row['PO_CODEPROFIL']
        clsUserChangePasswordfist['OP_MOTPASSEOLD'] = row['OP_MOTPASSEOLD']
        clsUserChangePasswordfist['OP_LOGINOLD'] = row['OP_LOGINOLD']
        clsUserChangePasswordfist['OP_MOTPASSENEW'] = row['OP_MOTPASSENEW']
        clsUserChangePasswordfist['OP_LOGINNEW'] = row['OP_LOGINNEW']
  
        
        
        
    # Vérification que toutes les données obligatoires sont présentes
        if not all([clsUserChangePasswordfist['PO_CODEPROFIL'], clsUserChangePasswordfist['OP_LOGINOLD'], 
                    clsUserChangePasswordfist['OP_MOTPASSENEW'], clsUserChangePasswordfist['OP_LOGINNEW'] 
                    ]):
            return jsonify({"SL_MESSAGE": "Données manquantes ou incorrectes.code erreur (301)", "SL_RESULTAT": 'FALSE'}), 200    
        
        # Récupérer la connexion à la base de données depuis current_app
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction avec les données récupérées
                response = pvgUserChangePasswordfist(cursor, clsUserChangePasswordfist)
                
                # Valider la transaction si tout s'est bien passé
                db_connexion.commit()
            
            # Retourner la réponse au client
            if response[0]['SL_RESULTAT'] == 'TRUE':
                return jsonify({"SL_MESSAGE": "Opération effectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response[0])
            else:
                return jsonify({"SL_MESSAGE": response['SL_MESSAGE'], "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la modification des accès : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            db_connexion.close()  
            
@api_bp.route('/pvgUserDemandePassword', methods=['POST'])
def UserDemandePassword():
    # Récupérer les données du corps de la requête
    request_data = request.json
    
    # Parcourir les éléments de la liste Objet
    for row in request_data['Objet']:
        clspvgUserDemandePassword = {}
        clspvgUserDemandePassword['OP_TELEPHONE'] = row['OP_TELEPHONE']
        clspvgUserDemandePassword['OP_LOGIN'] = row['OP_LOGIN']
        #clspvgUserDemandePassword['TYPEOPERATION'] = row['TYPEOPERATION']
        #clspvgUserDemandePassword['CODECRYPTAGE'] = row['CODECRYPTAGE']
        
        # Récupérer la connexion à la base de données depuis current_app
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction avec les données récupérées
                response = pvgUserDemandePassword(cursor, clspvgUserDemandePassword)
                
                # Valider la transaction si tout s'est bien passé
                db_connexion.commit()
            
            # Retourner la réponse au client
            if response[0]['SL_RESULTAT'] == 'TRUE':
                return jsonify({"SL_MESSAGE": "Opération effectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response[0])
            else:
                return jsonify({"SL_MESSAGE": response[0]['SL_MESSAGE'], "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la modification des accès : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            db_connexion.close() 



################################################################
#                           GESTION DE L'AUTHENTIFICATION                                                        #
################################################################


@api_bp.route('/creation_profil', methods=['POST'])
def pvgcreation_profil():
    # Récupérer les données du corps de la requête
    request_data = request.json

    for row in request_data['Objet']:
        profil_info = {}

        try:
            # Validation des chaînes de caractères
            profil_info['PO_CODEPROFIL'] = str(row.get('PO_CODEPROFIL', ''))
            profil_info['PO_LIBELLE'] = str(row.get('PO_LIBELLE', ''))
            
            AG_CODEAGENCE = None
            JT_DATEJOURNEETRAVAIL = None
            OP_CODEOPERATEUR = None
            if request_data['Objet'][0]['clsObjetEnvoi'].get('OE_A', ''):
                AG_CODEAGENCE = str(request_data['Objet'][0]['clsObjetEnvoi'].get('OE_A', '')) 
            if request_data['Objet'][0]['clsObjetEnvoi'].get('OE_J', ''):
                JT_DATEJOURNEETRAVAIL  = str(request_data['Objet'][0]['clsObjetEnvoi'].get('OE_J', ''))
            if request_data['Objet'][0]['clsObjetEnvoi'].get('OE_Y', ''):
                OP_CODEOPERATEUR  = str(request_data['Objet'][0]['clsObjetEnvoi'].get('OE_Y', '')) 

            # Préparer les paramètres pour la fonction
            if AG_CODEAGENCE and JT_DATEJOURNEETRAVAIL and OP_CODEOPERATEUR:
                vpp_critere = (AG_CODEAGENCE, JT_DATEJOURNEETRAVAIL, OP_CODEOPERATEUR)
            elif AG_CODEAGENCE and JT_DATEJOURNEETRAVAIL:
                vpp_critere = (AG_CODEAGENCE, JT_DATEJOURNEETRAVAIL)
            elif AG_CODEAGENCE:
                vpp_critere = (AG_CODEAGENCE,)
            else:
                vpp_critere = ()

        except ValueError as e:
            # Retourner un message d'erreur en cas de problème de type de données
            return jsonify({"SL_MESSAGE": f"Erreur de type de données : {str(e)}", "SL_RESULTAT": 'FALSE'}), 200
        
        except Exception as e:
            # Retourner un message d'erreur en cas d'exception générale
            return jsonify({"SL_MESSAGE": f"Erreur inattendue : {str(e)}", "SL_RESULTAT": 'FALSE'}), 200

        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion:
                cursor = db_connexion.cursor()
                cursor.execute("BEGIN TRANSACTION")
                
                response = test_journee_fermee(cursor, *vpp_critere)

                if response[0]['NBRE'] == 0:
                    return jsonify({"SL_MESSAGE": 'Cette journée a été déjà fermée ou non encore ouverte !' ,"SL_RESULTAT": 'FALSE'})

                # Appeler la fonction d'insertion dans la base de données
                reponse = creation_profil(cursor, profil_info)
                
                # Valider la transaction
                cursor.commit()

            return jsonify({"SL_MESSAGE": "Insertion réussie!", "SL_RESULTAT": 'TRUE', "data": reponse}), 200

        except Exception as e:
            cursor.rollback()
            return jsonify({"SL_MESSAGE": f"Erreur lors de l'insertion : {str(e)}", "SL_RESULTAT": 'FALSE'}), 200


@api_bp.route('/update_profil', methods=['POST'])
def pvgupdate_profil():
    # Récupérer les données du corps de la requête
    request_data = request.json

    for row in request_data['Objet']:
        profil_info = {}

        try:
            # Validation des chaînes de caractères
            profil_info['PO_CODEPROFIL'] = str(row.get('PO_CODEPROFIL', ''))
            profil_info['PO_LIBELLE'] = str(row.get('PO_LIBELLE', ''))
            
            AG_CODEAGENCE = None
            JT_DATEJOURNEETRAVAIL = None
            OP_CODEOPERATEUR = None
            if request_data['Objet'][0]['clsObjetEnvoi'].get('OE_A', ''):
                AG_CODEAGENCE = str(request_data['Objet'][0]['clsObjetEnvoi'].get('OE_A', '')) 
            if request_data['Objet'][0]['clsObjetEnvoi'].get('OE_J', ''):
                JT_DATEJOURNEETRAVAIL  = str(request_data['Objet'][0]['clsObjetEnvoi'].get('OE_J', ''))
            if request_data['Objet'][0]['clsObjetEnvoi'].get('OE_Y', ''):
                OP_CODEOPERATEUR  = str(request_data['Objet'][0]['clsObjetEnvoi'].get('OE_Y', '')) 

            # Préparer les paramètres pour la fonction
            if AG_CODEAGENCE and JT_DATEJOURNEETRAVAIL and OP_CODEOPERATEUR:
                vpp_critere = (AG_CODEAGENCE, JT_DATEJOURNEETRAVAIL, OP_CODEOPERATEUR)
            elif AG_CODEAGENCE and JT_DATEJOURNEETRAVAIL:
                vpp_critere = (AG_CODEAGENCE, JT_DATEJOURNEETRAVAIL)
            elif AG_CODEAGENCE:
                vpp_critere = (AG_CODEAGENCE,)
            else:
                vpp_critere = ()

        except ValueError as e:
            # Retourner un message d'erreur en cas de problème de type de données
            return jsonify({"SL_MESSAGE": f"Erreur de type de données : {str(e)}", "SL_RESULTAT": 'FALSE'}), 200
        
        except Exception as e:
            # Retourner un message d'erreur en cas d'exception générale
            return jsonify({"SL_MESSAGE": f"Erreur inattendue : {str(e)}", "SL_RESULTAT": 'FALSE'}), 200

        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion:
                cursor = db_connexion.cursor()
                cursor.execute("BEGIN TRANSACTION")
                
                response = test_journee_fermee(cursor, *vpp_critere)

                if response[0]['NBRE'] == 0:
                    return jsonify({"SL_MESSAGE": 'Cette journée a été déjà fermée ou non encore ouverte !' ,"SL_RESULTAT": 'FALSE'})

                # Appeler la fonction d'insertion dans la base de données
                reponse = update_profil(cursor, profil_info)
                
                # Valider la transaction
                cursor.commit()

            return jsonify({"SL_MESSAGE": "Insertion réussie!", "SL_RESULTAT": 'TRUE', "data": reponse}), 200

        except Exception as e:
            cursor.rollback()
            return jsonify({"SL_MESSAGE": f"Erreur lors de l'insertion : {str(e)}", "SL_RESULTAT": 'FALSE'}), 200
   
@api_bp.route('/delete_profil', methods=['POST'])
def pvgdelete_profil():
    # Récupérer les données du corps de la requête
    request_data = request.json

    for row in request_data['Objet']:
        profil_info = {}

        try:
            # Validation des chaînes de caractères
            profil_info['PO_CODEPROFIL'] = str(row.get('PO_CODEPROFIL', ''))
        

        except ValueError as e:
            # Retourner un message d'erreur en cas de problème de type de données
            return jsonify({"SL_MESSAGE": f"Erreur de type de données : {str(e)}", "SL_RESULTAT": 'FALSE'}), 200
        
        except Exception as e:
            # Retourner un message d'erreur en cas d'exception générale
            return jsonify({"SL_MESSAGE": f"Erreur inattendue : {str(e)}", "SL_RESULTAT": 'FALSE'}), 200

        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion:
                cursor = db_connexion.cursor()
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction d'insertion dans la base de données
                reponse = delete_profil(cursor, profil_info)
                
                # Valider la transaction
                cursor.commit()

            return jsonify({"SL_MESSAGE": "Insertion réussie!", "SL_RESULTAT": 'TRUE', "data": reponse}), 200

        except Exception as e:
            cursor.rollback()
            return jsonify({"SL_MESSAGE": f"{str(e)}", "SL_RESULTAT": 'FALSE'}), 200
 




################################################################
#                 GESTION DES PROFILS                     #
################################################################

################################################################
#                 GESTION DES PROFILS                     #
################################################################

################################################################
#                 GESTION DES UTILISATEURS                     #
################################################################


@api_bp.route('/insert_operateur', methods=['POST'])
def pvginsert_operateur():
    # Récupérer les données du corps de la requête
    request_data = request.json

    for row in request_data['Objet']:
        operateur_info = {}

        try:
            # Validation des chaînes de caractères
            operateur_info['OP_CODEOPERATEUR'] = str(row.get('OP_CODEOPERATEUR', ''))
            operateur_info['AG_CODEAGENCE'] = str(row.get('AG_CODEAGENCE', ''))
            operateur_info['PO_CODEPROFIL'] = str(row.get('PO_CODEPROFIL', ''))
            operateur_info['SR_CODESERVICE'] = str(row.get('SR_CODESERVICE', ''))
            operateur_info['OP_NOMPRENOM'] = str(row.get('OP_NOMPRENOM', ''))
            operateur_info['OP_TELEPHONE'] = str(row.get('OP_TELEPHONE', ''))
            operateur_info['OP_EMAIL'] = str(row.get('OP_EMAIL', ''))
            operateur_info['OP_LOGIN'] = str(row.get('OP_LOGIN', ''))
            operateur_info['OP_MOTPASSE'] = str(row.get('OP_MOTPASSE', ''))
            operateur_info['OP_URLPHOTO'] = str(row.get('OP_URLPHOTO', ''))
            operateur_info['OP_ACTIF'] = str(row.get('OP_ACTIF', ''))
            operateur_info['PL_CODENUMCOMPTECAISSE'] = str(row.get('PL_CODENUMCOMPTECAISSE', ''))
            operateur_info['PL_CODENUMCOMPTECOFFRE'] = str(row.get('PL_CODENUMCOMPTECOFFRE', ''))
            operateur_info['PL_CODENUMCOMPTEPROVISOIRE'] = str(row.get('PL_CODENUMCOMPTEPROVISOIRE', ''))
            operateur_info['PL_CODENUMCOMPTEWAVE'] = str(row.get('PL_CODENUMCOMPTEWAVE', ''))
            operateur_info['PL_CODENUMCOMPTEMTN'] = str(row.get('PL_CODENUMCOMPTEMTN', ''))
            operateur_info['PL_CODENUMCOMPTEORANGE'] = str(row.get('PL_CODENUMCOMPTEORANGE', ''))
            operateur_info['PL_CODENUMCOMPTEMOOV'] = str(row.get('PL_CODENUMCOMPTEMOOV', ''))
            operateur_info['PL_CODENUMCOMPTECHEQUE'] = str(row.get('PL_CODENUMCOMPTECHEQUE', ''))
            operateur_info['PL_CODENUMCOMPTEVIREMENT'] = str(row.get('PL_CODENUMCOMPTEVIREMENT', ''))
            operateur_info['OP_DATESAISIE'] = parse_datetime(row.get('OP_DATESAISIE'))
            operateur_info['CODECRYPTAGE'] = ''
            
            AG_CODEAGENCE = None
            JT_DATEJOURNEETRAVAIL = None
            OP_CODEOPERATEUR = None
            if request_data['Objet'][0]['clsObjetEnvoi'].get('OE_A', ''):
                AG_CODEAGENCE = str(request_data['Objet'][0]['clsObjetEnvoi'].get('OE_A', '')) 
            if request_data['Objet'][0]['clsObjetEnvoi'].get('OE_J', ''):
                JT_DATEJOURNEETRAVAIL  = str(request_data['Objet'][0]['clsObjetEnvoi'].get('OE_J', ''))
            if request_data['Objet'][0]['clsObjetEnvoi'].get('OE_Y', ''):
                OP_CODEOPERATEUR  = str(request_data['Objet'][0]['clsObjetEnvoi'].get('OE_Y', '')) 

            # Préparer les paramètres pour la fonction
            if AG_CODEAGENCE and JT_DATEJOURNEETRAVAIL and OP_CODEOPERATEUR:
                vpp_critere = (AG_CODEAGENCE, JT_DATEJOURNEETRAVAIL, OP_CODEOPERATEUR)
            elif AG_CODEAGENCE and JT_DATEJOURNEETRAVAIL:
                vpp_critere = (AG_CODEAGENCE, JT_DATEJOURNEETRAVAIL)
            elif AG_CODEAGENCE:
                vpp_critere = (AG_CODEAGENCE,)
            else:
                vpp_critere = ()

        except ValueError as e:
            # Retourner un message d'erreur en cas de problème de type de données
            return jsonify({"SL_MESSAGE": f"Erreur de type de données : {str(e)}", "SL_RESULTAT": 'FALSE'}), 200
        
        except Exception as e:
            # Retourner un message d'erreur en cas d'exception générale
            return jsonify({"SL_MESSAGE": f"Erreur inattendue : {str(e)}", "SL_RESULTAT": 'FALSE'}), 200

        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion:
                cursor = db_connexion.cursor()
                cursor.execute("BEGIN TRANSACTION")
                
                response = test_journee_fermee(cursor, *vpp_critere)

                if response[0]['NBRE'] == 0:
                    return jsonify({"SL_MESSAGE": 'Cette journée a été déjà fermée ou non encore ouverte !' ,"SL_RESULTAT": 'FALSE'})
        
                # Appeler la fonction d'insertion dans la base de données
                reponse = insert_operateur(cursor, operateur_info)
                
                # Valider la transaction
                cursor.commit()

            return jsonify({"SL_MESSAGE": "Insertion réussie!", "SL_RESULTAT": 'TRUE', "data": reponse}), 200

        except Exception as e:
            cursor.rollback()
            return jsonify({"SL_MESSAGE": f"Erreur lors de l'insertion : {str(e)}", "SL_RESULTAT": 'FALSE'}), 200

        

@api_bp.route('/update_compte_utilisateur', methods=['POST'])
def pvgupdate_compte_utilisateur():
    # Récupérer les données du corps de la requête
    request_data = request.json

    for row in request_data['Objet']:
        operateur_info = {}

        try:
            # Validation des chaînes de caractères
            operateur_info['OP_CODEOPERATEUR'] = str(row.get('OP_CODEOPERATEUR', ''))
            operateur_info['AG_CODEAGENCE'] = str(row.get('AG_CODEAGENCE', ''))
            operateur_info['PO_CODEPROFIL'] = str(row.get('PO_CODEPROFIL', ''))
            operateur_info['SR_CODESERVICE'] = str(row.get('SR_CODESERVICE', ''))
            operateur_info['OP_NOMPRENOM'] = str(row.get('OP_NOMPRENOM', ''))
            operateur_info['OP_TELEPHONE'] = str(row.get('OP_TELEPHONE', ''))
            operateur_info['OP_EMAIL'] = str(row.get('OP_EMAIL', ''))
            operateur_info['OP_LOGIN'] = str(row.get('OP_LOGIN', ''))
            operateur_info['OP_MOTPASSE'] = str(row.get('OP_MOTPASSE', ''))
            operateur_info['OP_URLPHOTO'] = str(row.get('OP_URLPHOTO', ''))
            operateur_info['OP_ACTIF'] = str(row.get('OP_ACTIF', ''))
            operateur_info['PL_CODENUMCOMPTECAISSE'] = str(row.get('PL_CODENUMCOMPTECAISSE', ''))
            operateur_info['PL_CODENUMCOMPTECOFFRE'] = str(row.get('PL_CODENUMCOMPTECOFFRE', ''))
            operateur_info['PL_CODENUMCOMPTEPROVISOIRE'] = str(row.get('PL_CODENUMCOMPTEPROVISOIRE', ''))
            operateur_info['PL_CODENUMCOMPTEWAVE'] = str(row.get('PL_CODENUMCOMPTEWAVE', ''))
            operateur_info['PL_CODENUMCOMPTEMTN'] = str(row.get('PL_CODENUMCOMPTEMTN', ''))
            operateur_info['PL_CODENUMCOMPTEORANGE'] = str(row.get('PL_CODENUMCOMPTEORANGE', ''))
            operateur_info['PL_CODENUMCOMPTEMOOV'] = str(row.get('PL_CODENUMCOMPTEMOOV', ''))
            operateur_info['PL_CODENUMCOMPTECHEQUE'] = str(row.get('PL_CODENUMCOMPTECHEQUE', ''))
            operateur_info['PL_CODENUMCOMPTEVIREMENT'] = str(row.get('PL_CODENUMCOMPTEVIREMENT', ''))
            operateur_info['OP_DATESAISIE'] = parse_datetime(row.get('OP_DATESAISIE'))
            operateur_info['CODECRYPTAGE'] = ""

            AG_CODEAGENCE = None
            JT_DATEJOURNEETRAVAIL = None
            OP_CODEOPERATEUR = None
            if request_data['Objet'][0]['clsObjetEnvoi'].get('OE_A', ''):
                AG_CODEAGENCE = str(request_data['Objet'][0]['clsObjetEnvoi'].get('OE_A', '')) 
            if request_data['Objet'][0]['clsObjetEnvoi'].get('OE_J', ''):
                JT_DATEJOURNEETRAVAIL  = str(request_data['Objet'][0]['clsObjetEnvoi'].get('OE_J', ''))
            if request_data['Objet'][0]['clsObjetEnvoi'].get('OE_Y', ''):
                OP_CODEOPERATEUR  = str(request_data['Objet'][0]['clsObjetEnvoi'].get('OE_Y', '')) 

            # Préparer les paramètres pour la fonction
            if AG_CODEAGENCE and JT_DATEJOURNEETRAVAIL and OP_CODEOPERATEUR:
                vpp_critere = (AG_CODEAGENCE, JT_DATEJOURNEETRAVAIL, OP_CODEOPERATEUR)
            elif AG_CODEAGENCE and JT_DATEJOURNEETRAVAIL:
                vpp_critere = (AG_CODEAGENCE, JT_DATEJOURNEETRAVAIL)
            elif AG_CODEAGENCE:
                vpp_critere = (AG_CODEAGENCE,)
            else:
                vpp_critere = ()
            
        except ValueError as e:
            # Retourner un message d'erreur en cas de problème de type de données
            return jsonify({"SL_MESSAGE": f"Erreur de type de données : {str(e)}", "SL_RESULTAT": 'FALSE'}), 200
        
        except Exception as e:
            # Retourner un message d'erreur en cas d'exception générale
            return jsonify({"SL_MESSAGE": f"Erreur inattendue : {str(e)}", "SL_RESULTAT": 'FALSE'}), 200

        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion:
                cursor = db_connexion.cursor()
                cursor.execute("BEGIN TRANSACTION")
                
                response = test_journee_fermee(cursor, *vpp_critere)

                if response[0]['NBRE'] == 0:
                    return jsonify({"SL_MESSAGE": 'Cette journée a été déjà fermée ou non encore ouverte !' ,"SL_RESULTAT": 'FALSE'})
        
                # Appeler la fonction d'insertion dans la base de données
                reponse = update_compte_utilisateur(cursor, operateur_info)
                
                # Valider la transaction
                cursor.commit()

            return jsonify({"SL_MESSAGE": "Insertion réussie!", "SL_RESULTAT": 'TRUE', "data": reponse}), 200

        except Exception as e:
            cursor.rollback()
            return jsonify({"SL_MESSAGE": f"Erreur lors de l'insertion : {str(e)}", "SL_RESULTAT": 'FALSE'}), 200

        #finally:
            cursor.close()
            
            
@api_bp.route('/delete_compte_utilisateur', methods=['POST'])
def pvgdelete_compte_utilisateur():
    # Récupérer les données du corps de la requête
    request_data = request.json

    for row in request_data['Objet']:
        operateur_info = {}

        try:
            # Validation des chaînes de caractères
            operateur_info['OP_CODEOPERATEUR'] = str(row.get('OP_CODEOPERATEUR', ''))
            operateur_info['AG_CODEAGENCE'] = str(row.get('AG_CODEAGENCE', ''))
            

        except ValueError as e:
            # Retourner un message d'erreur en cas de problème de type de données
            return jsonify({"SL_MESSAGE": f"Erreur de type de données : {str(e)}", "SL_RESULTAT": 'FALSE'}), 200
        
        except Exception as e:
            # Retourner un message d'erreur en cas d'exception générale
            return jsonify({"SL_MESSAGE": f"Erreur inattendue : {str(e)}", "SL_RESULTAT": 'FALSE'}), 200

        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion:
                cursor = db_connexion.cursor()
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction d'insertion dans la base de données
                reponse = delete_compte_utilisateur(cursor, operateur_info)
                
                # Valider la transaction
                cursor.commit()

            return jsonify({"SL_MESSAGE": "Insertion réussie!", "SL_RESULTAT": 'TRUE', "data": reponse}), 200

        except Exception as e:
            cursor.rollback()
            return jsonify({"SL_MESSAGE": f"Erreur lors de l'insertion : {str(e)}", "SL_RESULTAT": 'FALSE'}), 200

        #finally:
            cursor.close()            
            

################################################################
#                 GESTION DES UTILISATEURS                                                        #
################################################################


################################################################
#                           GESTION COMBOS                                                                    #
################################################################
@api_bp.route('/get_solde_mouvement_comptable', methods=['POST'])
def pvgget_solde_mouvement_comptable():
    request_data = request.json
    
    for row in request_data['Objet']:
        user_info = {}

        # Validation et récupération des données pour la suppression
        user_info['AG_CODEAGENCE'] = str(row.get('AG_CODEAGENCE', '')) 
        user_info['FT_CODEFACTURE'] = str(row.get('FT_CODEFACTURE', '')) 
        user_info['OP_CODEOPERATEUR'] = str(row.get('OP_CODEOPERATEUR', ''))
        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                if user_info['AG_CODEAGENCE']:  # Si une valeur est fournie
                    response = get_solde_mouvement_comptable(db_connexion, str(row.get('AG_CODEAGENCE', '')), str(row.get('FT_CODEFACTURE', '')), str(row.get('OP_CODEOPERATEUR', '')))
                
                
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE' , "MONTANTAREGLER": + response})
            
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()    


@api_bp.route('/ComboTableLabelAgence', methods=['POST'])
def ComboTableLabelAgence():
    request_data = request.json
    
    for row in request_data['Objet']:
        user_info = {}

        # Validation et récupération des données pour la suppression
        user_info['AG_CODEAGENCE'] = str(row.get('AG_CODEAGENCE', '')) 
        
        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                if user_info['AG_CODEAGENCE']:  # Si une valeur est fournie
                    response = pvgComboTableLabelAgence(db_connexion, str(row.get('AG_CODEAGENCE', '')))
                else:  # Sinon, on appelle sans paramètre
                    response = pvgComboTableLabelAgence(db_connexion)
                
                
            if len(response) > 0 :
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": 'Aucun élément trouvé', "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()            

@api_bp.route('/pvgComboExercice', methods=['POST'])
def ComboExercice():
    request_data = request.json
    
    for row in request_data['Objet']:
        user_info = {}

        # Validation et récupération des données pour la suppression
        AG_CODEAGENCE = None
        if row.get('AG_CODEAGENCE', ''):
           AG_CODEAGENCE = str(row.get('AG_CODEAGENCE', '')) 
        

        # Préparer les paramètres pour la fonction
        if AG_CODEAGENCE:
            vpp_critere = (AG_CODEAGENCE,)
        else:
            vpp_critere = ()
        
        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = pvgComboExercice(db_connexion, *vpp_critere)
                
                
                
            if len(response) > 0 :
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": 'Aucun élément trouvé', "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()  
            
            
@api_bp.route('/pvgComboPeriodicite', methods=['POST'])
def ComboPeriodicite():
    request_data = request.json
    
    for row in request_data['Objet']:
        user_info = {}

        
        
        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = pvgComboPeriodicite(db_connexion)
                
                
                
            if len(response) > 0 :
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": 'Aucun élément trouvé', "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()                        
 
 
@api_bp.route('/pvgComboperiode', methods=['POST'])
def Comboperiode():
    request_data = request.json
    
    for row in request_data['Objet']:
        user_info = {}

        # Validation et récupération des données pour la suppression
       
        PE_CODEPERIODICITE = str(row.get('PE_CODEPERIODICITE', '')) 
        if PE_CODEPERIODICITE is None or PE_CODEPERIODICITE == '':
           return jsonify([{"SL_MESSAGE": "Données manquantes. voir PE_CODEPERIODICITE", "SL_RESULTAT": 'FALSE'}])


       
        
        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = pvgComboperiode(db_connexion, PE_CODEPERIODICITE)
                
                
                
            if len(response) > 0 :
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": 'Aucun élément trouvé', "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()   
 
 
 
@api_bp.route('/pvgPeriodiciteDateDebutFin', methods=['POST'])
def ComboPeriodiciteDateDebutFin():
    request_data = request.json
    
    for row in request_data['Objet']:
        user_info = {}

        # Validation et récupération des données EX_EXERCICE,MO_CODEMOIS,PE_CODEPERIODICITE
        EX_EXERCICE = None
        if row.get('EX_EXERCICE', ''):
           EX_EXERCICE = str(row.get('EX_EXERCICE', '')) 
           
        MO_CODEMOIS = None
        if row.get('MO_CODEMOIS', ''):
           MO_CODEMOIS = str(row.get('MO_CODEMOIS', '')) 
        
        PE_CODEPERIODICITE = None
        if row.get('PE_CODEPERIODICITE', ''):
           PE_CODEPERIODICITE = str(row.get('PE_CODEPERIODICITE', ''))  
           
        if PE_CODEPERIODICITE is None or EX_EXERCICE is None or MO_CODEMOIS is None:
           return jsonify({"SL_MESSAGE": "Données manquantes. voir PE_CODEPERIODICITE ou EX_EXERCICE ou MO_CODEMOIS", "SL_RESULTAT": 'FALSE'})


       
        
        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = pvgPeriodiciteDateDebutFin(db_connexion, EX_EXERCICE,MO_CODEMOIS,PE_CODEPERIODICITE)
                
                
                
            if len(response) > 0 :
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": 'Aucun élément trouvé', "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()  
 
@api_bp.route('/pvgComboOperateur', methods=['POST'])
def ComboOperateur():
    request_data = request.json
    
    for row in request_data['Objet']:
        user_info = {}

        # Validation et récupération des données pour la suppression
       
        AG_CODEAGENCE = None
        OP_CODEOPERATEUR = None
        if row.get('AG_CODEAGENCE', ''):
           AG_CODEAGENCE = str(row.get('AG_CODEAGENCE', '')) 
        if row.get('OP_CODEOPERATEUR', ''):
           OP_CODEOPERATEUR  = str(row.get('OP_CODEOPERATEUR', '')) 

        # Préparer les paramètres pour la fonction
        if AG_CODEAGENCE and OP_CODEOPERATEUR:
            vpp_critere = (AG_CODEAGENCE, OP_CODEOPERATEUR)
        elif AG_CODEAGENCE:
            vpp_critere = (AG_CODEAGENCE,)
        else:
            vpp_critere = ()
        
        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction 
                response = pvgComboOperateur(db_connexion, *vpp_critere)
               
                
                
            if len(response) > 0 :
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": 'Aucun élément trouvé', "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()            


@api_bp.route('/pvgComboOperateurCaisse', methods=['POST'])
def ComboOperateurCaisse():
    request_data = request.json
    
    for row in request_data['Objet']:
        user_info = {}

        # Validation et récupération des données pour la suppression
       
        AG_CODEAGENCE = None
        OP_CODEOPERATEUR = None
        if row.get('AG_CODEAGENCE', ''):
           AG_CODEAGENCE = str(row.get('AG_CODEAGENCE', '')) 
        if row.get('OP_CODEOPERATEUR', ''):
           OP_CODEOPERATEUR  = str(row.get('OP_CODEOPERATEUR', '')) 

        # Préparer les paramètres pour la fonction
        if AG_CODEAGENCE and OP_CODEOPERATEUR:
            vpp_critere = (AG_CODEAGENCE, OP_CODEOPERATEUR)
        elif AG_CODEAGENCE:
            vpp_critere = (AG_CODEAGENCE,)
        else:
            vpp_critere = ()
        
        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction 
                response = pvgComboOperateurCaisse(db_connexion, *vpp_critere)
               
                
                
            if len(response) > 0 :
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": 'Aucun élément trouvé', "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()            
      
      
         
@api_bp.route('/pvgComboModeReglement', methods=['POST'])
def ComboModeReglement():
    request_data = request.json
    
    for row in request_data['Objet']:
        user_info = {}

        
        
        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = pvgComboModeReglement(db_connexion)
                
                
                
            if len(response) > 0 :
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": 'Aucun élément trouvé', "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()  
            
@api_bp.route('/pvgComboActe', methods=['POST'])
def ComboActe():
    request_data = request.json
    
    for row in request_data['Objet']:
        user_info = {}
        
        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = pvgComboActe(db_connexion)
                
                
                
            if len(response) > 0 :
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": 'Aucun élément trouvé', "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()   
            
            
            
@api_bp.route('/sexe', methods=['POST'])
def ComboSexe():
    request_data = request.json
    
    for row in request_data['Objet']:
        user_info = {}
        
        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = pvgComboSexe(db_connexion)
                
            if len(response) > 0 :
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": 'Aucun élément trouvé', "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()
            
            
            
@api_bp.route('/profession', methods=['POST'])
def ComboProfession():
    request_data = request.json
    
    for row in request_data['Objet']:
        user_info = {}
        
        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = pvgComboProfession(db_connexion)
                
            if len(response) > 0 :
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": 'Aucun élément trouvé', "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()



@api_bp.route('/pvgComboAssurance', methods=['POST'])
def ComboAssurance():
    request_data = request.json
    
    for row in request_data['Objet']:
        user_info = {}
        
        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = pvgComboAssurance(db_connexion)
                
                
                
            if len(response) > 0 :
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": 'Aucun élément trouvé', "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()
@api_bp.route('/pvgComboAssure', methods=['POST'])
def ComboAssure():
    request_data = request.json
    
    for row in request_data['Objet']:
        user_info = {}
        
        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = pvgComboAssure(db_connexion)
                
                
                
            if len(response) > 0 :
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": 'Aucun élément trouvé', "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()       
 
@api_bp.route('/pvgComboJournal', methods=['POST'])
def ComboJournal():
    request_data = request.json
    
    for row in request_data['Objet']:
        user_info = {}
        
        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = pvgComboJournal(db_connexion)
                
                
            if len(response) > 0 :
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": 'Aucun élément trouvé', "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()     

@api_bp.route('/pvgComboTypeshemacomptable', methods=['POST'])
def ComboTypeshemacomptable():
    request_data = request.json
    
    for row in request_data['Objet']:
        user_info = {}
        
        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = pvgComboTypeshemacomptable(db_connexion)
                
                
            if len(response) > 0 :
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": 'Aucun élément trouvé', "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()     
  
@api_bp.route('/pvgComboTypespiece', methods=['POST'])
def ComboTypespiece():
    request_data = request.json
    
    for row in request_data['Objet']:
        user_info = {}
        
        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = pvgComboTypespiece(db_connexion)
                
                
            if len(response) > 0 :
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": 'Aucun élément trouvé', "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()     
  

@api_bp.route('/pvgComboTypeTiers', methods=['POST'])
def ComboTypeTiers():
    request_data = request.json
    
    for row in request_data['Objet']:
        user_info = {}
        
        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = pvgComboTypeTiers(db_connexion)
                
                
            if len(response) > 0 :
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": 'Aucun élément trouvé', "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()   


  
@api_bp.route('/pvgComboTypeshemacomptableVersement', methods=['POST'])
def ComboTypeshemacomptableVersement():
    request_data = request.json
    
    for row in request_data['Objet']:
        user_info = {}
        
        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = pvgComboTypeshemacomptableVersement(db_connexion)
                
                
            if len(response) > 0 :
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": 'Aucun élément trouvé', "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()   
  
@api_bp.route('/pvgChargerDansDataSetSC_SCHEMACOMPTABLECODE', methods=['POST'])
def ChargerDansDataSetSC_SCHEMACOMPTABLECODE():
    request_data = request.json
    
    for row in request_data['Objet']:
        user_info = {}

        # Validation et récupération des données pour la suppression
      
        TS_CODETYPESCHEMACOMPTABLE = None
        if row.get('TS_CODETYPESCHEMACOMPTABLE', ''):
           TS_CODETYPESCHEMACOMPTABLE = str(row.get('TS_CODETYPESCHEMACOMPTABLE', '')) 
        
           
        # Préparer les paramètres pour la fonction
        
        if TS_CODETYPESCHEMACOMPTABLE :
            vpp_critere = (TS_CODETYPESCHEMACOMPTABLE,) 
        else:
            vpp_critere = ()
        
        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = pvgChargerDansDataSetSC_SCHEMACOMPTABLECODE(db_connexion, *vpp_critere)
                
                
                
            if len(response) > 0 :
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": 'Aucun élément trouvé', "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()    

@api_bp.route('/pvgComboCompte', methods=['POST'])
def ComboCompte():
    request_data = request.json
    
    for row in request_data['Objet']:
        user_info = {}

        # Validation et récupération des données pour la suppression
        SO_CODESOCIETE = None
        if row.get('SO_CODESOCIETE', ''):
           SO_CODESOCIETE = str(row.get('SO_CODESOCIETE', '')) 
        PL_NUMCOMPTE = None
        if row.get('PL_NUMCOMPTE', ''):
           PL_NUMCOMPTE = str(row.get('PL_NUMCOMPTE', '')) 
        PL_TYPECOMPTE = None
        if row.get('PL_TYPECOMPTE', ''):
           PL_TYPECOMPTE = str(row.get('PL_TYPECOMPTE', '')) 
           
        # Préparer les paramètres pour la fonction
        if SO_CODESOCIETE and PL_NUMCOMPTE is None and PL_TYPECOMPTE is None:
            vpp_critere = (SO_CODESOCIETE,)
        elif SO_CODESOCIETE and PL_NUMCOMPTE and PL_TYPECOMPTE is None:
            vpp_critere = (SO_CODESOCIETE,PL_NUMCOMPTE) 
        elif PL_TYPECOMPTE:
            if PL_NUMCOMPTE is None:
              PL_NUMCOMPTE = ''
            vpp_critere = (SO_CODESOCIETE,PL_NUMCOMPTE,PL_TYPECOMPTE)       
        else:
            vpp_critere = ()
        
        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = pvgComboCompte(db_connexion, *vpp_critere)
                
                
                
            if len(response) > 0 :
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify([{"SL_MESSAGE": 'Aucun élément trouvé', "SL_RESULTAT": 'FALSE'}])
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()          
            
            
            
@api_bp.route('/pays', methods=['POST'])
def ComboPays():
    request_data = request.json
    
    for row in request_data['Objet']:
        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = pvgComboPays(db_connexion)
                
            if len(response) > 0 :
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": 'Aucun élément trouvé', "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
            
            
            
@api_bp.route('/ville', methods=['POST'])
def ComboVille():
    request_data = request.json
    
    for row in request_data['Objet']:
        ville_info = {}
        ville_info['PY_CODEPAYS'] = str(row.get('PY_CODEPAYS', '')) 
        
        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = pvgComboVille(db_connexion, ville_info)
                
            if len(response) > 0 :
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": 'Aucun élément trouvé', "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})



@api_bp.route('/solde_compte_operateur', methods=['POST'])
def pvgGetSoldeCompteOperateur():
    request_data = request.json
    
    for row in request_data['Objet']:
        solde_cpte_op = {}
        solde_cpte_op['AG_CODEAGENCE'] = str(row.get('AG_CODEAGENCE', '')) 
        solde_cpte_op['PL_CODENUMCOMPTE'] = str(row.get('PL_CODENUMCOMPTE', '')) 
        solde_cpte_op['JT_DATEJOURNEETRAVAIL'] = str(row.get('JT_DATEJOURNEETRAVAIL', '')) 
        
        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = solde_du_compte(cursor, solde_cpte_op)
                
            if len(response) > 0 :
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": 'Aucun élément trouvé', "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            cursor.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
                                
################################################################
#                   FIN GESTION COMBOS                         #
################################################################



################################################################
#                                                             GESTION DES PARAMETRES                                                                  #
################################################################

@api_bp.route('/liste_operateur_par_type', methods=['POST'])
def pvgGetOperateurParType():
    request_data = request.json
    
    if 'Objet' not in request_data:
        return jsonify({"SL_MESSAGE": "Données manquantes.code erreur (300) voir le noeud Objet", "SL_RESULTAT": 'FALSE'})

    for row in request_data['Objet']:
        clsListeOperateur = {}
        # Validation et récupération des données pour la suppression
   
        clsListeOperateur['OP_CODEOPERATEUR'] = row.get('OP_CODEOPERATEUR')
        clsListeOperateur['AG_CODEAGENCE'] = row.get('AG_CODEAGENCE')
        clsListeOperateur['PO_CODEPROFIL'] = row.get('PO_CODEPROFIL')
        clsListeOperateur['SR_CODESERVICE'] = row.get('SR_CODESERVICE')
        clsListeOperateur['OP_NOMBRECONNEXION'] = row.get('OP_NOMBRECONNEXION')
        clsListeOperateur['TYPEOPERATION'] = row.get('TYPEOPERATION')
        
        required_keys = ['AG_CODEAGENCE']

        # Vérifier si toutes les clés requises existent dans le dictionnaire
        if not all(key in clsListeOperateur for key in required_keys):
            return jsonify({"SL_MESSAGE": "Données manquantes ou incorrectes. Code erreur (301)", "SL_RESULTAT": 'FALSE'})
        # Vérification que toutes les données obligatoires sont présentes
        if not all([clsListeOperateur['AG_CODEAGENCE']]):
           return jsonify({"SL_MESSAGE": "Données manquantes ou incorrectes.code erreur (301)", "SL_RESULTAT": 'FALSE'})

        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression ou récupération
                response = liste_operateur(db_connexion, clsListeOperateur)
                
                if response:
                    cursor.execute("COMMIT")
                    return jsonify({"SL_MESSAGE": "Opération effectuée avec succès !!!", "SL_RESULTAT": 'TRUE'}, response)
                else:
                    result = {}
	
                    result['SL_MESSAGE'] = "Opérateur non trouvé ou autre erreur."
                    result['SL_RESULTAT'] = "FALSE"
                    # Ajouter le dictionnaire à la liste des résultats
                    response.append(result)
            
                    cursor.execute("ROLLBACK")
                    return jsonify(response)
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors du chargement : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()
            
            
            
@api_bp.route('/liste_agence', methods=['POST'])
def pvgGetAgence():
    request_data = request.json
    
    if 'Objet' not in request_data:
        return jsonify({"SL_MESSAGE": "Données manquantes.code erreur (300) voir le noeud Objet", "SL_RESULTAT": 'FALSE'})

    for row in request_data['Objet']:

        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression ou récupération
                response = liste_des_agences(db_connexion)
                
                if response:
                    cursor.execute("COMMIT")
                    return jsonify({"SL_MESSAGE": "Opération effectuée avec succès !!!", "SL_RESULTAT": 'TRUE'}, response)
                else:
                    result = {}
	
                    result['SL_MESSAGE'] = "Agence non trouvée ou autre erreur."
                    result['SL_RESULTAT'] = "FALSE"
                    # Ajouter le dictionnaire à la liste des résultats
                    response.append(result)
            
                    cursor.execute("ROLLBACK")
                    return jsonify(response)
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors du chargement : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()



@api_bp.route('/modifier_agence', methods=['POST'])
def modificationAgence():
    request_data = request.json
    
    if 'Objet' not in request_data:
        return jsonify({"SL_MESSAGE": "Données manquantes.code erreur (300) voir le noeud Objet", "SL_RESULTAT": 'FALSE'})

    for row in request_data['Objet']:
        clsAgence = {}
        clsAgence['AG_AGENCECODE'] = str(row.get('AG_AGENCECODE', ''))
        clsAgence['AG_CODEAGENCE'] = str(row.get('AG_CODEAGENCE', ''))
        clsAgence['SO_CODESOCIETE'] = str(row.get('SO_CODESOCIETE', ''))
        clsAgence['AG_RAISONSOCIAL'] = str(row.get('AG_RAISONSOCIAL', ''))
        clsAgence['AG_DATECREATION'] = str(row.get('AG_DATECREATION', ''))
        clsAgence['AG_NUMEROAGREMENT'] = str(row.get('AG_NUMEROAGREMENT', ''))
        clsAgence['OP_CODEOPERATEUR'] = str(row.get('OP_CODEOPERATEUR', ''))
        clsAgence['AG_BOITEPOSTAL'] = str(row.get('AG_BOITEPOSTAL', ''))
        clsAgence['VL_CODEVILLE'] = str(row.get('VL_CODEVILLE', ''))
        clsAgence['AG_ADRESSEGEOGRAPHIQUE'] = str(row.get('AG_ADRESSEGEOGRAPHIQUE', ''))
        clsAgence['AG_TELEPHONE'] = str(row.get('AG_TELEPHONE', ''))
        clsAgence['AG_EMAIL'] = str(row.get('AG_EMAIL', ''))
        clsAgence['AG_EMAILMOTDEPASSE'] = str(row.get('AG_EMAILMOTDEPASSE', ''))
        clsAgence['TYPEOPERATION'] = str(row.get('TYPEOPERATION', ''))

        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression ou récupération
                modifier_des_agences(cursor, clsAgence, request_data['Objet'][0]['AG_EMAIL_DESTI'], request_data['Objet'][0]['AG_TELEPHONE_DESTI'])
                
                cursor.execute("COMMIT")
                return jsonify({"SL_MESSAGE": "Opération effectuée avec succès !!!", "SL_RESULTAT": 'TRUE'})
             
        
        except Exception as e:
            cursor.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors du chargement : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        # finally:
            # cursor.close()
            
            

@api_bp.route('/liste_profil', methods=['POST'])
def pvgGetProfil():
    request_data = request.json
    
    if 'Objet' not in request_data:
        return jsonify({"SL_MESSAGE": "Données manquantes.code erreur (300) voir le noeud Objet", "SL_RESULTAT": 'FALSE'})

    for row in request_data['Objet']:

        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression ou récupération
                response = liste_des_profils(db_connexion)
                
                if response:
                    cursor.execute("COMMIT")
                    return jsonify({"SL_MESSAGE": "Opération effectuée avec succès !!!", "SL_RESULTAT": 'TRUE'}, response)
                else:
                    result = {}
	
                    result['SL_MESSAGE'] = "Profil non trouvé ou autre erreur."
                    result['SL_RESULTAT'] = "FALSE"
                    # Ajouter le dictionnaire à la liste des résultats
                    response.append(result)
            
                    cursor.execute("ROLLBACK")
                    return jsonify(response)
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors du chargement : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()



@api_bp.route('/liste_service', methods=['POST'])
def pvgGetService():
    request_data = request.json
    
    if 'Objet' not in request_data:
        return jsonify({"SL_MESSAGE": "Données manquantes.code erreur (300) voir le noeud Objet", "SL_RESULTAT": 'FALSE'})

    for row in request_data['Objet']:

        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression ou récupération
                response = liste_des_services(db_connexion)
                
                if response:
                    cursor.execute("COMMIT")
                    return jsonify({"SL_MESSAGE": "Opération effectuée avec succès !!!", "SL_RESULTAT": 'TRUE'}, response)
                else:
                    result = {}
	
                    result['SL_MESSAGE'] = "Service non trouvé ou autre erreur."
                    result['SL_RESULTAT'] = "FALSE"
                    # Ajouter le dictionnaire à la liste des résultats
                    response.append(result)
            
                    cursor.execute("ROLLBACK")
                    return jsonify(response)
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors du chargement : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()
            
            

@api_bp.route('/liste_parametre', methods=['POST'])
def pvgGetParametre():
    request_data = request.json
    
    if 'Objet' not in request_data:
        return jsonify({"SL_MESSAGE": "Données manquantes.code erreur (300) voir le noeud Objet", "SL_RESULTAT": 'FALSE'})

    for row in request_data['Objet']:

        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression ou récupération
                response = liste_des_parametres(db_connexion)
                
                if response:
                    cursor.execute("COMMIT")
                    return jsonify({"SL_MESSAGE": "Opération effectuée avec succès !!!", "SL_RESULTAT": 'TRUE'}, response)
                else:
                    result = {}
	
                    result['SL_MESSAGE'] = "Paramètre non trouvé ou autre erreur."
                    result['SL_RESULTAT'] = "FALSE"
                    # Ajouter le dictionnaire à la liste des résultats
                    response.append(result)
            
                    cursor.execute("ROLLBACK")
                    return jsonify(response)
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors du chargement : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()



@api_bp.route('/modifier_parametrage', methods=['POST'])
def modificationParametrage():
    request_data = request.json
    
    if 'Objet' not in request_data:
        return jsonify({"SL_MESSAGE": "Données manquantes.code erreur (300) voir le noeud Objet", "SL_RESULTAT": 'FALSE'})

    for row in request_data['Objet']:
        clsAgence = {}
        clsAgence['PP_CODEPARAMETRE'] = str(row.get('PP_CODEPARAMETRE', ''))
        clsAgence['SO_CODESOCIETE'] = str(row.get('SO_CODESOCIETE', ''))
        clsAgence['PP_LIBELLE'] = str(row.get('PP_LIBELLE', ''))
        clsAgence['PP_MONTANTMINI'] = str(row.get('PP_MONTANTMINI', ''))
        clsAgence['PP_MONTANTMAXI'] = str(row.get('PP_MONTANTMAXI', ''))
        clsAgence['PP_TAUX'] = str(row.get('PP_TAUX', ''))
        clsAgence['PP_MONTANT'] = str(row.get('PP_MONTANT', ''))
        clsAgence['PP_VALEUR'] = str(row.get('PP_VALEUR', ''))
        clsAgence['PL_CODENUMCOMPTE'] = str(row.get('PL_CODENUMCOMPTE', ''))
        clsAgence['PP_AFFICHER'] = str(row.get('PP_AFFICHER', ''))

        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression ou récupération
                modifier_param(cursor, clsAgence)
                
                cursor.execute("COMMIT")
                return jsonify({"SL_MESSAGE": "Opération effectuée avec succès !!!", "SL_RESULTAT": 'TRUE'})
             
        
        except Exception as e:
            cursor.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors du chargement : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        # finally:
            # cursor.close()
  
  
################################################################
#                    GESTION DES PARAMETRES                    #
################################################################



################################################################
#                      GESTION DES OPERATIONS DE CAISSES       #
################################################################

@api_bp.route('/famille_operation', methods=['POST'])
def pvgGetFamilleOperation():
    request_data = request.json
    
    if 'Objet' not in request_data:
        return jsonify({"SL_MESSAGE": "Données manquantes.code erreur (300) voir le noeud Objet", "SL_RESULTAT": 'FALSE'})

    for row in request_data['Objet']:

        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression ou récupération
                response = liste_des_familles_operations(db_connexion)
                
                if response:
                    cursor.execute("COMMIT")
                    return jsonify({"SL_MESSAGE": "Opération effectuée avec succès !!!", "SL_RESULTAT": 'TRUE'}, response)
                else:
                    result = {}
	
                    result['SL_MESSAGE'] = "Famille d'opération non trouvée ou autre erreur."
                    result['SL_RESULTAT'] = "FALSE"
                    # Ajouter le dictionnaire à la liste des résultats
                    response.append(result)
            
                    cursor.execute("ROLLBACK")
                    return jsonify(response)
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors du chargement : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()
            
            
            
@api_bp.route('/operation', methods=['POST'])
def pvgGetOperation():
    request_data = request.json
    
    if 'Objet' not in request_data:
        return jsonify({"SL_MESSAGE": "Données manquantes.code erreur (300) voir le noeud Objet", "SL_RESULTAT": 'FALSE'})

    for row in request_data['Objet']:
        clsOperation = {}
        clsOperation['FO_CODEFAMILLEOPERATION'] = str(row.get('FO_CODEFAMILLEOPERATION', ''))
        
        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression ou récupération
                response = liste_des_operations(db_connexion, clsOperation)
                
                if response:
                    cursor.execute("COMMIT")
                    return jsonify({"SL_MESSAGE": "Opération effectuée avec succès !!!", "SL_RESULTAT": 'TRUE'}, response)
                else:
                    result = {}
	
                    result['SL_MESSAGE'] = "Opération non trouvée ou autre erreur."
                    result['SL_RESULTAT'] = "FALSE"
                    # Ajouter le dictionnaire à la liste des résultats
                    response.append(result)
            
                    cursor.execute("ROLLBACK")
                    return jsonify(response)
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors du chargement : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()
            
################################################################
#       GESTION DES OPERATIONS DE CAISSES                      #
################################################################




# ################################################################
#       GESTION DES JOURNEES DE TRAVAIL                      #
#################################################################

@api_bp.route('/valeur_scalaire_requete_max_journee', methods=['POST'])
def pvgValeurScalaireRequeteMax():
    request_data = request.json
    
    for row in request_data['Objet']:
        user_info = {}

        # Validation et récupération des données pour la suppression
        AG_CODEAGENCE = None
        JT_DATEJOURNEETRAVAIL = None
        JT_STATUT = None
        if row.get('AG_CODEAGENCE', ''):
           AG_CODEAGENCE = str(row.get('AG_CODEAGENCE', '')) 
        if row.get('JT_DATEJOURNEETRAVAIL', ''):
           JT_DATEJOURNEETRAVAIL = parse_datetime(row.get('JT_DATEJOURNEETRAVAIL', '')) 
        if row.get('JT_STATUT', ''):
           JT_STATUT  = str(row.get('JT_STATUT', '')) 

        # Préparer les paramètres pour la fonction
        if AG_CODEAGENCE and JT_DATEJOURNEETRAVAIL and JT_STATUT:
            vpp_critere = (AG_CODEAGENCE, JT_DATEJOURNEETRAVAIL,JT_STATUT)
        elif AG_CODEAGENCE and JT_DATEJOURNEETRAVAIL:
            vpp_critere = (AG_CODEAGENCE, JT_DATEJOURNEETRAVAIL)
        elif AG_CODEAGENCE:
            vpp_critere = (AG_CODEAGENCE,)
        else:
            vpp_critere = ()
        
        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = valeur_scalaire_requete_max(db_connexion, *vpp_critere)
                
            if len(response) > 0:
                return jsonify({"SL_MESSAGE": "elements existant !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": "pas d'élement", "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()



@api_bp.route('/valeur_scalaire_requete_count_journee', methods=['POST'])
def pvgValeurScalaireRequeteCount():
    request_data = request.json
    
    for row in request_data['Objet']:
        user_info = {}

        # Validation et récupération des données pour la suppression
       
        AG_CODEAGENCE = None
        JT_STATUT = None
        JT_DATEJOURNEETRAVAIL = None
        if row.get('AG_CODEAGENCE', ''):
           AG_CODEAGENCE = str(row.get('AG_CODEAGENCE', '')) 
        if row.get('JT_STATUT', ''):
           JT_STATUT  = str(row.get('JT_STATUT', '')) 
        if row.get('JT_DATEJOURNEETRAVAIL', ''):
           JT_DATEJOURNEETRAVAIL  = str(row.get('JT_DATEJOURNEETRAVAIL', '')) 

        # Préparer les paramètres pour la fonction
        if AG_CODEAGENCE and JT_STATUT:
            vpp_critere = (AG_CODEAGENCE, JT_STATUT)
        elif AG_CODEAGENCE and JT_DATEJOURNEETRAVAIL:
            vpp_critere = (AG_CODEAGENCE, JT_DATEJOURNEETRAVAIL)
        elif AG_CODEAGENCE:
            vpp_critere = (AG_CODEAGENCE,)
        else:
            vpp_critere = ()
        
        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = valeur_scalaire_requete_count(db_connexion, *vpp_critere)
                
            if len(response) > 0:
                return jsonify({"SL_MESSAGE": "Opérations réalisée avec succès !!!", "SL_RESULTAT": 'TRUE'}, response)
            else:
                return jsonify({"SL_MESSAGE": "pas d'élement", "SL_RESULTAT": 'FALSE'})
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close() 
            
            
            
@api_bp.route('/date_systeme_serveur', methods=['POST'])
def pvgGetDateSystemeServeur():
    request_data = request.json
    
    if request_data:
        user_info = {}

        # Validation et récupération des données pour la suppression
       
        vpp_critere = ()
        
        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = table_libelle_date_systeme_serveur(db_connexion, *vpp_critere)
                
            if len(response) > 0:
                return jsonify({"SL_MESSAGE": "Opérations réalisée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": "pas d'élement", "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            #db_connexion.close()
            
                     
            
@api_bp.route('/ajouter_journee_travail', methods=['POST'])
def pvgInsertJourneeTravail():
        # Récupérer les données du corps de la requête
        request_data = request.json
        journeetravail_infos = []
        if 'Objet' not in request_data:
            return jsonify({"SL_MESSAGE": "Données manquantes.code erreur (300) voir le noeud Objet", "SL_RESULTAT": 'FALSE'})
        
        for row in request_data['Objet']:
            journeetravail_info = {}

            try:
                # Validation des données
                journeetravail_info['AG_CODEAGENCE'] = int(row.get('AG_CODEAGENCE', 0))
                journeetravail_info['JT_DATEJOURNEETRAVAIL'] = parse_datetime(row.get('JT_DATEJOURNEETRAVAIL'))
                journeetravail_info['OP_CODEOPERATEUR'] = int(row.get('OP_CODEOPERATEUR', ''))
                journeetravail_info['JT_STATUT'] = str(row.get('JT_STATUT', ''))
                journeetravail_infos.append(journeetravail_info)
            except ValueError as e:
                # Retourner un message d'erreur en cas de problème de type de données
                return jsonify({"SL_MESSAGE": f"Erreur de type de données : {str(e)}", "SL_RESULTAT": 'FALSE'}), 200
            except Exception as e:
                # Retourner un message d'erreur en cas d'exception générale
                return jsonify({"SL_MESSAGE": f"Erreur inattendue : {str(e)}", "SL_RESULTAT": 'FALSE'}), 200
            
            # Vérification que toutes les données obligatoires sont présentes
            if not all([journeetravail_info['AG_CODEAGENCE'], journeetravail_info['JT_DATEJOURNEETRAVAIL'], 
                        journeetravail_info['OP_CODEOPERATEUR'], journeetravail_info['JT_STATUT'], 
                        ]):
                return jsonify({"SL_MESSAGE": "Données manquantes ou incorrectes.code erreur (301)", "SL_RESULTAT": 'FALSE'}), 200
            
        # Connexion à la base de données
        db_connexion = connect_database()
        db_connexion = db_connexion.cursor()
        db_connexion.execute("BEGIN TRANSACTION")
        
        #try:
        
        for journeetravail_info in journeetravail_infos:
            # Appeler la fonction d'insertion dans la base de données
            insert_journee_travail(db_connexion, journeetravail_info)

        # Valider la transaction
        get_commit(db_connexion,journeetravail_infos)
                
        return jsonify({"SL_MESSAGE": "Insertion réussie!", "SL_RESULTAT": 'TRUE'})



@api_bp.route('/liste_journee_de_travail', methods=['POST'])
def pvgGetJourneeDeTravail():
    request_data = request.json
    
    for row in request_data['Objet']:
        user_info = {}

        # Validation et récupération des données pour la suppression
        AG_CODEAGENCE = None
        JT_DATEJOURNEETRAVAIL = None
        JT_STATUT = None
        if row.get('AG_CODEAGENCE', ''):
           AG_CODEAGENCE = str(row.get('AG_CODEAGENCE', '')) 
        if row.get('JT_DATEJOURNEETRAVAIL', ''):
           JT_DATEJOURNEETRAVAIL = parse_datetime(row.get('JT_DATEJOURNEETRAVAIL', '')) 
        if row.get('JT_STATUT', ''):
           JT_STATUT  = str(row.get('JT_STATUT', '')) 

        # Préparer les paramètres pour la fonction
        if AG_CODEAGENCE and JT_DATEJOURNEETRAVAIL and JT_STATUT:
            vpp_critere = (AG_CODEAGENCE, JT_DATEJOURNEETRAVAIL,JT_STATUT)
        elif AG_CODEAGENCE and JT_DATEJOURNEETRAVAIL:
            vpp_critere = (AG_CODEAGENCE, JT_DATEJOURNEETRAVAIL)
        elif AG_CODEAGENCE and JT_STATUT:
            vpp_critere = (AG_CODEAGENCE, JT_STATUT)
        elif AG_CODEAGENCE:
            vpp_critere = (AG_CODEAGENCE,)
        else:
            vpp_critere = ()
        
        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = liste_journee_travail(db_connexion, *vpp_critere)
                
            if len(response) > 0:
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": 'Aucun élément trouvé', "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            db_connexion.close()



@api_bp.route('/update_journee_travail', methods=['POST'])
def pvgUpdateJourneeTravail():
    request_data = request.json
    user_info = {}
    for row in request_data['Objet']:
        

        # Validation et récupération des données pour la suppression
        AG_CODEAGENCE = str(row.get('AG_CODEAGENCE', '')) 
        JT_DATEJOURNEETRAVAIL = parse_datetime(row.get('JT_DATEJOURNEETRAVAIL', '')) 
        JT_STATUT  = str(row.get('JT_STATUT', '')) 
        
        
        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                update_journee_travail_statut(cursor, AG_CODEAGENCE,JT_DATEJOURNEETRAVAIL,JT_STATUT)
                user_infos = [{
                    'AG_CODEAGENCE':"1000",
                    'JT_STATUT':"O",
                }]
                get_commit(cursor,user_infos)
               
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'})
            
        
        except Exception as e:
            cursor.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la mise a jour : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        #finally:
            cursor.close()
            
# ################################################################
#        GESTION DES JOURNEES DE TRAVAIL                         #
#################################################################



# ################################################################
#           GESTION DE LA COMPTABILITE                      
#################################################################

@api_bp.route('/reedition', methods=['POST'])
def pvgReedition():
    # Récupérer les données du corps de la requête
    request_data = request.json
    
    if 'Objet' not in request_data:
        return jsonify({"SL_MESSAGE": "Données manquantes. Code erreur (300) voir le noeud Objet", "SL_RESULTAT": 'FALSE'})

    for row in request_data['Objet']:
        objet_reedition = {}
        objet_reedition['AG_CODEAGENCE'] = str(row.get('AG_CODEAGENCE', ''))
        objet_reedition['MC_DATEPIECE'] = str(row.get('MC_DATEPIECE', ''))
        objet_reedition['NUMEROBORDEREAU'] = str(row.get('NUMEROBORDEREAU', ''))
        objet_reedition['CONTACT_DESTI'] = str(row.get('CONTACT_DESTI', ''))
        objet_reedition['EMAIL_DESTI'] = str(row.get('EMAIL_DESTI', ''))
        objet_reedition['TYPEOPERATION'] = str(row.get('TYPEOPERATION', ''))
  
    # Connexion à la base de données
    db_connexion = connect_database()
    
    try:
        cursor = db_connexion.cursor()
        cursor.execute("BEGIN TRANSACTION")

        try:
            # Appeler la fonction d'insertion dans la base de données
            response = get_info_comptabilisation(db_connexion, objet_reedition)
            
            # Retourner la réponse au client
            if len(response) > 0:
                ##db_connexion.close()
                return jsonify({"SL_MESSAGE":"Opération éffectuée avec success !", "SL_RESULTAT": 'TRUE'}, response) 
            else:
                ##db_connexion.close()
                return jsonify({"SL_MESSAGE": "Aucun élément trouvé !" ,"SL_RESULTAT": 'FALSE'})
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": f"Erreur lors de l'insertion : {str(e)}", "SL_RESULTAT": 'FALSE'}), 200

    except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
    """ #finally:
        #db_connexion.close() """



@api_bp.route('/operation_de_caisse', methods=['POST'])
def pvgOperationCaisse():
    # Récupérer les données du corps de la requête
    request_data = request.json
    
    if 'Objet' not in request_data:
        return jsonify({"SL_MESSAGE": "Données manquantes. Code erreur (300) voir le noeud Objet", "SL_RESULTAT": 'FALSE'})
  
    for row in request_data['Objet']:
        objet_facture = {}
        objet_facture['AG_CODEAGENCE'] = str(row.get('AG_CODEAGENCE', ''))
        objet_facture['PT_DATESAISIE'] = str(row.get('PT_DATESAISIE', ''))
        objet_facture['OP_CODEOPERATEUR'] = str(row.get('OP_CODEOPERATEUR', ''))
        objet_facture['OP_CODEOPERATION'] = str(row.get('OP_CODEOPERATION', ''))
        
        AG_CODEAGENCE = None
        JT_DATEJOURNEETRAVAIL = None
        OP_CODEOPERATEUR = None
        if request_data['Objet'][0]['clsObjetEnvoi'].get('OE_A', ''):
           AG_CODEAGENCE = str(request_data['Objet'][0]['clsObjetEnvoi'].get('OE_A', '')) 
        if request_data['Objet'][0]['clsObjetEnvoi'].get('OE_J', ''):
           JT_DATEJOURNEETRAVAIL  = str(request_data['Objet'][0]['clsObjetEnvoi'].get('OE_J', ''))
        if request_data['Objet'][0]['clsObjetEnvoi'].get('OE_Y', ''):
           OP_CODEOPERATEUR  = str(request_data['Objet'][0]['clsObjetEnvoi'].get('OE_Y', '')) 

        # Préparer les paramètres pour la fonction
        if AG_CODEAGENCE and JT_DATEJOURNEETRAVAIL and OP_CODEOPERATEUR:
            vpp_critere = (AG_CODEAGENCE, JT_DATEJOURNEETRAVAIL, OP_CODEOPERATEUR)
        elif AG_CODEAGENCE and JT_DATEJOURNEETRAVAIL:
            vpp_critere = (AG_CODEAGENCE, JT_DATEJOURNEETRAVAIL)
        elif AG_CODEAGENCE:
            vpp_critere = (AG_CODEAGENCE,)
        else:
            vpp_critere = ()
        
    # Connexion à la base de données
    db_connexion = connect_database()
    
    try:
        cursor = db_connexion.cursor()
        cursor.execute("BEGIN TRANSACTION")
        
        response = test_journee_fermee(cursor, *vpp_critere)

        if response[0]['NBRE'] == 0:
            return jsonify({"SL_MESSAGE": 'Cette journée a été déjà fermée ou non encore ouverte !' ,"SL_RESULTAT": 'FALSE'})
        
        # Consigner les mouvements
        clsmouvement_infos = []
        for row in request_data['Objet'][0]['TABLEMODEREGLEMENT']:
            objet_mode_reglement = {}
            try:
                objet_mode_reglement['MR_CODEMODEREGLEMENT'] = str(row.get('MR_CODEMODEREGLEMENT', ''))
                objet_mode_reglement['AG_CODEAGENCE'] = str(objet_facture['AG_CODEAGENCE'])
                objet_mode_reglement['MC_DATEPIECE'] = str(objet_facture['PT_DATESAISIE'])
                objet_mode_reglement['MC_NUMPIECE'] = str(row.get('MC_NUMPIECE', ''))
                objet_mode_reglement['MC_NUMSEQUENCE'] = str(row.get('MC_NUMSEQUENCE', ''))
                objet_mode_reglement['OP_CODEOPERATEUR'] = str(objet_facture['OP_CODEOPERATEUR'])
                objet_mode_reglement['MC_MONTANTDEBIT'] = row.get('MC_MONTANTDEBIT', '')
                objet_mode_reglement['MC_MONTANTCREDIT'] = row.get('MC_MONTANTCREDIT', '')
                objet_mode_reglement['MC_DATESAISIE'] = str(objet_facture['PT_DATESAISIE'])
                objet_mode_reglement['MC_ANNULATION'] = str(row.get('MC_ANNULATION', ''))
                objet_mode_reglement['JO_CODEJOURNAL'] = str(row.get('JO_CODEJOURNAL', ''))
                objet_mode_reglement['MC_REFERENCEPIECE'] = str(row.get('MC_REFERENCEPIECE', ''))
                objet_mode_reglement['MC_LIBELLEOPERATION'] = str(row.get('MC_LIBELLEOPERATION', ''))
                objet_mode_reglement['MC_NOMTIERS'] = str(row.get('MC_NOMTIERS', ''))
                objet_mode_reglement['MC_CONTACTTIERS'] = str(row.get('MC_CONTACTTIERS', ''))
                objet_mode_reglement['MC_EMAILTIERS'] = str(row.get('MC_EMAILTIERS', ''))
                objet_mode_reglement['MC_NUMPIECETIERS'] = str(row.get('MC_NUMPIECETIERS', ''))
                objet_mode_reglement['MC_TERMINAL'] = str(row.get('MC_TERMINAL', ''))
                objet_mode_reglement['MC_AUTRE'] = str(row.get('MC_AUTRE', ''))
                objet_mode_reglement['MC_AUTRE1'] = str(row.get('MC_AUTRE1', ''))
                objet_mode_reglement['MC_AUTRE2'] = str(row.get('MC_AUTRE2', ''))
                objet_mode_reglement['MC_AUTRE3'] = str(row.get('MC_AUTRE3', ''))
                objet_mode_reglement['TS_CODETYPESCHEMACOMPTABLE'] = str(row.get('TS_CODETYPESCHEMACOMPTABLE', ''))
                objet_mode_reglement['MC_SENSBILLETAGE'] = str(row.get('MC_SENSBILLETAGE', ''))
                objet_mode_reglement['MC_LIBELLEBANQUE'] = str(row.get('MC_LIBELLEBANQUE', ''))
                objet_mode_reglement['MC_MONTANT_FACTURE'] = row.get('MC_MONTANT_FACTURE', '')
                objet_mode_reglement['OP_CODEOPERATION'] = str(objet_facture['OP_CODEOPERATION'])
                objet_mode_reglement['OP_CODEOPERATEURPASSATIONFOND'] = str(row.get('OP_CODEOPERATEURPASSATIONFOND'))

                clsmouvement_infos.append(objet_mode_reglement) 
            except ValueError as e:
                # Retourner un message d'erreur en cas de problème de type de données
                return jsonify({"SL_MESSAGE": f"Erreur de type de données : {str(e)}", "SL_RESULTAT": 'FALSE'}), 400
            except Exception as e:
                # Retourner un message d'erreur en cas d'exception générale
                return jsonify({"SL_MESSAGE": f"Erreur inattendue : {str(e)}", "SL_RESULTAT": 'FALSE'}), 200

        try:
            # Appeler la fonction d'insertion dans la base de données
            response = pvgComptabilisationOperationsCaisse(cursor, clsmouvement_infos)
                        
            # Retourner la réponse au client
            if response['SL_RESULTAT'] == "TRUE":
                ##cursor.close()
                return jsonify({"NUMEROBORDEREAUREGLEMENT":str(response['NUMEROBORDEREAU']),"MC_LIBELLEOPERATION":str(response['MC_LIBELLEOPERATION']),"SL_MESSAGE":"Comptabilisation éffectuée avec success !" + response['MESSAGEAPI'] ,"SL_RESULTAT": 'TRUE'}) 
            else:
                ##cursor.close()
                return jsonify({"SL_MESSAGE":response['SL_MESSAGE'] ,"SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            cursor.rollback()
            return jsonify({"SL_MESSAGE": f"Erreur lors de l'insertion : {str(e)}", "SL_RESULTAT": 'FALSE'}), 200
    except Exception as e:
            cursor.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
    """ #finally:
        #cursor.close() """
        
# ################################################################
#         GESTION DE LA COMPTABILITE                            #
#################################################################

# ################################################################
#         GESTION GUICHET                                        #
#################################################################



@api_bp.route('/pvgAjouterComptabilisation', methods=['POST'])
def OperationVersementRetrait():
    # Récupérer les données du corps de la requête
    
    request_data = request.json
    # Extraire les données nécessaires pour l'appel à la fonction
    Objet = request_data['Objet']
   # billetages = request_data['Objet']['clsBilletages']
   
    clsEtatmouvementacomptabiliserss = []
    
    
    
    # Boucle sur les éléments de 'Objet'
    for row in request_data['Objet']:
            clsEtatmouvementacomptabilisers = {}

            # Assigner chaque propriété une à une
            clsEtatmouvementacomptabilisers['AG_CODEAGENCE'] = row.get('AG_CODEAGENCE', None)
            clsEtatmouvementacomptabilisers['MC_DATEPIECE'] = row.get('MC_DATEPIECE', None)
            clsEtatmouvementacomptabilisers['MC_NUMPIECE'] = row.get('MC_NUMPIECE', None)
            clsEtatmouvementacomptabilisers['MC_NUMSEQUENCE'] = row.get('MC_NUMSEQUENCE', None)
            clsEtatmouvementacomptabilisers['MR_CODEMODEREGLEMENT'] = row.get('MR_CODEMODEREGLEMENT', None)
            clsEtatmouvementacomptabilisers['PT_IDPATIENT'] = row.get('PT_IDPATIENT', None)
            clsEtatmouvementacomptabilisers['FT_CODEFACTURE'] = row.get('FT_CODEFACTURE', None)
            clsEtatmouvementacomptabilisers['OP_CODEOPERATEUR'] = row.get('OP_CODEOPERATEUR', None)
            clsEtatmouvementacomptabilisers['MC_MONTANTDEBIT'] = row.get('MC_MONTANTDEBIT', None)
            clsEtatmouvementacomptabilisers['MC_MONTANTCREDIT'] = row.get('MC_MONTANTCREDIT', None)
            clsEtatmouvementacomptabilisers['MC_DATESAISIE'] = row.get('MC_DATESAISIE', None)
            clsEtatmouvementacomptabilisers['MC_ANNULATION'] = row.get('MC_ANNULATION', None)
            clsEtatmouvementacomptabilisers['JO_CODEJOURNAL'] = row.get('JO_CODEJOURNAL', None)
            clsEtatmouvementacomptabilisers['MC_REFERENCEPIECE'] = row.get('MC_REFERENCEPIECE', None)
            clsEtatmouvementacomptabilisers['MC_LIBELLEOPERATION'] = row.get('MC_LIBELLEOPERATION', None)
            clsEtatmouvementacomptabilisers['PL_CODENUMCOMPTE'] = row.get('PL_CODENUMCOMPTE', None)
            clsEtatmouvementacomptabilisers['MC_NOMTIERS'] = row.get('MC_NOMTIERS', None)
            clsEtatmouvementacomptabilisers['MC_CONTACTTIERS'] = row.get('MC_CONTACTTIERS', None)
            clsEtatmouvementacomptabilisers['MC_EMAILTIERS'] = row.get('MC_EMAILTIERS', None)
            clsEtatmouvementacomptabilisers['MC_NUMPIECETIERS'] = row.get('MC_NUMPIECETIERS', None)
            clsEtatmouvementacomptabilisers['MC_TERMINAL'] = row.get('MC_TERMINAL', None)
            clsEtatmouvementacomptabilisers['MC_AUTRE'] = row.get('MC_AUTRE', None)
            clsEtatmouvementacomptabilisers['MC_AUTRE1'] = row.get('MC_AUTRE1', None)
            clsEtatmouvementacomptabilisers['MC_AUTRE2'] = row.get('MC_AUTRE2', None)
            clsEtatmouvementacomptabilisers['MC_AUTRE3'] = row.get('MC_AUTRE3', None)
            clsEtatmouvementacomptabilisers['TS_CODETYPESCHEMACOMPTABLE'] = row.get('TS_CODETYPESCHEMACOMPTABLE', None)
            clsEtatmouvementacomptabilisers['MC_SENSBILLETAGE'] = row.get('MC_SENSBILLETAGE', None)
            clsEtatmouvementacomptabilisers['MC_LIBELLEBANQUE'] = row.get('MC_LIBELLEBANQUE', None)
            clsEtatmouvementacomptabilisers['EM_MONTANT'] = row.get('EM_MONTANT', None)

            clsEtatmouvementacomptabiliserss.append(clsEtatmouvementacomptabilisers)
    
    AG_CODEAGENCE = None
    MC_DATESAISIE = None
    OP_CODEOPERATEUR = None
    if clsEtatmouvementacomptabiliserss[0]['OP_CODEOPERATEUR']:
        AG_CODEAGENCE = clsEtatmouvementacomptabiliserss[0]['AG_CODEAGENCE']
    if clsEtatmouvementacomptabiliserss[0]['MC_DATESAISIE']:
        MC_DATESAISIE  = clsEtatmouvementacomptabiliserss[0]['MC_DATESAISIE']
    if clsEtatmouvementacomptabiliserss[0]['OP_CODEOPERATEUR']:
        OP_CODEOPERATEUR  = clsEtatmouvementacomptabiliserss[0]['OP_CODEOPERATEUR']

    # Préparer les paramètres pour la fonction
    if AG_CODEAGENCE and MC_DATESAISIE and OP_CODEOPERATEUR:
        vpp_critere = (AG_CODEAGENCE, MC_DATESAISIE, OP_CODEOPERATEUR)
    elif AG_CODEAGENCE and MC_DATESAISIE:
        vpp_critere = (AG_CODEAGENCE, MC_DATESAISIE)
    elif AG_CODEAGENCE:
        vpp_critere = (AG_CODEAGENCE,)
    else:
        vpp_critere = ()
            
    # Récupérer la connexion à la base de données depuis current_app
   # db_connection = current_app.db_connection
    
   # db_connection.begin()
    #try:
    db_connection = connect_database()
    db_connection = db_connection.cursor()
    db_connection.execute("BEGIN TRANSACTION")
    
    responses = test_journee_fermeeVersement(db_connection, *vpp_critere)

    if responses[0]['NBRE'] == 0:
        return jsonify({"SL_MESSAGE": 'Cette journée a été déjà fermée ou non encore ouverte !' ,"SL_RESULTAT": 'FALSE'})
        
    
        #db_connection.begin()
         # Appeler la fonction avec les données récupérées
    response = pvgComptabilisationVersement(db_connection, clsEtatmouvementacomptabiliserss)
        
        # Retourner la réponse au client
    if response['SL_RESULTAT'] == "TRUE":
        #db_connection.close()
        return jsonify({"NUMEROBORDEREAU":str(response['NUMEROBORDEREAU']),"SL_MESSAGE":"Comptabilisation éffectuée avec success !!! / " + response['MESSAGEAPI'] ,"SL_RESULTAT": 'TRUE'}) 
    else:
        #db_connection.close()
        return jsonify({"SL_MESSAGE":response['SL_MESSAGE'] ,"SL_RESULTAT": 'FALSE'}) 
      




# ################################################################
#         GESTION GUICHET                               #
##################################################################





















def parse_numeric(value):
    """Vérifie si la valeur est un nombre et la convertit. Renvoie une exception si la conversion échoue."""
    if value is None or value == '':
        return None
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Format numérique invalide: {value}")
    
def generer_numero_compte_morale():
    # Générer trois blocs de trois chiffres
    bloc1 = random.randint(100, 999)
    bloc2 = random.randint(100, 999)
    bloc3 = random.randint(100, 999)
    
    # Assembler les blocs avec des tirets
    numero_compte_morale = f"{bloc1}-{bloc2}-{bloc3}"
    
    return numero_compte_morale
    
def get_commit(connexion,clsBilletages):
    try:
       for row in clsBilletages: 
        cursor = connexion
        params = {
            'AG_CODEAGENCE3': '1000',
            'MC_DATEPIECE3': '01/01/1900'
        }
        try:
            connexion.commit()
            cursor.execute("EXECUTE [PC_COMMIT]  ?, ?", list(params.values()))
            #instruction pour valider la commande de mise à jour
            connexion.commit()
        except Exception as e:
            # En cas d'erreur, annuler la transaction
            cursor.execute("ROLLBACK")
            cursor.close()
            MYSQL_REPONSE = e.args[1]
            if "varchar" in MYSQL_REPONSE:
               MYSQL_REPONSE = MYSQL_REPONSE.split("varchar", 1)[1].split("en type de donn", 1)[0]
               
            raise Exception(MYSQL_REPONSE)
    except Exception as e:
        MYSQL_REPONSE = f'Erreur lors du commit des opérations: {str(e)}'
        raise Exception(MYSQL_REPONSE)        


