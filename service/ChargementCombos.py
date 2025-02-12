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


def get_solde_mouvement_comptable(connexion, ag_codeagence, ft_codefacture, op_codeoperateur):
    
    try:
        cursor = connexion.cursor()
        cursor.execute("EXEC PS_RECUPERATIONMONTANTDEJAPAYE ?,?,?",(ag_codeagence,ft_codefacture, op_codeoperateur))
        
        try:
            cursor = connexion.cursor()
            
            # Requête paramétrée
            query = "SELECT * FROM dbo.TEMPRECUPERATIONDEJAPAYERESULTAT{}".format(op_codeoperateur)

            # Exécution de la requête
            cursor.execute(query)

            rows = cursor.fetchone()
            return rows.MONTANTDEJAPAYE
        except Exception as e:
            # En cas d'erreur, lever une exception avec un message approprié
            raise Exception(f"Erreur lors de la récupération des données: {str(e.args[1])}")
    
    except Exception as e:
        connexion.rollback()
        raise Exception(f"Erreur lors de l'insertion: {str(e.args[1])}")



def pvgComboTableLabelAgence(connexion, *vppCritere):
    cursor = connexion.cursor()

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
    
def pvgComboOperateur(connexion, *vppCritere):
    """
    Récupère les opérateurs en fonction des critères fournis.
    - vppCritere[0] : Code agence (obligatoire si présent).
    - vppCritere[1] : Code opérateur (optionnel).
    """
    cursor = connexion.cursor()

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
        connexion.rollback()
        raise Exception(f"Erreur lors de l'exécution de la requête : {str(e)}")

    finally:
        cursor.close()

def pvgComboExercice(connexion, *vppCritere):
    """
    Récupère les opérateurs en fonction des critères fournis.
    - vppCritere[0] : Code agence (obligatoire si présent).
    - vppCritere[1] : Code opérateur (optionnel).
    """
    cursor = connexion.cursor()

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
        connexion.rollback()
        raise Exception(f"Erreur lors de l'exécution de la requête : {str(e)}")

    finally:
        cursor.close()
 

def pvgComboCompte(connexion, *vppCritere):
    """
    Récupère les comptes en fonction des critères fournis.
    - vppCritere[0] : Code société (obligatoire si présent).
    - vppCritere[1] : Numéro de compte (optionnel).
    - vppCritere[2] : Type de compte (optionnel).
    """
    cursor = connexion.cursor()

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


def pvgComboModeReglement(connexion):
    """
    Récupère les opérateurs en fonction des critères fournis.
    - vppCritere[0] : Code agence (obligatoire si présent).
    - vppCritere[1] : Code opérateur (optionnel).
    """
    cursor = connexion.cursor()

    
    
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
        connexion.rollback()
        raise Exception(f"Erreur lors de l'exécution de la requête : {str(e)}")

    finally:
        cursor.close()
        
        
        
def pvgComboPays(connexion):
    
    params = {}
    #return clsSmsouts
    params = {
        'CODECRYPTAGE': CODECRYPTAGE
    }
   
    try:
        cursor = connexion.cursor()
        
        # Exécuter la fonction SQL avec le codecryptage comme paramètre
        cursor.execute("SELECT * FROM dbo.FT_PAYS(?)", list(params.values()))
                       
        rows = cursor.fetchall()
        results = []
        for row in rows:
            result = {}

            result['PY_CODEPAYS'] = row.PY_CODEPAYS
            result['PY_CODEPOSTALE'] = row.PY_CODEPOSTALE
            result['PY_LIBELLE'] = row.PY_LIBELLE
            result['PY_LIBELLENATIONALITE'] = row.PY_LIBELLENATIONALITE
            result['PY_NUMEROORDRE'] = row.PY_NUMEROORDRE
            result['PY_REFERENCE'] = row.PY_REFERENCE
            result['PY_ABREVIATION'] = row.PY_ABREVIATION
 
            # Ajouter le dictionnaire à la liste des résultats
            results.append(result)
        
        return results
    except Exception as e:
        # En cas d'erreur, lever une exception avec un message approprié
        raise Exception(f"Erreur lors de la récupération des données: {str(e.args[1])}")



def pvgComboVille(connexion, ville_info):
    
    params = {}
    #return clsSmsouts
    params = {
        'PY_CODEPAYS': ville_info['PY_CODEPAYS'],
        'CODECRYPTAGE': CODECRYPTAGE
    }
   
    try:
        cursor = connexion.cursor()
        
        # Exécuter la fonction SQL avec le codecryptage comme paramètre
        cursor.execute("SELECT * FROM dbo.FT_VILLE(?,?)", list(params.values()))
                       
        rows = cursor.fetchall()
        results = []
        for row in rows:
            result = {}

            result['VL_CODEVILLE'] = row.VL_CODEVILLE
            result['VL_LIBELLE'] = row.VL_LIBELLE
            result['VL_REFERENCE'] = row.VL_REFERENCE
            result['VL_DESCRIPTION'] = row.VL_DESCRIPTION
            result['PY_CODEPAYS'] = row.PY_CODEPAYS
 
            # Ajouter le dictionnaire à la liste des résultats
            results.append(result)
        
        return results
    except Exception as e:
        # En cas d'erreur, lever une exception avec un message approprié
        raise Exception(f"Erreur lors de la récupération des données: {str(e.args[1])}")



def pvgComboAssure(connexion):
    """
    Récupère les opérateurs en fonction des critères fournis.
    - vppCritere[0] : Code agence (obligatoire si présent).
    - vppCritere[1] : Code opérateur (optionnel).
    """
    cursor = connexion.cursor()


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
        connexion.rollback()
        raise Exception(f"Erreur lors de l'exécution de la requête : {str(e)}")

    finally:
        cursor.close()
 

