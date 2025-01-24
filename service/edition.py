import sys
sys.path.append("../")
from config import CODECRYPTAGE
import datetime
from datetime import datetime
from tools.toolDate import parse_datetime



# recu de caisse
def recu_edition(connexion,AG_CODEAGENCE,MC_DATEPIECE,NUMEROBORDEREAU):
    """
    Récupère les données de la fonction SQL [PS_EDITION_RECU] avec le code de cryptage fourni.
    @AG_CODEAGENCE as varchar(50),
    @CODECRYPTAGE as varchar(50)
    :param connexion: Connexion à la base de données SQL Server
    :param codecryptage: Le code de cryptage utilisé pour décrypter les données
    :return: Liste de dictionnaires représentant les enregistrements de la table intermédiaire
    """
    
    try:
        cursor = connexion.cursor()
        
        # Exécuter la fonction SQL avec le codecryptage comme paramètre
        cursor.execute("SELECT * FROM FT_EDITION_RECU(?,?,?,?)",(AG_CODEAGENCE,datetime.strptime(MC_DATEPIECE, "%d/%m/%Y"),NUMEROBORDEREAU,CODECRYPTAGE))
                       
        rows = cursor.fetchall()
        results = []
        for row in rows:
            result = {}
            result['AG_CODEAGENCE'] = row.AG_CODEAGENCE
            result['MC_NUMPIECE'] = row.MC_NUMPIECE
            result['MC_DATEPIECE'] = row.MC_DATEPIECE.strftime("%d/%m/%Y")  # Formatage de la date
            result['NUMEROBORDEREAU'] = row.NUMEROBORDEREAU
            result['MC_NUMSEQUENCE'] = row.MC_NUMSEQUENCE
            result['MR_CODEMODEREGLEMENT'] = row.MR_CODEMODEREGLEMENT
            result['JO_CODEJOURNAL'] = row.JO_CODEJOURNAL
            result['PL_CODENUMCOMPTE'] = row.PL_CODENUMCOMPTE
            result['PL_NUMCOMPTE'] = row.PL_NUMCOMPTE
            result['MC_REFERENCEPIECE'] = row.MC_REFERENCEPIECE
            result['MC_REFERENCEPIECEORIGINAL'] = row.MC_REFERENCEPIECEORIGINAL
            result['MC_LIBELLEOPERATION'] = row.MC_LIBELLEOPERATION
            result['OP_CODEOPERATEUR'] = row.OP_CODEOPERATEUR
            result['MC_NOMTIERS'] = row.MC_NOMTIERS
            result['TS_CODETYPESCHEMACOMPTABLE'] = row.TS_CODETYPESCHEMACOMPTABLE
            result['MC_MONTANTDEBIT'] = int(row.MC_MONTANTDEBIT)
            result['MC_MONTANTCREDIT'] = int(row.MC_MONTANTCREDIT)
            result['MC_DATESAISIE'] = row.MC_DATESAISIE.strftime("%d/%m/%Y") if row.MC_DATESAISIE else None
            result['MC_ANNULATION'] = row.MC_ANNULATION
            result['CO_INTITULECOMPTERECU'] = row.CO_INTITULECOMPTERECU
            result['PI_CODEPIECE'] = row.PI_CODEPIECE
            result['PI_LIBELLEPIECE'] = row.PI_LIBELLEPIECE
            result['MC_NUMPIECETIERS'] = row.MC_NUMPIECETIERS
            result['SO_SLOGAN'] = row.SO_SLOGAN
            result['MC_SENSBILLETAGE'] = row.MC_SENSBILLETAGE
            result['MC_CONTACTTIERS'] = row.MC_CONTACTTIERS
            result['AG_RAISONSOCIAL'] = row.AG_RAISONSOCIAL
            result['FT_CODEFACTURE'] = row.FT_CODEFACTURE
            result['FT_MONTANTFACTURE'] = row.FT_MONTANTFACTURE
            
            # Ajouter le dictionnaire à la liste des résultats
            results.append(result)
        
        
        return results
    except Exception as e:
        # En cas d'erreur, lever une exception avec un message approprié
        raise Exception(f"Erreur lors de la récupération des données: {str(e.args[1])}")



