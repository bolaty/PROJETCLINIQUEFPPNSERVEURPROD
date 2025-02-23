import sys
sys.path.append("../")
from config import CODECRYPTAGE
import datetime
from datetime import datetime
from tools.toolDate import parse_datetime

def pvgComboTypespiece(connexion):
    """
    Récupère les opérateurs en fonction des critères fournis.
    - vppCritere[0] : Code agence (obligatoire si présent).
    - vppCritere[1] : Code opérateur (optionnel).
    """
    cursor = connexion.cursor()


    # Requête SQL
    vapRequete = f"""
        SELECT PI_CODEPIECE,PI_LIBELLEPIECE FROM dbo.PIECEIDENTITE  ORDER BY PI_LIBELLEPIECE
    """
    
    try:
        # Exécution de la requête
        cursor.execute(vapRequete)
        rows = cursor.fetchall()

        # Formatage des résultats
        results = []
        for row in rows:
            result = {
                'PI_CODEPIECE': row[0],
                'PI_LIBELLEPIECE': row[1]
            }
            results.append(result)
        return results

    except Exception as e:
        # Gestion des erreurs
        connexion.rollback()
        raise Exception(f"Erreur lors de l'exécution de la requête : {str(e)}")

def pvgComboTypeshemacomptableVersement(connexion):
    """
    Récupère les opérateurs en fonction des critères fournis.
    - vppCritere[0] : Code agence (obligatoire si présent).
    - vppCritere[1] : Code opérateur (optionnel).
    """
    cursor = connexion.cursor()


    # Requête SQL
    vapRequete = f"""
        SELECT TS_CODETYPESCHEMACOMPTABLE,TS_LIBELLE FROM dbo.TYPESCHEMACOMPTABLE WHERE TS_CODETYPESCHEMACOMPTABLE ='00023' OR TS_CODETYPESCHEMACOMPTABLE ='00024' ORDER BY TS_LIBELLE DESC
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


def pvgChargerDansDataSetSC_SCHEMACOMPTABLECODE(connexion, *vppCritere):
    """
    Récupère les comptes en fonction des critères fournis.
    - vppCritere[0] : Code société (obligatoire si présent).
    - vppCritere[1] : Numéro de compte (optionnel).
    - vppCritere[2] : Type de compte (optionnel).
    """
    cursor = connexion.cursor()

    # Préparation des critères et paramètres
    if len(vppCritere) == 0:
        vap_critere = ""
        vap_valeur_parametre = []

    elif len(vppCritere) == 1:
        vap_critere = " WHERE TS_CODETYPESCHEMACOMPTABLE = ?"
        vap_valeur_parametre = [vppCritere[0]]
   
    else:
        raise ValueError("Nombre de critères non pris en charge.")

    # Requête SQL
    vapRequete = f"""
        SELECT DISTINCT *  FROM dbo.SCHEMACOMPTABLE
        {vap_critere}
        ORDER BY SC_NUMEROORDRE
    """

    try:
        # Exécution de la requête
        cursor.execute(vapRequete, vap_valeur_parametre)
        rows = cursor.fetchall()

        # Formatage des résultats
        results = []
        for row in rows:
            result = {
                'SC_CODESCHEMACOMPTABLE': row[0],
                'SC_SCHEMACOMPTABLECODE': row[1],
                'SC_NUMEROORDRE': row[2],
                'TS_CODETYPESCHEMACOMPTABLE': row[3],
                'JO_CODEJOURNAL': row[4],
                'CD_CODECONDITION': row[5],
                'ML_CODEMONTANTCALCULER': row[6],
                'PL_CODENUMCOMPTE': row[7],
                'SX_CODESEXE': row[8],
                'SC_SENS': row[9],
                'SC_LIBELLE': row[10],
                'SC_COMPTABILISATIONJOURNAL': row[11],
                'SC_MONTANTNUMERIQUE': int(row[12]),
                'SC_BLOCAGECOMPTE': row[13],
                'SC_LIGNECACHEE': row[14],
                'SC_SENSBILLETAGE': row[15],
                'SC_AFFICHER': row[16],
                'SC_CHOIXCOMPTE': row[17]
            }
            results.append(result)
        return results

    except Exception as e:
        # Gestion des erreurs
        raise Exception(f"Erreur lors de l'exécution de la requête : {str(e)}")

    finally:
        cursor.close()