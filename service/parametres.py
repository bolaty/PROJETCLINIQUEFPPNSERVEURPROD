from config import MYSQL_REPONSE,LIENAPISMS,CODECRYPTAGE
import datetime
from datetime import datetime




def liste_operateur(connexion, clsListeOperateur):
    
    params = {}
    #return clsSmsouts
    params = {
        'OP_CODEOPERATEUR': clsListeOperateur['OP_CODEOPERATEUR'],
        'AG_CODEAGENCE': clsListeOperateur['AG_CODEAGENCE'],
        'PO_CODEPROFIL': clsListeOperateur['PO_CODEPROFIL'],
        'SR_CODESERVICE': clsListeOperateur['SR_CODESERVICE'],
        'OP_NOMBRECONNEXION': clsListeOperateur['OP_NOMBRECONNEXION'],
        'CODECRYPTAGE': CODECRYPTAGE,
        'TYPEOPERATION': ""
    }
   
    try:
        cursor = connexion.cursor()
        
        # Exécuter la fonction SQL avec le codecryptage comme paramètre
        cursor.execute("SELECT * FROM dbo.FT_OPERATEURPARTYPE(?,?,?,?,?,?,?)", list(params.values()))
                       
        rows = cursor.fetchall()
        results = []
        for row in rows:
            result = {}
	
            result['OP_CODEOPERATEUR'] = row.OP_CODEOPERATEUR
            result['AG_CODEAGENCE'] = row.AG_CODEAGENCE
            result['PO_CODEPROFIL'] = row.PO_CODEPROFIL
            result['PO_LIBELLE'] = row.PO_LIBELLE
            result['SR_CODESERVICE'] = row.SR_CODESERVICE
            result['SR_LIBELLE'] = row.SR_LIBELLE
            result['OP_NOMPRENOM'] = row.OP_NOMPRENOM
            result['OP_TELEPHONE'] = row.OP_TELEPHONE
            result['OP_EMAIL'] = row.OP_EMAIL
            result['OP_LOGIN'] = row.OP_LOGIN
            result['OP_MOTPASSE'] = row.OP_MOTPASSE
            result['OP_URLPHOTO'] = row.OP_URLPHOTO
            result['OP_ACTIF'] = row.OP_ACTIF
            result['PL_CODENUMCOMPTECAISSE'] = row.PL_CODENUMCOMPTECAISSE
            result['PL_CODENUMCOMPTECOFFRE'] = row.PL_CODENUMCOMPTECOFFRE
            result['PL_CODENUMCOMPTEPROVISOIRE'] = row.PL_CODENUMCOMPTEPROVISOIRE
            result['PL_CODENUMCOMPTEWAVE'] = row.PL_CODENUMCOMPTEWAVE
            result['PL_CODENUMCOMPTEMTN'] = row.PL_CODENUMCOMPTEMTN
            result['PL_CODENUMCOMPTEORANGE'] = row.PL_CODENUMCOMPTEORANGE
            result['PL_CODENUMCOMPTEMOOV'] = row.PL_CODENUMCOMPTEMOOV
            result['PL_CODENUMCOMPTECHEQUE'] = row.PL_CODENUMCOMPTECHEQUE
            result['PL_CODENUMCOMPTEVIREMENT'] = row.PL_CODENUMCOMPTEVIREMENT
            result['OP_DATESAISIE'] = row.OP_DATESAISIE.strftime("%d/%m/%Y")
 
            # Ajouter le dictionnaire à la liste des résultats
            results.append(result)
        
        return results
    except Exception as e:
        # En cas d'erreur, lever une exception avec un message approprié
        raise Exception(f"Erreur lors de la récupération des données: {str(e.args[1])}")
    
    
    