# brouillard de caisse
def brouillard_caisse_edition(connection, broui_caisse_info):
    """
    Récupère les données de la procédure SQL [PS_ETATMOUVEMENTCOMPTABLE].
    
    :param connection: Connexion à la base de données SQL Server
    :param AG_CODEAGENCE: Nature du compte (varchar)
    :param DATEDEBUT: Indicateur actif (varchar)
    :param DATEFIN: Type d'écran (varchar)
    :param CU_CODECOMPTEUTULISATEURAGENT: Type d'écran (varchar)
    :param CODECRYPTAGE: Type d'écran (varchar)
    :return: Liste de dictionnaires représentant les enregistrements de la table
    """
    try:
        cursor = connection.cursor()
        
        DATEDEBUT = parse_datetime(broui_caisse_info['DATEDEBUT'])
        DATEFIN = parse_datetime(broui_caisse_info['DATEFIN'])
        
        # Préparation des paramètres
        params = {
            'AG_CODEAGENCE': broui_caisse_info['AG_CODEAGENCE'],
            'OP_CODEOPERATEUR': broui_caisse_info['OP_CODEOPERATEUR'],
            'DATEDEBUT': DATEDEBUT,
            'DATEFIN': DATEFIN,
            'CODECRYPTAGE': CODECRYPTAGE,
            'TYPEETAT': broui_caisse_info['TYPEETAT'],
            'OP_CODEOPERATEUREDITION': broui_caisse_info['OP_CODEOPERATEUREDITION']
        }
    
        # Exécuter la procédure stockée avec le bon schéma (assure-toi que 'dbo' est le bon schéma)
        cursor.execute("EXEC dbo.PS_ETATBROUILLARDCAISSE ?,?,?,?,?,?,?", list(params.values()))
        
        # Passer aux résultats (au cas où la procédure exécute plusieurs commandes)
        #cursor.nextset()
        # Récupérer les résultats
        rows = cursor.fetchall()
        results = []
        total_debit = 0  # Initialisation du total des débits
        total_credit = 0  # Initialisation du total des crédits
        solde = 0
        if len(rows) > 0  :
            solde = rows[0].SOLDEPRECEDENTOPERATION  # Initialisation du total des crédits
            solde = solde if solde is not None else 0
            solde = parse_numeric(solde)  # Initialisation du total des crédits
        # Parcourir les lignes et les convertir en dictionnaires
        for row in rows:
            
            # Ajout des montants au total
            total_debit += row.MC_MONTANTDEBIT if row.MC_MONTANTDEBIT is not None else 0
            total_credit += row.MC_MONTANTCREDIT if row.MC_MONTANTCREDIT is not None else 0
            
            solde += int(row.MC_MONTANTDEBIT) - int(row.MC_MONTANTCREDIT)
            
            result = {
                'AG_CODEAGENCE': row.AG_CODEAGENCE,
                'AG_RAISONSOCIAL': row.AG_RAISONSOCIAL,
                'MC_DATEPIECE': row.MC_DATEPIECE.strftime("%d/%m/%Y") if row.MC_DATEPIECE else None,
                'MC_REFERENCEPIECE': row.MC_REFERENCEPIECE,
                'MC_LIBELLEOPERATION': row.MC_LIBELLEOPERATION,
                'MC_MONTANTDEBIT': int(row.MC_MONTANTDEBIT),
                'MC_MONTANTCREDIT': int(row.MC_MONTANTCREDIT),
                'PT_CODEPATIENT': row.PT_CODEPATIENT,
                'PT_NOMPRENOMS': row.PT_NOMPRENOMS,
                'AS_CODEASSURANCE': row.AS_CODEASSURANCE,
                'AS_LIBELLE': row.AS_LIBELLE,
                'OP_CODEOPERATEUR': row.OP_CODEOPERATEUR,
                'OP_NOMPRENOM': row.OP_NOMPRENOM,
                'MR_CODEMODEREGLEMENT': row.MR_CODEMODEREGLEMENT,
                'MR_LIBELLE': row.MR_LIBELLE,
                'ACT_CODEACTE': row.ACT_CODEACTE,
                'ACT_LIBELLE': row.ACT_LIBELLE,
                'NUMBORDEREAU': row.NUMBORDEREAU,
                'MC_NUMPIECE': row.MC_NUMPIECE,
                'MC_NUMSEQUENCE': row.MC_NUMSEQUENCE,
                'PL_CODENUMCOMPTE': row.PL_CODENUMCOMPTE,
                'PL_NUMCOMPTE': row.PL_NUMCOMPTE,
                'MONTANT_TOTAL_ESPECE': int(row.MONTANT_TOTAL_ESPECE),
                'MONTANT_TOTAL_OM': int(row.MONTANT_TOTAL_OM),
                'MONTANT_TOTAL_MOMO': int(row.MONTANT_TOTAL_MOMO),
                'MONTANT_TOTAL_FLOOZ': int(row.MONTANT_TOTAL_FLOOZ),
                'MONTANT_TOTAL_WAVE': int(row.MONTANT_TOTAL_WAVE),
                'MONTANT_TOTAL_CHEQUE': int(row.MONTANT_TOTAL_CHEQUE),
                'MONTANT_TOTAL_VIREMENT': int(row.MONTANT_TOTAL_VIREMENT),
                'CU_SOLDE': int(solde),
                'SOLDEPRECEDENTOPERATION':  int(row.SOLDEPRECEDENTOPERATION) if row.SOLDEPRECEDENTOPERATION is not None else 0,
                
               
            }
            
            results.append(result)
            
        return results
    
    except Exception as e:
        # Gérer les exceptions et retourner un message d'erreur approprié
        raise Exception(f"Erreur lors de la récupération des données: {str(e)}")

