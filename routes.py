from flask import Blueprint,request, jsonify,current_app,current_app as app,send_file
from service.dashboard import dashboard
from service.FacturePatient import insert_patient, get_id_patient, insert_facture, update_facture, delete_facture, get_facture, list_facture
from service.comptabilisationOperation import pvgComptabilisationOperations
from service.edition import recu_edition, brouillard_caisse_edition, journal_edition, gd_livre_edition, balance_edition
from service.auth import connexion_utilisateur
from service.ChargementCombos import pvgPeriodiciteDateDebutFin,pvgComboCompte,pvgComboTypeshemacomptable,pvgComboAssurance,pvgComboAssure,pvgComboActe,pvgComboModeReglement,pvgComboperiode,pvgComboTableLabelAgence,pvgComboOperateur,pvgComboExercice,pvgComboPeriodicite, pvgComboSexe, pvgComboProfession
from models.models import clsObjetEnvoi
from datetime import datetime
import traceback
from utils import connect_database
from config import MYSQL_REPONSE
import random
import os
from tools.toolCodeFacture import generer_code_facture
from tools.toolDate import parse_datetime
api_bp = Blueprint('api', __name__)



################################################################
#                                                                  GESTION DES FACTURES                                                                  #
################################################################

@api_bp.route('/creation_facture', methods=['POST'])
def pvg_creation_facture():
    # Récupérer les données du corps de la requête
    request_data = request.json
    
    if 'Objet' not in request_data:
        return jsonify({"SL_MESSAGE": "Données manquantes. Code erreur (300) voir le noeud Objet", "SL_RESULTAT": 'FALSE'})

    for row in request_data['Objet']:
        objet_facture = {}
        # objet_facture['PT_CODEPATIENT'] = str(row.get('PT_CODEPATIENT', ''))
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
        objet_facture['ACT_CODEACTE'] = str(row.get('ACT_CODEACTE', ''))
        objet_facture['AS_CODEASSURANCE'] = str(row.get('AS_CODEASSURANCE', ''))
        objet_facture['MC_DATESAISIE'] = str(row.get('PT_DATESAISIE', ''))
        objet_facture['FT_ANNULATION'] = str(row.get('FT_ANNULATION', ''))
        objet_facture['TYPEOPERATION'] = str(row.get('TYPEOPERATION', ''))
        objet_facture['ACT_CODEACTE'] = str(row.get('ACT_CODEACTE', ''))
  
    # Connexion à la base de données
    db_connexion = connect_database()
    
    try:
        # with db_connexion.cursor() as cursor:
        cursor = db_connexion.cursor()
        cursor.execute("BEGIN TRANSACTION")
    
        if objet_facture['TYPEOPERATION'] != '7':
            try:
                # creer le patient
                insert_patient(db_connexion, objet_facture)
            except ValueError as e:
                result = {}

                result['SL_MESSAGE'] = e
                result['SL_RESULTAT'] = "FALSE"
                # Ajouter le dictionnaire à la liste des résultats
                response.append(result)
        
                cursor.execute("ROLLBACK")
                return jsonify(response)
            
            # recuperer lid du patient
            id_patient = get_id_patient(db_connexion, objet_facture['OP_CODEOPERATEUR'])
            objet_facture['PT_IDPATIENT'] = id_patient[0]['PT_IDPATIENT']
        
        # creer la facture du patient
        try:
            # generer le code de la facture
            objet_facture['FT_CODEFACTURE'] = generer_code_facture(objet_facture['AG_CODEAGENCE'])
        except ValueError as e:
            result = {}

            result['SL_MESSAGE'] = e
            result['SL_RESULTAT'] = "FALSE"
            # Ajouter le dictionnaire à la liste des résultats
            response.append(result)
    
            cursor.execute("ROLLBACK")
            return jsonify(response)
        
        # creation de la facture
        insert_facture(db_connexion, objet_facture)
            
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
                objet_mode_reglement['MC_MONTANTDEBIT'] = str(row.get('MC_MONTANTDEBIT', ''))
                objet_mode_reglement['MC_MONTANTCREDIT'] = str(row.get('MC_MONTANTCREDIT', ''))
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
                objet_mode_reglement['MC_MONTANT_FACTURE'] = str(row.get('MC_MONTANT_FACTURE', ''))
                objet_mode_reglement['ACT_CODEACTE'] = str(objet_facture['ACT_CODEACTE'])
                clsmouvement_infos.append(objet_mode_reglement) 
            except ValueError as e:
                # Retourner un message d'erreur en cas de problème de type de données
                return jsonify({"SL_MESSAGE": f"Erreur de type de données : {str(e)}", "SL_RESULTAT": 'FALSE'}), 400
            except Exception as e:
                # Retourner un message d'erreur en cas d'exception générale
                return jsonify({"SL_MESSAGE": f"Erreur inattendue : {str(e)}", "SL_RESULTAT": 'FALSE'}), 500

        try:
            # Appeler la fonction d'insertion dans la base de données
            response = pvgComptabilisationOperations(db_connexion, clsmouvement_infos)
                        
            # Retourner la réponse au client
            if response['SL_RESULTAT'] == "TRUE":
                #db_connexion.close()
                return jsonify({"NUMEROBORDEREAUREGLEMENT":str(response['NUMEROBORDEREAU']),"SL_MESSAGE":"Comptabilisation éffectuée avec success !" + response['MESSAGEAPI'] ,"SL_RESULTAT": 'TRUE'}) 
            else:
                #db_connexion.close()
                return jsonify({"SL_MESSAGE":response['SL_MESSAGE'] ,"SL_RESULTAT": 'FALSE'})
    
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": f"Erreur lors de l'insertion : {str(e)}", "SL_RESULTAT": 'FALSE'}), 500
    except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
    finally:
        db_connexion.close()



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
        
        finally:
            db_connexion.close()
            
            