def liste_des_agences(connexion):
    
    params = {}
    #return clsSmsouts
    params = {
        'CODECRYPTAGE': CODECRYPTAGE
    }
   
    try:
        cursor = connexion.cursor()
        
        # Exécuter la fonction SQL avec le codecryptage comme paramètre
        cursor.execute("SELECT * FROM dbo.FT_AGENCE(?)", list(params.values()))
                       
        rows = cursor.fetchall()
        results = []
        for row in rows:
            result = {}
	
            result['AG_CODEAGENCE'] = row.AG_CODEAGENCE
            result['SO_CODESOCIETE'] = row.SO_CODESOCIETE
            result['AG_RAISONSOCIAL'] = row.AG_RAISONSOCIAL
            result['AG_DATECREATION'] = row.AG_DATECREATION.strftime("%d/%m/%Y")
            result['AG_NUMEROAGREMENT'] = row.AG_NUMEROAGREMENT
            result['OP_CODEOPERATEUR'] = row.OP_CODEOPERATEUR
            result['AG_BOITEPOSTAL'] = row.AG_BOITEPOSTAL
            result['VL_CODEVILLE'] = row.VL_CODEVILLE
            result['AG_ADRESSEGEOGRAPHIQUE'] = row.AG_ADRESSEGEOGRAPHIQUE
            result['AG_TELEPHONE'] = row.AG_TELEPHONE
            result['AG_EMAIL'] = row.AG_EMAIL
            result['AG_EMAILMOTDEPASSE'] = row.AG_EMAILMOTDEPASSE
            result['AG_EMAILDESTI1'] = row.AG_EMAILDESTI1
            result['AG_EMAILDESTI2'] = row.AG_EMAILDESTI2
            result['AG_EMAILDESTI3'] = row.AG_EMAILDESTI3
            result['AG_EMAILDESTI4'] = row.AG_EMAILDESTI4
            result['AG_EMAILDESTI5'] = row.AG_EMAILDESTI5
            result['AG_TELEPHONEDESTI1'] = row.AG_TELEPHONEDESTI1
            result['AG_TELEPHONEDESTI2'] = row.AG_TELEPHONEDESTI2
            result['AG_TELEPHONEDESTI3'] = row.AG_TELEPHONEDESTI3
            result['AG_TELEPHONEDESTI4'] = row.AG_TELEPHONEDESTI4
            result['AG_TELEPHONEDESTI5'] = row.AG_TELEPHONEDESTI5
 
            # Ajouter le dictionnaire à la liste des résultats
            results.append(result)
        
        return results
    except Exception as e:
        # En cas d'erreur, lever une exception avec un message approprié
        raise Exception(f"Erreur lors de la récupération des données: {str(e.args[1])}")
    
    
    
def modifier_des_agences(connexion, clsAgence, tab_email, tab_contact):
    params = {
        'AG_CODEAGENCE': clsAgence['AG_CODEAGENCE'],
        'SO_CODESOCIETE': clsAgence['SO_CODESOCIETE'],
        'AG_RAISONSOCIAL': clsAgence['AG_RAISONSOCIAL'],
        'AG_DATECREATION': datetime.strptime(clsAgence['AG_DATECREATION'], "%d/%m/%Y"),
        'AG_NUMEROAGREMENT': clsAgence['AG_NUMEROAGREMENT'],
        'OP_CODEOPERATEUR': int(clsAgence['OP_CODEOPERATEUR']),
        'AG_BOITEPOSTAL': clsAgence['AG_BOITEPOSTAL'],
        'VL_CODEVILLE': clsAgence['VL_CODEVILLE'],
        'AG_ADRESSEGEOGRAPHIQUE': clsAgence['AG_ADRESSEGEOGRAPHIQUE'],
        'AG_TELEPHONE': clsAgence['AG_TELEPHONE'],
        'AG_EMAIL': clsAgence['AG_EMAIL'],
        'AG_EMAILMOTDEPASSE': clsAgence['AG_EMAILMOTDEPASSE'],
        'CODECRYPTAGE': CODECRYPTAGE,
        'TYPEOPERATION': int(clsAgence['TYPEOPERATION']),
        'AG_EMAILDESTI1': '',
        'AG_EMAILDESTI2': '',
        'AG_EMAILDESTI3': '',
        'AG_EMAILDESTI4': '',
        'AG_EMAILDESTI5': '',
        'AG_TELEPHONEDESTI1': '',
        'AG_TELEPHONEDESTI2': '',
        'AG_TELEPHONEDESTI3': '',
        'AG_TELEPHONEDESTI4': '',
        'AG_TELEPHONEDESTI5': ''
    }
    
    if tab_email:
        if len(tab_email) == 1:
            params['AG_EMAILDESTI1'] = tab_email[0]
        elif len(tab_email) == 2:
            params['AG_EMAILDESTI1'] = tab_email[0]
            params['AG_EMAILDESTI2'] = tab_email[1]
        elif len(tab_email) == 3:
            params['AG_EMAILDESTI1'] = tab_email[0]
            params['AG_EMAILDESTI2'] = tab_email[1]
            params['AG_EMAILDESTI3'] = tab_email[2]
        elif len(tab_email) == 4:
            params['AG_EMAILDESTI1'] = tab_email[0]
            params['AG_EMAILDESTI2'] = tab_email[1]
            params['AG_EMAILDESTI3'] = tab_email[2]
            params['AG_EMAILDESTI4'] = tab_email[3]
        else:
            params['AG_EMAILDESTI1'] = tab_email[0]
            params['AG_EMAILDESTI2'] = tab_email[1]
            params['AG_EMAILDESTI3'] = tab_email[2]
            params['AG_EMAILDESTI4'] = tab_email[3]
            params['AG_EMAILDESTI5'] = tab_email[4]
    
    if tab_contact:
        if len(tab_contact) == 1:
            params['AG_TELEPHONEDESTI1'] = tab_contact[0]
        elif len(tab_contact) == 2:
            params['AG_TELEPHONEDESTI1'] = tab_contact[0]
            params['AG_TELEPHONEDESTI2'] = tab_contact[1]
        elif len(tab_contact) == 3:
            params['AG_TELEPHONEDESTI1'] = tab_contact[0]
            params['AG_TELEPHONEDESTI2'] = tab_contact[1]
            params['AG_TELEPHONEDESTI3'] = tab_contact[2]
        elif len(tab_contact) == 4:
            params['AG_TELEPHONEDESTI1'] = tab_contact[0]
            params['AG_TELEPHONEDESTI2'] = tab_contact[1]
            params['AG_TELEPHONEDESTI3'] = tab_contact[2]
            params['AG_TELEPHONEDESTI4'] = tab_contact[3]
        else:
            params['AG_TELEPHONEDESTI1'] = tab_contact[0]
            params['AG_TELEPHONEDESTI2'] = tab_contact[1]
            params['AG_TELEPHONEDESTI3'] = tab_contact[2]
            params['AG_TELEPHONEDESTI4'] = tab_contact[3]
            params['AG_TELEPHONEDESTI5'] = tab_contact[4]
        
    try:
        cursor = connexion
        
        # Exécuter la fonction SQL avec le codecryptage comme paramètre
        cursor.execute("EXEC dbo.PC_AGENCE ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?", list(params.values()))
    except Exception as e:
        connexion.rollback()
        raise Exception(f"Erreur lors de l'insertion: {str(e.args[1])}")
    
    
    
