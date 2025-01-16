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
from config import MYSQL_REPONSE,LIENAPISMS
import threading
from config import CODECRYPTAGE

class clsAgence:
    def __init__(self):
        self.SO_CODESOCIETE = ''
        self.AG_AGENCECODE = ''
        self.VL_CODEVILLE = ''
        self.AG_RAISONSOCIAL = ''
        self.AG_CODEAGENCE = ''
        self.AG_BOITEPOSTAL = ''
        self.AG_ADRESSEGEOGRAPHIQUE = ''
        self.AG_TELEPHONE = ''
        self.AG_FAX = ''
        self.AG_EMAIL = ''
        self.AG_NUMEROAGREMENT = ''
        self.AG_REFERENCE = ''
        self.AG_DATECREATION = ''
        self.AG_ACTIF = ''
        self.OP_CODEOPERATEUR = ''
#Liste ...

def pvgComboTableLabelAgence(connection, *vppCritere):
    cursor = connection.cursor()

    if len(vppCritere) >= 1:
        vapCritere = " WHERE AG_CODEAGENCE=? AND AG_ACTIF='O'"
        vapNomParametre = ('@AG_CODEAGENCE',)
        vapValeurParametre = (vppCritere[0],)
    else:
        vapCritere = ""
        vapNomParametre = ()
        vapValeurParametre = ()

    vapRequete = f"""
        SELECT 
            AG_RAISONSOCIAL,
            AG_CODEAGENCE
        FROM AGENCE 
        {vapCritere}
    """
    try:
        cursor.execute(vapRequete, vapValeurParametre)
    except Exception as e:
        cursor.close()
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible d\'exécuter la procédure stockée : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)
    
    try:
        rows = cursor.fetchall()

        clsAgenceObj = clsAgence()
        results = []
        for row in rows:
            result = {}
            result['AG_RAISONSOCIAL'] = row[0]
            result['AG_CODEAGENCE'] = row[1]
            results.append(result)    
        # Retourne l'objet
        return results
    except Exception as e:
        cursor.close()
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible d\'exécuter la procédure stockée : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)
    
def pvgComboOperateur(connection, *vppCritere):
    """
    Récupère les opérateurs en fonction des critères fournis.
    - vppCritere[0] : Code agence (obligatoire si présent).
    - vppCritere[1] : Code opérateur (optionnel).
    """
    cursor = connection.cursor()

    # Préparation des critères et paramètres
    if len(vppCritere) == 0:
        vap_critere = ""
        vap_valeur_parametre = []
    elif len(vppCritere) == 1:
        vap_critere = " WHERE AG_CODEAGENCE=? AND OP_ACTIF='O'"
        vap_valeur_parametre = [vppCritere[0]]
    elif len(vppCritere) == 2:
        vap_critere = " WHERE AG_CODEAGENCE=? AND OP_CODEOPERATEUR=? AND OP_ACTIF='O'"
        vap_valeur_parametre = [vppCritere[0], vppCritere[1]]
    else:
        raise ValueError("Nombre de critères non pris en charge.")

    # Requête SQL
    vapRequete = f"""
        SELECT 
            OP_CODEOPERATEUR,
            AG_CODEAGENCE,
            CAST(DECRYPTBYPASSPHRASE('{CODECRYPTAGE}', OP_NOMPRENOM) AS varchar(550)) AS OP_NOMPRENOM
        FROM OPERATEUR 
        {vap_critere}
    """
    
    try:
        # Exécution de la requête
        cursor.execute(vapRequete, vap_valeur_parametre)
        rows = cursor.fetchall()

        # Formatage des résultats
        results = []
        for row in rows:
            result = {
                'OP_CODEOPERATEUR': row[0],
                'AG_CODEAGENCE': row[1],
                'OP_NOMPRENOM': row[2],
            }
            results.append(result)
        return results

    except Exception as e:
        # Gestion des erreurs
        connection.rollback()
        raise Exception(f"Erreur lors de l'exécution de la requête : {str(e)}")

    finally:
        cursor.close()

