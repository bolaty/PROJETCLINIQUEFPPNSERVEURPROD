from flask import Blueprint, request, jsonify
import pyodbc
import datetime
from datetime import datetime
from typing import List
import json
import requests
import socket
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import uuid
#import pyodbc
import sys
sys.path.append("../")
from config import MYSQL_REPONSE,LIENAPISMS,CODECRYPTAGE
import threading
from tools.toolEnvoiSmsEmail import envoi_sms_reedition, envoi_email_reedition



#creation du patient
def insert_patient(connexion, patient_info):
    cursor = connexion
    # Préparation des paramètres
    params = {
        'PT_IDPATIENT': patient_info.get('PT_IDPATIENT') or None,
        'PT_CODEPATIENT': patient_info.get('PT_CODEPATIENT') or None,
        'PT_MATRICULE': patient_info['PT_MATRICULE'],
        'AG_CODEAGENCE': patient_info['AG_CODEAGENCE'],
        'PT_NOMPRENOMS': patient_info['PT_NOMPRENOMS'],
        'PT_CONTACT': patient_info['PT_CONTACT'],
        'PT_EMAIL': patient_info['PT_EMAIL'],
        'PT_DATENAISSANCE': datetime.strptime(patient_info.get('PT_DATENAISSANCE') or '01/01/1900', "%d/%m/%Y"),
        'PT_DATESAISIE': datetime.strptime(patient_info['PT_DATESAISIE'], "%d/%m/%Y"),
        'PT_LIEUHABITATION': patient_info['PT_LIEUHABITATION'],
        'PF_CODEPROFESSION': patient_info.get('PF_CODEPROFESSION') or None,
        'SX_CODESEXE': patient_info['SX_CODESEXE'],
        'STAT_CODESTATUT': patient_info.get('STAT_CODESTATUT') or None,
        'OP_CODEOPERATEUR': patient_info['OP_CODEOPERATEUR'],
        'PL_CODENUMCOMPTE': patient_info.get('PL_CODENUMCOMPTE') or None,
        'CODECRYPTAGE': CODECRYPTAGE,
        'TYPEOPERATION': patient_info['TYPEOPERATION'],  # 0
    }
    
    try:
        try:
            # verifie si le numero de telephone et/ou lemail existe deja. si oui, lever un message d'erreur sinon creer le patient
            cursor.execute("SELECT * FROM dbo.FT_CONTACTEMAILEXIST(?,?,?,?,?,?,?)", (params['AG_CODEAGENCE'], params['PT_CONTACT'], params['PT_EMAIL'], params['PT_CODEPATIENT'], params['PT_MATRICULE'], params['PT_IDPATIENT'], params['CODECRYPTAGE']))
        except Exception as e:
                cursor.rollback()
                raise Exception(f"Erreur lors de l'insertion: {str(e.args[1])}")
            
        # Récupération des résultats
        result = cursor.fetchone()
        if result:
            message = result[0]
            raise Exception(message)
        else:
            try:
                cursor.execute("EXEC dbo.PC_PATIENT ?, ?, ?, ?, ?,?, ?, ?, ?, ?,?, ?, ?, ?, ?,?, ?", list(params.values()))
            except Exception as e:
                cursor.rollback()
                raise Exception(f"Erreur lors de l'insertion: {str(e.args[1])}")
    except Exception as e:
        cursor.rollback()
        # Gérer et formater l'exception correctement
        if len(e.args) == 1:
            raise Exception(f"{e.args[0]}")
        else:
            raise Exception(f"Erreur lors de l'insertion: {e.args[1]}")