# journal
def journal_edition(connexion, journal_info):
    
     # Préparation des paramètres
    params = {
        'AG_CODEAGENCE': journal_info['AG_CODEAGENCE'],
        'OP_CODEOPERATEUR': journal_info['OP_CODEOPERATEUR'] or None,
        'DATEDEBUT': datetime.strptime(journal_info['DATEDEBUT'], "%d/%m/%Y"),
        'DATEFIN': datetime.strptime(journal_info['DATEFIN'], "%d/%m/%Y"),
        'CODECRYPTAGE': CODECRYPTAGE,
        'TYPEETAT': journal_info['TYPEETAT'],
        'OP_CODEOPERATEUREDITION': journal_info['OP_CODEOPERATEUREDITION'],
        'MR_CODEMODEREGLEMENT': journal_info['MR_CODEMODEREGLEMENT'],
        'ACT_CODEACTE': journal_info['ACT_CODEACTE'],
        'STAT_CODESTATUT': journal_info['STAT_CODESTATUT'],
        'AS_CODEASSURANCE': journal_info['AS_CODEASSURANCE'],
        'MONTANTDEBUT': journal_info['MONTANTDEBUT'],
        'MONTANTFIN': journal_info['MONTANTFIN'],
        'NUMBORDEREAU': journal_info['NUMBORDEREAU']
    }
    
    try:
        cursor = connexion.cursor()
        
        # Exécuter la fonction SQL avec le codecryptage comme paramètre
        cursor.execute("EXEC PS_ETATJOURNAL ?,?,?,?,?,?,?,?,?,?,?,?,?,?", list(params.values()))
        
        rows = cursor.fetchall()
        results = []
        for row in rows:
            result = {}
            
            result['AG_CODEAGENCE'] = row.AG_CODEAGENCE
            result['AG_RAISONSOCIAL'] = row.AG_RAISONSOCIAL
            result['MC_DATEPIECE'] = row.MC_DATEPIECE.strftime("%d/%m/%Y")  # Formatage de la date
            result['MC_REFERENCEPIECE'] = row.MC_REFERENCEPIECE
            result['MC_LIBELLEOPERATION'] = row.MC_LIBELLEOPERATION
            result['MC_MONTANTDEBIT'] = int(row.MC_MONTANTDEBIT)
            result['MC_MONTANTCREDIT'] = int(row.MC_MONTANTCREDIT)
            result['PT_NOMPRENOMS'] = row.PT_NOMPRENOMS
            result['OP_CODEOPERATEUR'] = row.OP_CODEOPERATEUR
            result['OP_NOMPRENOM'] = row.OP_NOMPRENOM
            result['NUMBORDEREAU'] = row.NUMBORDEREAU
            result['PL_CODENUMCOMPTE'] = row.PL_CODENUMCOMPTE
            result['PL_NUMCOMPTE'] = row.PL_NUMCOMPTE
            result['PT_CONTACT'] = row.PT_CONTACT
            result['PT_CODEPATIENT'] = row.PT_CODEPATIENT
            result['MC_NUMPIECE'] = row.MC_NUMPIECE
            result['MC_NUMSEQUENCE'] = row.MC_NUMSEQUENCE
  
            # Ajouter le dictionnaire à la liste des résultats
            results.append(result)
        
        return results
    except Exception as e:
        # En cas d'erreur, lever une exception avec un message approprié
        raise Exception(f"Erreur lors de la récupération des données: {str(e.args[1])}")
    
    