def pvgComboExercice(connection, *vppCritere):
    """
    Récupère les opérateurs en fonction des critères fournis.
    - vppCritere[0] : Code agence (obligatoire si présent).
    - vppCritere[1] : Code opérateur (optionnel).
    """
    cursor = connection.cursor()

    # Préparation des critères et paramètres
    if len(vppCritere) == 0:
        vap_critere = ""
        vap_valeur_parametre = []
    elif len(vppCritere) == 1:
        vap_critere = " WHERE AG_CODEAGENCE=? AND EX_ETATEXERCICE='O'"
        vap_valeur_parametre = [vppCritere[0]]
    else:
        raise ValueError("Nombre de critères non pris en charge.")

    # Requête SQL
    vapRequete = f"""
        SELECT 
            EX_EXERCICE,
            EX_DESCEXERCICE,
            AG_CODEAGENCE
        FROM EXERCICE 
        {vap_critere}
    """
    
    try:
        # Exécution de la requête
        cursor.execute(vapRequete, vap_valeur_parametre)
        rows = cursor.fetchall()

        # Formatage des résultats
        results = []
        for row in rows:
            result = {
                'EX_EXERCICE': row[0],
                'EX_DESCEXERCICE': row[1],
                'AG_CODEAGENCE': row[2],
            }
            results.append(result)
        return results

    except Exception as e:
        # Gestion des erreurs
        connection.rollback()
        raise Exception(f"Erreur lors de l'exécution de la requête : {str(e)}")

    finally:
        cursor.close()
 

def pvgComboCompte(connection, *vppCritere):
    """
    Récupère les comptes en fonction des critères fournis.
    - vppCritere[0] : Code société (obligatoire si présent).
    - vppCritere[1] : Numéro de compte (optionnel).
    - vppCritere[2] : Type de compte (optionnel).
    """
    cursor = connection.cursor()

    # Préparation des critères et paramètres
    if len(vppCritere) == 0:
        vap_critere = " WHERE PL_ACTIF='O'"
        vap_valeur_parametre = []

    elif len(vppCritere) == 1:
        vap_critere = " WHERE SO_CODESOCIETE = ? AND PL_ACTIF='O'"
        vap_valeur_parametre = [vppCritere[0]]

    elif len(vppCritere) == 2:
        vap_critere = " WHERE SO_CODESOCIETE = ? AND PL_NUMCOMPTE LIKE ? AND PL_ACTIF='O'"
        vap_valeur_parametre = [vppCritere[0], f"{vppCritere[1]}%"]

    elif len(vppCritere) == 3:
        vap_critere = " WHERE SO_CODESOCIETE = ? AND PL_NUMCOMPTE LIKE ? AND PL_TYPECOMPTE = ? AND PL_ACTIF='O'"
        vap_valeur_parametre = [vppCritere[0], f"{vppCritere[1]}%", vppCritere[2]]

    else:
        raise ValueError("Nombre de critères non pris en charge.")

    # Requête SQL
    vapRequete = f"""
        SELECT PL_CODENUMCOMPTE, PL_NUMCOMPTE, PL_LIBELLE
        FROM PLANCOMPTABLE
        {vap_critere}
        ORDER BY PL_NUMCOMPTE
    """

    try:
        # Exécution de la requête
        cursor.execute(vapRequete, vap_valeur_parametre)
        rows = cursor.fetchall()

        # Formatage des résultats
        results = []
        for row in rows:
            result = {
                'PL_CODENUMCOMPTE': row[0],
                'PL_NUMCOMPTE': row[1],
                'PL_LIBELLE': row[2],
            }
            results.append(result)
        return results

    except Exception as e:
        # Gestion des erreurs
        raise Exception(f"Erreur lors de l'exécution de la requête : {str(e)}")

    finally:
        cursor.close()


def pvgComboModeReglement(connection):
    """
    Récupère les opérateurs en fonction des critères fournis.
    - vppCritere[0] : Code agence (obligatoire si présent).
    - vppCritere[1] : Code opérateur (optionnel).
    """
    cursor = connection.cursor()

    
    
    # Requête SQL
    vapRequete = f"""
        SELECT 
            MR_CODEMODEREGLEMENT,
            MR_LIBELLE
        FROM MODEREGLEMENT 
    """
    
    try:
        # Exécution de la requête
        cursor.execute(vapRequete)
        rows = cursor.fetchall()

        # Formatage des résultats
        results = []
        for row in rows:
            result = {
                'MR_CODEMODEREGLEMENT': row[0],
                'MR_LIBELLE': row[1]
            }
            results.append(result)
        return results

    except Exception as e:
        # Gestion des erreurs
        connection.rollback()
        raise Exception(f"Erreur lors de l'exécution de la requête : {str(e)}")

    finally:
        cursor.close()