# recuperation de lid du patient en cours
def get_id_patient(cursor, _OP_CODEOPERATEUR):
    try:
        # Requête paramétrée
        query = "SELECT * FROM dbo.TEMPRECUPERATIONIDPATIENTRESULTAT{}".format(_OP_CODEOPERATEUR)

        # Exécution de la requête
        cursor.execute(query)

        rows = cursor.fetchall()
        results = []
        for row in rows:
            result = {}
            result['PT_IDPATIENT'] = row.PT_IDPATIENT
            
            # Ajouter le dictionnaire à la liste des résultats
            results.append(result)
        
        return results
    except Exception as e:
        # En cas d'erreur, lever une exception avec un message approprié
        raise Exception(f"Erreur lors de la récupération des données: {str(e.args[1])}")



#creation de la facture
def insert_facture(cursor, facture_info):
    # Préparation des paramètres
    params = {
        'FT_CODEFACTURE': facture_info.get('FT_CODEFACTURE') or None,
        'PT_IDPATIENT': facture_info.get('PT_IDPATIENT') or None,
        'MC_DATESAISIE': datetime.strptime(facture_info['MC_DATESAISIE'], "%d/%m/%Y"),
        'OP_CODEOPERATEUR': facture_info['OP_CODEOPERATEUR'],
        'FT_ANNULATION': facture_info['FT_ANNULATION'],
        'CODECRYPTAGE': CODECRYPTAGE,
        'TYPEOPERATION': 0,
        'AG_CODEAGENCE': facture_info['AG_CODEAGENCE']
    }

    try:
        cursor.execute("EXEC dbo.PC_FACTUREPATIENT ?, ?, ?, ?, ?,?, ?, ?", list(params.values()))
    except Exception as e:
        cursor.rollback()
        raise Exception(f"Erreur lors de l'insertion: {str(e.args[1])}")
    
    
#creation de la facture
def get_code_facture(cursor, _AG_CODEAGENCE, _OP_CODEOPERATEUR):
    # Préparation des paramètres
    params = {
        'AG_CODEAGENCE': _AG_CODEAGENCE,
        'OP_CODEOPERATEUR': _OP_CODEOPERATEUR
    }

    try:
        cursor.execute("EXEC dbo.PS_GENERATIONIDFACTUREPATIENT ?, ?", list(params.values()))
        
        try:
            # Requête paramétrée
            query = "SELECT * FROM dbo.TEMPGENERATIONIDFACTUREPATIENTRESULTAT{}".format(_OP_CODEOPERATEUR)

            # Exécution de la requête
            cursor.execute(query)

            rows = cursor.fetchone()
            return rows.FT_CODEFACTURE
        except Exception as e:
            # En cas d'erreur, lever une exception avec un message approprié
            raise Exception(f"Erreur lors de la récupération des données: {str(e.args[1])}")
    
    except Exception as e:
        cursor.rollback()
        raise Exception(f"Erreur lors de l'insertion: {str(e.args[1])}")



# mofication
def update_facture(connexion, facture_info):
    params = {
        'FT_CODEFACTURE': facture_info['FT_CODEFACTURE'] if 'FT_CODEFACTURE' in facture_info and facture_info['FT_CODEFACTURE'] else None,
        'PT_IDPATIENT': facture_info['PT_IDPATIENT'],
        'MC_DATESAISIE': facture_info['MC_DATESAISIE'],
        'OP_CODEOPERATEUR': facture_info['OP_CODEOPERATEUR'],
        'FT_ANNULATION': facture_info['FT_ANNULATION'],
        'CODECRYPTAGE': CODECRYPTAGE,
        'TYPEOPERATION': 1,
        'AG_CODEAGENCE': facture_info['AG_CODEAGENCE']
    }

    try:
        cursor = connexion.cursor()
        cursor.execute("EXEC dbo.PC_FACTUREPATIENT ?, ?, ?, ?, ?,?, ?, ?", list(params.values()))
        connexion.commit()
        get_commit(connexion,facture_info)
        #cursor.close()
    except Exception as e:
        connexion.rollback()
        raise Exception(f"Erreur lors de la modification: {str(e.args[1])}")

