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
 
            # Ajouter le dictionnaire à la liste des résultats
            results.append(result)
        
        return results
    except Exception as e:
        # En cas d'erreur, lever une exception avec un message approprié
        raise Exception(f"Erreur lors de la récupération des données: {str(e.args[1])}")
    
    
    
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