@api_bp.route('/liste_facture_par_type', methods=['POST'])
def pvgGetFactureParType():
    request_data = request.json
    
    if 'Objet' not in request_data:
        return jsonify({"SL_MESSAGE": "Données manquantes.code erreur (300) voir le noeud Objet", "SL_RESULTAT": 'FALSE'})

    for row in request_data['Objet']:
        clsListeFacture = {}
        # Validation et récupération des données pour la suppression
   
        clsListeFacture['FT_CODEFACTURE'] = row.get('FT_CODEFACTURE')
        clsListeFacture['PT_IDPATIENT'] = row.get('PT_IDPATIENT')
        clsListeFacture['ACT_CODEACTE'] = row.get('ACT_CODEACTE')
        clsListeFacture['AS_CODEASSURANCE'] = row.get('AS_CODEASSURANCE')
        clsListeFacture['MC_DATESAISIE'] = row.get('MC_DATESAISIE')
        clsListeFacture['TYPEOPERATION'] = row.get('TYPEOPERATION')
        
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
                response = list_facture(db_connexion, clsListeFacture)
                
                if response:
                    cursor.execute("COMMIT")
                    return jsonify({"SL_MESSAGE": "Opération effectuée avec succès !!!", "SL_RESULTAT": 'TRUE'}, response)
                else:
                    result = {}
	
                    result['SL_MESSAGE'] = "Facture non trouvée ou autre erreur."
                    result['SL_RESULTAT'] = "FALSE"
                    # Ajouter le dictionnaire à la liste des résultats
                    response.append(result)
            
                    cursor.execute("ROLLBACK")
                    return jsonify(response)
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors du chargement : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        finally:
            db_connexion.close()
            
################################################################
#                                                                  GESTION DES FACTURES                                                                  #
################################################################




################################################################
#                                                                  GESTION DES EDITIONS                                                                  #
################################################################

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
        
        finally:
            db_connexion.close()



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
        broui_caisse_info['DATEDEBUT'] = str(row.get('DATEDEBUT'))
        broui_caisse_info['DATEFIN'] = str(row.get('DATEFIN'))
        broui_caisse_info['TYPEETAT'] = str(row.get('TYPEETAT'))
        broui_caisse_info['OP_CODEOPERATEUREDITION'] = str(row.get('OP_CODEOPERATEUREDITION'))

        # Connexion à la base de données
        db_connexion = connect_database()

        try:
            with db_connexion.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = brouillard_caisse_edition(db_connexion, broui_caisse_info)
            
            if len(response) > 0:
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": "Aucuns élement trouvé !!!", "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors du chargement : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        finally:
            db_connexion.close()



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
        
        finally:
            db_connexion.close()
  
  
  
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
        
        finally:
            db_connexion.close()



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
        
        finally:
            db_connexion.close()
            