def liste_des_profils(connexion):
    
    params = {}
    #return clsSmsouts
    params = {
        'CODECRYPTAGE': CODECRYPTAGE
    }
   
    try:
        cursor = connexion.cursor()
        
        # Exécuter la fonction SQL avec le codecryptage comme paramètre
        cursor.execute("SELECT * FROM dbo.FT_PROFIL(?)", list(params.values()))
                       
        rows = cursor.fetchall()
        results = []
        for row in rows:
            result = {}
	
            result['PO_CODEPROFIL'] = row.PO_CODEPROFIL
            result['PO_LIBELLE'] = row.PO_LIBELLE
 
            # Ajouter le dictionnaire à la liste des résultats
            results.append(result)
        
        return results
    except Exception as e:
        # En cas d'erreur, lever une exception avec un message approprié
        raise Exception(f"Erreur lors de la récupération des données: {str(e.args[1])}")
    
    

def liste_des_services(connexion):
    
    params = {}
    #return clsSmsouts
    params = {
        'CODECRYPTAGE': CODECRYPTAGE
    }
   
    try:
        cursor = connexion.cursor()
        
        # Exécuter la fonction SQL avec le codecryptage comme paramètre
        cursor.execute("SELECT * FROM dbo.FT_SERVICE(?)", list(params.values()))
                       
        rows = cursor.fetchall()
        results = []
        for row in rows:
            result = {}
	
            result['SR_CODESERVICE'] = row.SR_CODESERVICE
            result['SR_LIBELLE'] = row.SR_LIBELLE
 
            # Ajouter le dictionnaire à la liste des résultats
            results.append(result)
        
        return results
    except Exception as e:
        # En cas d'erreur, lever une exception avec un message approprié
        raise Exception(f"Erreur lors de la récupération des données: {str(e.args[1])}")
    
    
    
def liste_des_parametres(connexion):
    
    params = {}
    #return clsSmsouts
    params = {
        'CODECRYPTAGE': CODECRYPTAGE
    }
   
    try:
        cursor = connexion.cursor()
        
        # Exécuter la fonction SQL avec le codecryptage comme paramètre
        cursor.execute("SELECT * FROM dbo.FT_PARAMETRE(?)", list(params.values()))
                       
        rows = cursor.fetchall()
        results = []
        for row in rows:
            result = {}

            result['PP_CODEPARAMETRE'] = row.PP_CODEPARAMETRE
            result['SO_CODESOCIETE'] = row.SO_CODESOCIETE
            result['PP_LIBELLE'] = row.PP_LIBELLE
            result['PP_MONTANTMINI'] = row.PP_MONTANTMINI
            result['PP_MONTANTMAXI'] = row.PP_MONTANTMAXI
            result['PP_TAUX'] = row.PP_TAUX
            result['PP_MONTANT'] = row.PP_MONTANT
            result['PP_VALEUR'] = row.PP_VALEUR
            result['PL_CODENUMCOMPTE'] = row.PL_CODENUMCOMPTE
            result['PP_AFFICHER'] = row.PP_AFFICHER
 
            # Ajouter le dictionnaire à la liste des résultats
            results.append(result)
        
        return results
    except Exception as e:
        # En cas d'erreur, lever une exception avec un message approprié
        raise Exception(f"Erreur lors de la récupération des données: {str(e.args[1])}")