# grand livre
def gd_livre_edition(connexion, gd_livre_info):
    
     # Préparation des paramètres
    params = {
        'AG_CODEAGENCE': gd_livre_info['AG_CODEAGENCE'],
        'OP_CODEOPERATEUR': gd_livre_info['OP_CODEOPERATEUR'] or None, 
        'DATEDEBUT': datetime.strptime(gd_livre_info['DATEDEBUT'], "%d/%m/%Y"),
        'DATEFIN': datetime.strptime(gd_livre_info['DATEFIN'], "%d/%m/%Y"),
        'CODECRYPTAGE': CODECRYPTAGE,
        'TYPEETAT': gd_livre_info['TYPEETAT'],
        'OP_CODEOPERATEUREDITION': gd_livre_info['OP_CODEOPERATEUREDITION'],
		
        'NUMCOMPTEDEBUT': gd_livre_info['NUMCOMPTEDEBUT'],
        'NUMCOMPTEFIN': gd_livre_info['NUMCOMPTEFIN']
    }
    
    try:
        cursor = connexion.cursor()
        
        # Exécuter la fonction SQL avec le codecryptage comme paramètre
        cursor.execute("EXEC PS_ETATGRANDLIVRE ?,?,?,?,?,?,?,?,?", list(params.values()))
        
        rows = cursor.fetchall()
        results = []
        total_debit = 0  # Initialisation du total des débits
        total_credit = 0  # Initialisation du total des crédits
        solde = 0
        if len(rows) > 0  :
            solde = rows[0].SOLEPRECEDENT  # Initialisation du total des crédits
            solde = solde if solde is not None else 0
            solde = parse_numeric(solde)  # Initialisation du total des crédits
        for row in rows:
            result = {}
            # Ajout des montants au total
            total_debit += row.MC_MONTANTDEBIT if row.MC_MONTANTDEBIT is not None else 0
            total_credit += row.MC_MONTANTCREDIT if row.MC_MONTANTCREDIT is not None else 0
            
            solde += int(row.MC_MONTANTDEBIT) - int(row.MC_MONTANTCREDIT)
            result = {
            'AG_CODEAGENCE': row.AG_CODEAGENCE,
            'AG_RAISONSOCIAL': row.AG_RAISONSOCIAL,
            'MC_DATEPIECE': row.MC_DATEPIECE.strftime("%d/%m/%Y"),  # Formatage de la date
            'MC_REFERENCEPIECE' :row.MC_REFERENCEPIECE,
            'MC_LIBELLEOPERATION': row.MC_LIBELLEOPERATION,
            'MC_MONTANTDEBIT': int(row.MC_MONTANTDEBIT),
            'MC_MONTANTCREDIT' :int(row.MC_MONTANTCREDIT),
            'OP_CODEOPERATEUR': row.OP_CODEOPERATEUR,
            'OP_NOMPRENOM': row.OP_NOMPRENOM,
            'NUMBORDEREAU': row.NUMBORDEREAU,
            'PL_CODENUMCOMPTE': row.PL_CODENUMCOMPTE,
            'PL_NUMCOMPTE': row.PL_NUMCOMPTE,
            'PL_LIBELLE': row.PL_LIBELLE,
            'PT_CODEPATIENT': row.PT_CODEPATIENT,
            'JO_CODEJOURNAL': row.JO_CODEJOURNAL,
            'MC_NUMPIECE': row.MC_NUMPIECE,
            'MC_NUMSEQUENCE': row.MC_NUMSEQUENCE,
            'SOLDE': solde,
            'SOLEPRECEDENT': row.SOLEPRECEDENT
            }
            # Ajouter le dictionnaire à la liste des résultats
            results.append(result)
        
        return results
    except Exception as e:
        # En cas d'erreur, lever une exception avec un message approprié
        raise Exception(f"Erreur lors de la récupération des données: {str(e.args[1])}")