################################################################
#                                                                  GESTION DES EDITIONS                                                                  #
################################################################



################################################################
#                                                                      GESTION DASHBOARD                                                                  #
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
        
        finally:
            db_connexion.close()
            
################################################################
#                                                                      GESTION DASHBOARD                                                                  #
################################################################



################################################################
#                                                        GESTION DE L'AUTHENTIFICATION                                                        #
################################################################

#service de connection
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
                db_connexion.commit()
            
            # Retourner la réponse au client
            if len(response) > 0:
                return jsonify({"SL_MESSAGE": "Connexion effectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response[0])
            else:
                return jsonify({"SL_MESSAGE": 'Longin ou mot de passe incorrect', "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connexion.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la connexion : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        finally:
            db_connexion.close()                    

################################################################
#                                                        GESTION DE L'AUTHENTIFICATION                                                        #
################################################################

################################################################
#                    GESTION COMBOS                            #
################################################################
@api_bp.route('/ComboTableLabelAgence', methods=['POST'])
def ComboTableLabelAgence():
    request_data = request.json
    
    for row in request_data['Objet']:
        user_info = {}

        # Validation et récupération des données pour la suppression
        user_info['AG_CODEAGENCE'] = str(row.get('AG_CODEAGENCE', '')) 
        
        # Connexion à la base de données
        db_connection = connect_database()

        try:
            with db_connection.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                if user_info['AG_CODEAGENCE']:  # Si une valeur est fournie
                    response = pvgComboTableLabelAgence(db_connection, str(row.get('AG_CODEAGENCE', '')))
                else:  # Sinon, on appelle sans paramètre
                    response = pvgComboTableLabelAgence(db_connection)
                
                
            if len(response) > 0 :
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": 'Aucun élément trouvé', "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connection.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        finally:
            db_connection.close()            

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
        db_connection = connect_database()

        try:
            with db_connection.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = pvgComboExercice(db_connection, *vpp_critere)
                
                
                
            if len(response) > 0 :
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": 'Aucun élément trouvé', "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connection.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        finally:
            db_connection.close()  
            
            
@api_bp.route('/pvgComboPeriodicite', methods=['POST'])
def ComboPeriodicite():
    request_data = request.json
    
    for row in request_data['Objet']:
        user_info = {}

        
        
        # Connexion à la base de données
        db_connection = connect_database()

        try:
            with db_connection.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = pvgComboPeriodicite(db_connection)
                
                
                
            if len(response) > 0 :
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": 'Aucun élément trouvé', "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connection.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        finally:
            db_connection.close()                        
 
 
@api_bp.route('/pvgComboperiode', methods=['POST'])
def Comboperiode():
    request_data = request.json
    
    for row in request_data['Objet']:
        user_info = {}

        # Validation et récupération des données pour la suppression
       
        PE_CODEPERIODICITE = str(row.get('PE_CODEPERIODICITE', '')) 
        if PE_CODEPERIODICITE is None or PE_CODEPERIODICITE == '':
           return jsonify({"SL_MESSAGE": "Données manquantes. voir PE_CODEPERIODICITE", "SL_RESULTAT": 'FALSE'})


       
        
        # Connexion à la base de données
        db_connection = connect_database()

        try:
            with db_connection.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = pvgComboperiode(db_connection, PE_CODEPERIODICITE)
                
                
                
            if len(response) > 0 :
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": 'Aucun élément trouvé', "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connection.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        finally:
            db_connection.close()   
 
 
 
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
        db_connection = connect_database()

        try:
            with db_connection.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = pvgPeriodiciteDateDebutFin(db_connection, EX_EXERCICE,MO_CODEMOIS,PE_CODEPERIODICITE)
                
                
                
            if len(response) > 0 :
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": 'Aucun élément trouvé', "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connection.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        finally:
            db_connection.close()  
 
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
        db_connection = connect_database()

        try:
            with db_connection.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction 
                response = pvgComboOperateur(db_connection, *vpp_critere)
               
                
                
            if len(response) > 0 :
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": 'Aucun élément trouvé', "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connection.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        finally:
            db_connection.close()            
            
@api_bp.route('/pvgComboModeReglement', methods=['POST'])
def ComboModeReglement():
    request_data = request.json
    
    for row in request_data['Objet']:
        user_info = {}

        
        
        # Connexion à la base de données
        db_connection = connect_database()

        try:
            with db_connection.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = pvgComboModeReglement(db_connection)
                
                
                
            if len(response) > 0 :
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": 'Aucun élément trouvé', "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connection.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        finally:
            db_connection.close()  
            
@api_bp.route('/pvgComboActe', methods=['POST'])
def ComboActe():
    request_data = request.json
    
    for row in request_data['Objet']:
        user_info = {}
        
        # Connexion à la base de données
        db_connection = connect_database()

        try:
            with db_connection.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = pvgComboActe(db_connection)
                
                
                
            if len(response) > 0 :
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": 'Aucun élément trouvé', "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connection.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        finally:
            db_connection.close()   
            
            
            
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
        
        finally:
            db_connexion.close()
            
            
            
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
        
        finally:
            db_connexion.close()



@api_bp.route('/pvgComboAssurance', methods=['POST'])
def ComboAssurance():
    request_data = request.json
    
    for row in request_data['Objet']:
        user_info = {}
        
        # Connexion à la base de données
        db_connection = connect_database()

        try:
            with db_connection.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = pvgComboAssurance(db_connection)
                
                
                
            if len(response) > 0 :
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": 'Aucun élément trouvé', "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connection.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        finally:
            db_connection.close()
@api_bp.route('/pvgComboAssure', methods=['POST'])
def ComboAssure():
    request_data = request.json
    
    for row in request_data['Objet']:
        user_info = {}
        
        # Connexion à la base de données
        db_connection = connect_database()

        try:
            with db_connection.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = pvgComboAssure(db_connection)
                
                
                
            if len(response) > 0 :
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": 'Aucun élément trouvé', "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connection.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        finally:
            db_connection.close()       
 
@api_bp.route('/pvgComboTypeshemacomptable', methods=['POST'])
def ComboTypeshemacomptable():
    request_data = request.json
    
    for row in request_data['Objet']:
        user_info = {}
        
        # Connexion à la base de données
        db_connection = connect_database()

        try:
            with db_connection.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = pvgComboTypeshemacomptable(db_connection)
                
                
            if len(response) > 0 :
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": 'Aucun élément trouvé', "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connection.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        finally:
            db_connection.close()     
   

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
        db_connection = connect_database()

        try:
            with db_connection.cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                
                # Appeler la fonction de suppression
                response = pvgComboCompte(db_connection, *vpp_critere)
                
                
                
            if len(response) > 0 :
                return jsonify({"SL_MESSAGE": "Opération éffectuée avec succès !!!", "SL_RESULTAT": 'TRUE'},response)
            else:
                return jsonify({"SL_MESSAGE": 'Aucun élément trouvé', "SL_RESULTAT": 'FALSE'})
        
        except Exception as e:
            db_connection.rollback()
            return jsonify({"SL_MESSAGE": "Erreur lors de la recuperation : " + str(e), "SL_RESULTAT": 'FALSE'})
        
        finally:
            db_connection.close()                      
################################################################
#                   FIN GESTION COMBOS                         #
################################################################


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
    
def get_commit(connection,clsBilletages):
    try:
       for row in clsBilletages: 
        cursor = connection
        params = {
            'AG_CODEAGENCE3': '1000',
            'MC_DATEPIECE3': '01/01/1900'
        }
        try:
            connection.commit()
            cursor.execute("EXECUTE [PC_COMMIT]  ?, ?", list(params.values()))
            #instruction pour valider la commande de mise à jour
            connection.commit()
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