def pvgComboAssure(connection):
    """
    Récupère les opérateurs en fonction des critères fournis.
    - vppCritere[0] : Code agence (obligatoire si présent).
    - vppCritere[1] : Code opérateur (optionnel).
    """
    cursor = connection.cursor()


    # Requête SQL
    vapRequete = f"""
        SELECT 
            STAT_CODESTATUT,
            STAT_LIBELLE
        FROM STATUTPATIENT 
    """
    
    try:
        # Exécution de la requête
        cursor.execute(vapRequete)
        rows = cursor.fetchall()

        # Formatage des résultats
        results = []
        for row in rows:
            result = {
                'STAT_CODESTATUT': row[0],
                'STAT_LIBELLE': row[1]
            }
            results.append(result)
        return results

    except Exception as e:
        # Gestion des erreurs
        connection.rollback()
        raise Exception(f"Erreur lors de l'exécution de la requête : {str(e)}")

    finally:
        cursor.close()
 

def pvgComboTypeshemacomptable(connection):
    """
    Récupère les opérateurs en fonction des critères fournis.
    - vppCritere[0] : Code agence (obligatoire si présent).
    - vppCritere[1] : Code opérateur (optionnel).
    """
    cursor = connection.cursor()


    # Requête SQL
    vapRequete = f"""
        SELECT TS_CODETYPESCHEMACOMPTABLE,TS_LIBELLE FROM dbo.TYPESCHEMACOMPTABLE ORDER BY TS_LIBELLE
    """
    
    try:
        # Exécution de la requête
        cursor.execute(vapRequete)
        rows = cursor.fetchall()

        # Formatage des résultats
        results = []
        for row in rows:
            result = {
                'TS_CODETYPESCHEMACOMPTABLE': row[0],
                'TS_LIBELLE': row[1]
            }
            results.append(result)
        return results

    except Exception as e:
        # Gestion des erreurs
        connection.rollback()
        raise Exception(f"Erreur lors de l'exécution de la requête : {str(e)}")

    finally:
        cursor.close()       
def pvgComboAssurance(connection):
    """
    Récupère les opérateurs en fonction des critères fournis.
    - vppCritere[0] : Code agence (obligatoire si présent).
    - vppCritere[1] : Code opérateur (optionnel).
    """
    cursor = connection.cursor()


    # Requête SQL
    vapRequete = f"""
        SELECT 
            AS_CODEASSURANCE,
            AS_LIBELLE
        FROM ASSURANCE 
    """
    
    try:
        # Exécution de la requête
        cursor.execute(vapRequete)
        rows = cursor.fetchall()

        # Formatage des résultats
        results = []
        for row in rows:
            result = {
                'AS_CODEASSURANCE': row[0],
                'AS_LIBELLE': row[1]
            }
            results.append(result)
        return results

    except Exception as e:
        # Gestion des erreurs
        connection.rollback()
        raise Exception(f"Erreur lors de l'exécution de la requête : {str(e)}")

    finally:
        cursor.close()        
        
def pvgComboActe(connection):
    """
    Récupère les opérateurs en fonction des critères fournis.
    - vppCritere[0] : Code agence (obligatoire si présent).
    - vppCritere[1] : Code opérateur (optionnel).
    """
    cursor = connection.cursor()


    # Requête SQL
    vapRequete = f"""
        SELECT 
            ACT_CODEACTE,
            ACT_LIBELLE
        FROM ACTE 
    """
    
    try:
        # Exécution de la requête
        cursor.execute(vapRequete)
        rows = cursor.fetchall()

        # Formatage des résultats
        results = []
        for row in rows:
            result = {
                'ACT_CODEACTE': row[0],
                'ACT_LIBELLE': row[1]
            }
            results.append(result)
        return results

    except Exception as e:
        # Gestion des erreurs
        connection.rollback()
        raise Exception(f"Erreur lors de l'exécution de la requête : {str(e)}")

    finally:
        cursor.close()



def pvgComboSexe(connexion):
    cursor = connexion.cursor()

    # Requête SQL
    query = f"""
        SELECT 
            SX_CODESEXE,
            SX_LIBELLE
        FROM SEXE 
    """
    
    try:
        # Exécution de la requête
        cursor.execute(query)
        rows = cursor.fetchall()

        # Formatage des résultats
        results = []
        for row in rows:
            result = {
                'SX_CODESEXE': row[0],
                'SX_LIBELLE': row[1]
            }
            results.append(result)
        return results
    except Exception as e:
        # Gestion des erreurs
        connexion.rollback()
        raise Exception(f"Erreur lors de l'exécution de la requête : {str(e)}")
    finally:
        cursor.close()
        
        
        