# suppression
def delete_facture(connexion, facture_info):
    params = {
        'FT_CODEFACTURE': facture_info['FT_CODEFACTURE'] if 'FT_CODEFACTURE' in facture_info and facture_info['FT_CODEFACTURE'] else None,
        'PT_IDPATIENT': None,
        'MC_DATESAISIE': parse_datetime('01/01/1900'),
        'OP_CODEOPERATEUR': None,
        'FT_ANNULATION': '',
        'CODECRYPTAGE': CODECRYPTAGE,
        'TYPEOPERATION': 2,
        'AG_CODEAGENCE': facture_info['AG_CODEAGENCE']
    }

    try:
        cursor = connexion.cursor()
        cursor.execute("EXEC dbo.PC_FACTUREPATIENT ?, ?, ?, ?, ?,?, ?, ?", list(params.values()))
        connexion.commit()
        get_commit(connexion,facture_info)
        #cursor.close()
    except Exception as e:
        connexion.rollback()
        raise Exception(f"Erreur lors de la suppression: {str(e.args[1])}")
    
    
    
# liste
def get_facture(connexion):
    """
    Récupère les données de la fonction SQL FT_FACTUREPATIENT avec le code de cryptage fourni.
    
    :param connexion: Connexion à la base de données SQL Server
    :param codecryptage: Le code de cryptage utilisé pour décrypter les données
    :return: Liste de dictionnaires représentant les enregistrements de la table intermédiaire
    """
    
    try:
        cursor = connexion.cursor()
        
        # Exécuter la fonction SQL avec le codecryptage comme paramètre
        cursor.execute("SELECT * FROM dbo.FT_FACTUREPATIENT(?)",(CODECRYPTAGE))

        rows = cursor.fetchall()
        results = []
        for row in rows:
            result = {}

            result['FT_CODEFACTURE'] = row.FT_CODEFACTURE
            result['PT_IDPATIENT'] = row.PT_IDPATIENT
            result['ACT_CODEACTE'] = row.ACT_CODEACTE
            result['AS_CODEASSURANCE'] = row.AS_CODEASSURANCE
            result['MC_DATESAISIE'] = row.MC_DATESAISIE.strftime("%d/%m/%Y")
            result['OP_CODEOPERATEUR'] = row.OP_CODEOPERATEUR
            result['FT_ANNULATION'] = row.FT_ANNULATION
            
            # Ajouter le dictionnaire à la liste des résultats
            results.append(result)
        
        return results
    except Exception as e:
        # En cas d'erreur, lever une exception avec un message approprié
        raise Exception(f"Erreur lors de la récupération des données: {str(e.args[1])}")