# balance
def balance_edition(connexion, balance_info):
    
     # Préparation des paramètres
    params = {
        'AG_CODEAGENCE': balance_info['AG_CODEAGENCE'],
        'OP_CODEOPERATEUR': balance_info['OP_CODEOPERATEUR'] if 'OP_CODEOPERATEUR' in balance_info else None,
        'DATEDEBUT': datetime.strptime(balance_info['DATEDEBUT'], "%d/%m/%Y"),
        'DATEFIN': datetime.strptime(balance_info['DATEFIN'], "%d/%m/%Y"),
        'CODECRYPTAGE': CODECRYPTAGE,
        'TYPEETAT': balance_info['TYPEETAT'],
        'OP_CODEOPERATEUREDITION': balance_info['OP_CODEOPERATEUREDITION'],
		
        'PL_OPTION': balance_info['PL_OPTION']
    }
    
    try:
        cursor = connexion.cursor()
        
        # Exécuter la fonction SQL avec le codecryptage comme paramètre
        cursor.execute("EXEC PS_ETATBALANCE ?,?,?,?,?,?,?,?", list(params.values()))

        rows = cursor.fetchall()
        results = []
        for row in rows:
            result = {}
            
            result['AG_CODEAGENCE'] = row.AG_CODEAGENCE
            result['AG_RAISONSOCIAL'] = row.AG_RAISONSOCIAL
            result['PL_CODENUMCOMPTE'] = row.PL_CODENUMCOMPTE
            result['PL_NUMCOMPTE'] = row.PL_NUMCOMPTE
            result['PL_LIBELLE'] = row.PL_LIBELLE
            result['PL_COMPTECOLLECTIF'] = row.PL_COMPTECOLLECTIF
		
            result['MOUVEMENTPRECEDENTDEBIT'] = int(row.MOUVEMENTPRECEDENTDEBIT)
            result['MOUVEMENTPRECEDENTCREDIT'] = int(row.MOUVEMENTPRECEDENTCREDIT)
            result['MOUVEMENTPERIODEDEBIT'] = int(row.MOUVEMENTPERIODEDEBIT)
            result['MOUVEMENTPERIODECREDIT'] = int(row.MOUVEMENTPERIODECREDIT)
            result['SOLDEPERIODEDEBIT'] = int(row.SOLDEPERIODEDEBIT)
            result['SOLDEPERIODECREDIT'] = int(row.SOLDEPERIODECREDIT)
		
            result['TOTALCHARGEPRECEDENT'] = int(row.TOTALCHARGEPRECEDENT)
            result['TOTALCHARGEENCOURS'] = int(row.TOTALCHARGEENCOURS)
            result['TOTALCHARGEFINAL'] = int(row.TOTALCHARGEFINAL)
            result['TOTALPRODUITPRECEDENT'] = int(row.TOTALPRODUITPRECEDENT)
            result['TOTALPRODUITENCOURS'] = int(row.TOTALPRODUITENCOURS)
            result['TOTALPRODUITFINAL'] = int(row.TOTALPRODUITFINAL)
		
            result['TOTALSOLDEPERIODEDEBIT'] = int(row.TOTALSOLDEPERIODEDEBIT)
            result['TOTALSOLDEPERIODECREDIT'] = int(row.TOTALSOLDEPERIODECREDIT)
            result['TOTALMOUVEMENTPRECEDENTDEBIT'] = int(row.TOTALMOUVEMENTPRECEDENTDEBIT)
            result['TOTALMOUVEMENTPRECEDENTCREDIT'] = int(row.TOTALMOUVEMENTPRECEDENTCREDIT)
            result['TOTALMOUVEMENTPERIODEDEBIT'] = int(row.TOTALMOUVEMENTPERIODEDEBIT)
            result['TOTALMOUVEMENTPERIODECREDIT'] = int(row.TOTALMOUVEMENTPERIODECREDIT)

            # Ajouter le dictionnaire à la liste des résultats
            results.append(result)
        
        return results
    except Exception as e:
        # En cas d'erreur, lever une exception avec un message approprié
        raise Exception(f"Erreur lors de la récupération des données: {str(e.args[1])}")







def parse_numeric(value):
    """Vérifie si la valeur est un nombre et la convertit. Renvoie une exception si la conversion échoue."""
    if value is None or value == '':
        return None
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Format numérique invalide: {value}")

def get_commit(connexion,clsBilletages):
    try:
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