def pvgComboProfession(connexion):
    cursor = connexion.cursor()

    # Requête SQL
    query = f"""
        SELECT 
            PF_CODEPROFESSION,
            PF_LIBELLE
        FROM PROFESSION 
    """
    
    try:
        # Exécution de la requête
        cursor.execute(query)
        rows = cursor.fetchall()

        # Formatage des résultats
        results = []
        for row in rows:
            result = {
                'PF_CODEPROFESSION': row[0],
                'PF_LIBELLE': row[1]
            }
            results.append(result)
        return results
    except Exception as e:
        # Gestion des erreurs
        connexion.rollback()
        raise Exception(f"Erreur lors de l'exécution de la requête : {str(e)}")
    finally:
        cursor.close()
        
        

def pvgComboPeriodicite(connection):
    """
    Récupère les opérateurs en fonction des critères fournis.
    - vppCritere[0] : Code agence (obligatoire si présent).
    - vppCritere[1] : Code opérateur (optionnel).
    """
    cursor = connection.cursor()

    # Préparation des critères et paramètres
    
    vap_critere = "WHERE PE_ACTIF='O'"
    vap_valeur_parametre = []
   

    # Requête SQL
    vapRequete = f"""
        SELECT 
            PE_CODEPERIODICITE,
            PE_LIBELLE
        FROM PERIODICITE 
        {vap_critere}
    """
    
    try:
        # Exécution de la requête
        cursor.execute(vapRequete, vap_valeur_parametre)
        rows = cursor.fetchall()

        # Formatage des résultats
        results = []
        for row in rows:
            result = {
                'PE_CODEPERIODICITE': row[0],
                'PE_LIBELLE': row[1]
            }
            results.append(result)
        return results

    except Exception as e:
        # Gestion des erreurs
        connection.rollback()
        raise Exception(f"Erreur lors de l'exécution de la requête : {str(e)}")

    finally:
        cursor.close()
        
def pvgComboperiode(connection, PE_CODEPERIODICITE):
    """
    Récupère les opérateurs en fonction des critères fournis.
    - vppCritere[0] : Code agence (obligatoire si présent).
    - vppCritere[1] : Code opérateur (optionnel).
    """
    cursor = connection.cursor()
    

    # Requête SQL
    try:
        # Exécution de la requête
        cursor.execute("SELECT * FROM dbo.FC_PERIODICITE(?)",(PE_CODEPERIODICITE))
         
        rows = cursor.fetchall()

        # Formatage des résultats
        results = []
        for row in rows:
            result = {
                'MO_CODEMOIS': row[0],
                'MO_LIBELLE': row[1]
            }
            results.append(result)
        return results

    except Exception as e:
        # Gestion des erreurs
        connection.rollback()
        raise Exception(f"Erreur lors de l'exécution de la requête : {str(e)}")

    finally:
        cursor.close()  
        
def pvgPeriodiciteDateDebutFin(connection, EX_EXERCICE,MO_CODEMOIS,PE_CODEPERIODICITE):
    """
    Récupère les opérateurs en fonction des critères fournis.
    - vppCritere[0] : Code agence (obligatoire si présent).
    - vppCritere[1] : Code opérateur (optionnel).
    """
    cursor = connection.cursor()
    

    # Requête SQL
    try:
        # Exécution de la requête
        cursor.execute("SELECT * FROM dbo.FC_PERIODICITEDATEDEBUTFIN(?,?,?)",(EX_EXERCICE,MO_CODEMOIS,PE_CODEPERIODICITE))
         
        rows = cursor.fetchall()

        # Formatage des résultats
        results = []
        for row in rows:
            result = {
                'MO_DATEDEBUT': row.MO_DATEDEBUT.strftime("%d/%m/%Y") if row.MO_DATEDEBUT else None,
                'MO_DATEFIN': row.MO_DATEFIN.strftime("%d/%m/%Y") if row.MO_DATEFIN else None
            }
            results.append(result)
        return results

    except Exception as e:
        # Gestion des erreurs
        connection.rollback()
        raise Exception(f"Erreur lors de l'exécution de la requête : {str(e)}")

    finally:
        cursor.close()               