# liste selon le type de tiers
def list_facture(connexion, clsListeFacture):
    
    params = {}
    #return clsSmsouts
    params = {
        'AG_CODEAGENCE': clsListeFacture['AG_CODEAGENCE'],
        'FT_CODEFACTURE': clsListeFacture['FT_CODEFACTURE'],
        'PT_IDPATIENT': clsListeFacture['PT_IDPATIENT'],
        'ACT_CODEACTE': clsListeFacture['ACT_CODEACTE'],
        'PT_NOMPRENOMS': clsListeFacture['PT_NOMPRENOMS'],
        'PT_CONTACT': clsListeFacture['PT_CONTACT'],
        'PT_MATRICULE': clsListeFacture['PT_MATRICULE'],
        'PT_CODEPATIENT': clsListeFacture['PT_CODEPATIENT'],
        'AS_CODEASSURANCE': clsListeFacture['AS_CODEASSURANCE'],
        'MC_DATESAISIE1': datetime.strptime(clsListeFacture['MC_DATESAISIE1'], "%d/%m/%Y"),
        'MC_DATESAISIE2': datetime.strptime(clsListeFacture['MC_DATESAISIE2'], "%d/%m/%Y"),
        'CODECRYPTAGE': CODECRYPTAGE,
        'TYPEOPERATION': int(clsListeFacture['TYPEOPERATION']),
        'MONTANT1': int(clsListeFacture.get('MONTANT1') or 0),
        'MONTANT2': int(clsListeFacture.get('MONTANT2') or 0)
    }
   
    try:
        cursor = connexion
        
        # Exécuter la fonction SQL avec le codecryptage comme paramètre
        cursor.execute("SELECT * FROM dbo.FT_FACTUREPATIENTPARTYPE(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", list(params.values()))
                       
        rows = cursor.fetchall()
        results = []
        for row in rows:
            result = {}
	
            result['AG_CODEAGENCE'] = row.AG_CODEAGENCE
            result['FT_CODEFACTURE'] = row.FT_CODEFACTURE
            result['PT_IDPATIENT'] = row.PT_IDPATIENT
            result['ACT_CODEACTE'] = row.ACT_CODEACTE
            result['AS_CODEASSURANCE'] = row.AS_CODEASSURANCE
            result['MC_DATESAISIE'] = row.MC_DATESAISIE.strftime("%d/%m/%Y")
            result['OP_CODEOPERATEUR'] = row.OP_CODEOPERATEUR
            result['FT_ANNULATION'] = row.FT_ANNULATION
            result['PT_NOMPRENOMS'] = row.PT_NOMPRENOMS
            result['PT_CONTACT'] = row.PT_CONTACT
            result['PT_EMAIL'] = row.PT_EMAIL
            result['ACT_LIBELLE'] = row.ACT_LIBELLE
            result['AS_LIBELLE'] = row.AS_LIBELLE
            result['OP_NOMPRENOM'] = row.OP_NOMPRENOM
            result['MONTANT_FACTURE'] = int(row.MONTANT_FACTURE)
            result['SX_CODESEXE'] = row.SX_CODESEXE
            result['PT_DATENAISSANCE'] = row.PT_DATENAISSANCE.strftime("%d/%m/%Y")
            result['PT_LIEUHABITATION'] = row.PT_LIEUHABITATION
            result['PF_CODEPROFESSION'] = row.PF_CODEPROFESSION
            result['PT_MATRICULE'] = row.PT_MATRICULE
            result['STAT_CODESTATUT'] = row.STAT_CODESTATUT
            result['NUMEROBORDEREAU'] = row.NUMEROBORDEREAU
            result['PT_CODEPATIENT'] = row.PT_CODEPATIENT
            result['MR_LIBELLE'] = row.MR_LIBELLE
            # Ajouter le dictionnaire à la liste des résultats
            results.append(result)
        
        return results
    except Exception as e:
        # En cas d'erreur, lever une exception avec un message approprié
        raise Exception(f"Erreur lors de la récupération des données: {str(e.args[1])}")
 