def pvgComboTypeshemacomptable(connexion):
    """
    Récupère les opérateurs en fonction des critères fournis.
    - vppCritere[0] : Code agence (obligatoire si présent).
    - vppCritere[1] : Code opérateur (optionnel).
    """
    cursor = connexion.cursor()


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
        connexion.rollback()
        raise Exception(f"Erreur lors de l'exécution de la requête : {str(e)}")

    finally:
        cursor.close()       

def pvgComboAssurance(connexion):
    """
    Récupère les opérateurs en fonction des critères fournis.
    - vppCritere[0] : Code agence (obligatoire si présent).
    - vppCritere[1] : Code opérateur (optionnel).
    """
    cursor = connexion.cursor()


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
        connexion.rollback()
        raise Exception(f"Erreur lors de l'exécution de la requête : {str(e)}")

    finally:
        cursor.close()        
        
def pvgComboActe(connexion):
    """
    Récupère les opérateurs en fonction des critères fournis.
    - vppCritere[0] : Code agence (obligatoire si présent).
    - vppCritere[1] : Code opérateur (optionnel).
    """
    cursor = connexion.cursor()


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
        connexion.rollback()
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
        
        

def pvgComboPeriodicite(connexion):
    """
    Récupère les opérateurs en fonction des critères fournis.
    - vppCritere[0] : Code agence (obligatoire si présent).
    - vppCritere[1] : Code opérateur (optionnel).
    """
    cursor = connexion.cursor()

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
        connexion.rollback()
        raise Exception(f"Erreur lors de l'exécution de la requête : {str(e)}")

    finally:
        cursor.close()
        
def pvgComboperiode(connexion, PE_CODEPERIODICITE):
    """
    Récupère les opérateurs en fonction des critères fournis.
    - vppCritere[0] : Code agence (obligatoire si présent).
    - vppCritere[1] : Code opérateur (optionnel).
    """
    cursor = connexion.cursor()
    

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
        connexion.rollback()
        raise Exception(f"Erreur lors de l'exécution de la requête : {str(e)}")

    finally:
        cursor.close()  
        
def pvgPeriodiciteDateDebutFin(connexion, EX_EXERCICE,MO_CODEMOIS,PE_CODEPERIODICITE):
    """
    Récupère les opérateurs en fonction des critères fournis.
    - vppCritere[0] : Code agence (obligatoire si présent).
    - vppCritere[1] : Code opérateur (optionnel).
    """
    cursor = connexion.cursor()
    

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
        connexion.rollback()
        raise Exception(f"Erreur lors de l'exécution de la requête : {str(e)}")

    finally:
        cursor.close()
        
        
        
def liste_des_familles_operations(connexion):
    
    params = {}
    #return clsSmsouts
    params = {
        'CODECRYPTAGE': CODECRYPTAGE
    }
   
    try:
        cursor = connexion.cursor()
        
        # Exécuter la fonction SQL avec le codecryptage comme paramètre
        cursor.execute("SELECT * FROM dbo.FT_FAMILLEOPERATION(?)", list(params.values()))
                       
        rows = cursor.fetchall()
        results = []
        for row in rows:
            result = {}

            result['FO_CODEFAMILLEOPERATION'] = row.FO_CODEFAMILLEOPERATION
            result['FO_LIBELLE'] = row.FO_LIBELLE
            result['FO_STATUT'] = row.FO_STATUT
            result['FO_NUMORDRE'] = row.FO_NUMORDRE
 
            # Ajouter le dictionnaire à la liste des résultats
            results.append(result)
        
        return results
    except Exception as e:
        # En cas d'erreur, lever une exception avec un message approprié
        raise Exception(f"Erreur lors de la récupération des données: {str(e.args[1])}")
    
    
    
def liste_des_operations(connexion, clsOperation):
    
    params = {}
    #return clsSmsouts
    params = {
        'FO_CODEFAMILLEOPERATION': clsOperation['FO_CODEFAMILLEOPERATION'],
        'CODECRYPTAGE': CODECRYPTAGE
    }
   
    try:
        cursor = connexion.cursor()
        
        # Exécuter la fonction SQL avec le codecryptage comme paramètre
        cursor.execute("SELECT * FROM dbo.FT_OPERATION(?,?)", list(params.values()))
                       
        rows = cursor.fetchall()
        results = []
        for row in rows:
            result = {}

            result['OP_CODEOPERATION'] = row.OP_CODEOPERATION
            result['OP_LIBELLE'] = row.OP_LIBELLE
            result['FO_CODEFAMILLEOPERATION'] = row.FO_CODEFAMILLEOPERATION
            result['OP_STATUT'] = row.OP_STATUT
            result['OP_NUMORDRE'] = row.OP_NUMORDRE
            result['TS_CODETYPESCHEMACOMPTABLE'] = row.TS_CODETYPESCHEMACOMPTABLE
            result['JO_CODEJOURNAL'] = row.JO_CODEJOURNAL
            result['PL_CODENUMCOMPTE'] = row.PL_CODENUMCOMPTE
            result['OP_SENS'] = row.OP_SENS
            result['OP_MONTANT'] = row.OP_MONTANT
            result['OP_MODIFICATIONMONTANT'] = row.OP_MODIFICATIONMONTANT
            result['PL_CODENUMCOMPTECONTREPARTIE'] = row.PL_CODENUMCOMPTECONTREPARTIE
 
            # Ajouter le dictionnaire à la liste des résultats
            results.append(result)
        
        return results
    except Exception as e:
        # En cas d'erreur, lever une exception avec un message approprié
        raise Exception(f"Erreur lors de la récupération des données: {str(e.args[1])}")