def get_info_comptabilisation(connexion, reedition_info):
    # Préparation des paramètres
    params = {
        'AG_CODEAGENCE': reedition_info['AG_CODEAGENCE'] ,
        'NUMEROBORDEREAU': reedition_info['NUMEROBORDEREAU'],
        'DATEJOURNEE': datetime.strptime(reedition_info['MC_DATEPIECE'], "%d/%m/%Y"),
        'TYPEOPERATION': reedition_info['TYPEOPERATION'],  # 0
        'CODECRYPTAGE': CODECRYPTAGE
    }
    
    try:
        cursor = connexion.cursor()
        
        try:
            cursor = connexion.cursor()
            cursor.execute("EXEC dbo.PS_REEDITION ?, ?, ?, ?, ?", list(params.values()))
            
            rows = cursor.fetchall()
            results = []
            for row in rows:
                result = {}
                result['AG_CODEAGENCE'] = row.AG_CODEAGENCE
                result['MC_DATEPIECE'] = row.MC_DATEPIECE.strftime("%d/%m/%Y")
                result['MC_NUMPIECE'] = row.MC_NUMPIECE
                result['MC_NUMSEQUENCE'] = row.MC_NUMSEQUENCE
                result['MR_CODEMODEREGLEMENT'] = row.MR_CODEMODEREGLEMENT
                result['MR_LIBELLE'] = row.MR_LIBELLE
                result['PT_IDPATIENT'] = row.PT_IDPATIENT
                result['FT_CODEFACTURE'] = row.FT_CODEFACTURE
                result['OP_CODEOPERATEUR'] = row.OP_CODEOPERATEUR
                result['MC_MONTANTDEBIT'] = row.MC_MONTANTDEBIT
                result['MC_MONTANTCREDIT'] = row.MC_MONTANTCREDIT
                result['MC_DATESAISIE'] = row.MC_DATESAISIE.strftime("%d/%m/%Y")
                result['MC_ANNULATION'] = row.MC_ANNULATION
                result['JO_CODEJOURNAL'] = row.JO_CODEJOURNAL
                result['MC_REFERENCEPIECE'] = row.MC_REFERENCEPIECE
                result['MC_LIBELLEOPERATION'] = row.MC_LIBELLEOPERATION
                result['PL_CODENUMCOMPTE'] = row.PL_CODENUMCOMPTE
                result['MC_NOMTIERS'] = row.MC_NOMTIERS
                result['MC_CONTACTTIERS'] = row.MC_CONTACTTIERS
                result['MC_EMAILTIERS'] = row.MC_EMAILTIERS
                result['MC_NUMPIECETIERS'] = row.MC_NUMPIECETIERS
                result['MC_TERMINAL'] = row.MC_TERMINAL
                result['MC_AUTRE'] = row.MC_AUTRE
                result['MC_AUTRE1'] = row.MC_AUTRE1
                result['MC_AUTRE2'] = row.MC_AUTRE2
                result['MC_AUTRE3'] = row.MC_AUTRE3
                result['TS_CODETYPESCHEMACOMPTABLE'] = row.TS_CODETYPESCHEMACOMPTABLE
                result['MC_SENSBILLETAGE'] = row.MC_SENSBILLETAGE
                result['MC_LIBELLEBANQUE'] = row.MC_LIBELLEBANQUE
                result['MC_NUMBORDEREAU'] = row.MC_NUMBORDEREAU
                result['OP_NOMPRENOM'] = row.OP_NOMPRENOM
                result['AG_RAISONSOCIAL'] = row.AG_RAISONSOCIAL
                result['AG_EMAIL'] = row.AG_EMAIL
                result['AG_EMAILMOTDEPASSE'] = row.AG_EMAILMOTDEPASSE
                
                # Ajouter le dictionnaire à la liste des résultats
                results.append(result)
            
            if reedition_info['TYPEOPERATION'] == '0':
                return results
            elif reedition_info['TYPEOPERATION'] == '1':
                # cas d'envoi par sms
                thread_traitement = threading.Thread(target=envoi_sms_reedition, args=(connexion, reedition_info, results))
                thread_traitement.daemon = True
                thread_traitement.start()
                results = [{'MESSAGE': 'Sms envoyé avec succès !'}]
                return results
            else:
                # cas d'envoi par email
                thread_traitement = threading.Thread(target=envoi_email_reedition, args=(connexion, reedition_info, results))
                thread_traitement.daemon = True
                thread_traitement.start()
                results = [{'MESSAGE': 'Email envoyé avec succès !'}]
                return results

        except Exception as e:
            connexion.rollback()
            raise Exception(f"Erreur lors de l'insertion: {str(e.args[1])}")
    except Exception as e:
        connexion.rollback()
        # Gérer et formater l'exception correctement
        if len(e.args) == 1:
            raise Exception(f"{e.args[0]}")
        else:
            raise Exception(f"Erreur lors de l'insertion: {e.args[1]}")
        
        

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
    


def parse_datetime(date_str):
    """Convertit une chaîne de caractères en datetime. Renvoie None si la conversion échoue."""
    if not date_str:
        return None
    
    # Liste des formats possibles
    date_formats = ["%d/%m/%Y","%d-%m-%Y", "%Y-%m-%d %H:%M:%S"]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    # Si aucun format ne correspond, lever une exception
    raise ValueError(f"Format de date invalide: {date_str}")