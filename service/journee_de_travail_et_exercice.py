import datetime
from datetime import datetime



def valeur_scalaire_requete_max(connexion, *vpp_critere):
    # Définition des critères et des paramètres
    if len(vpp_critere) == 0:
        vap_critere = ""
        vap_valeur_parametre = []
    
    elif len(vpp_critere) == 1:
        vap_critere = " WHERE AG_CODEAGENCE=?"
        vap_valeur_parametre = [vpp_critere[0]]
    elif len(vpp_critere) == 2:
        vap_critere = " WHERE AG_CODEAGENCE=? AND JT_DATEJOURNEETRAVAIL=?"
        vap_valeur_parametre = [vpp_critere[0], vpp_critere[1]]
    elif len(vpp_critere) == 3:
        vap_critere = " WHERE AG_CODEAGENCE=? AND JT_DATEJOURNEETRAVAIL=? AND  JT_STATUT=?"
        vap_valeur_parametre = [vpp_critere[0], vpp_critere[1], vpp_critere[2]]
    else:
        raise ValueError("Nombre de critères non pris en charge")

    vap_requete = f"""
        SELECT MAX(JT_DATEJOURNEETRAVAIL) AS JT_DATEJOURNEETRAVAIL  FROM JOURNEETRAVAIL {vap_critere}
    """

    cursor = connexion.cursor()
    try:
        # Exécution de la requête avec les paramètres
        cursor.execute(vap_requete, vap_valeur_parametre)
        
        # Récupération du résultat
        rows = cursor.fetchone()
        results = []
        for row in rows:
            result = {}
            result['JT_DATEJOURNEETRAVAIL'] = row.strftime("%d/%m/%Y")
            # Ajouter le dictionnaire à la liste des résultats
            results.append(result)
        return results
    except Exception as e:
        connexion.rollback()  # Annule la transaction en cas d'erreur
        raise Exception(f"Erreur lors de l'exécution de la requête : {str(e)}")
    finally:
        cursor.close()  # Fermeture du curseur dans le bloc finally



def valeur_scalaire_requete_count(connexion, *vpp_critere):
    # Définition des critères et des paramètres
    if len(vpp_critere) == 0:
        vap_critere = ""
        vap_valeur_parametre = []
    elif len(vpp_critere) == 1:
        vap_critere = " WHERE AG_CODEAGENCE=?"
        vap_valeur_parametre = [vpp_critere[0]]
    elif len(vpp_critere) == 2 and vpp_critere[1] == 'O':
        vap_critere = " WHERE AG_CODEAGENCE=? AND JT_STATUT=?"
        vap_valeur_parametre = [vpp_critere[0], vpp_critere[1]]
    elif len(vpp_critere) == 2:
        vap_critere = " WHERE AG_CODEAGENCE=? AND JT_DATEJOURNEETRAVAIL=?"
        vap_valeur_parametre = [vpp_critere[0], datetime.strptime(vpp_critere[1], "%d/%m/%Y")]
    else:
        raise ValueError("Nombre de critères non pris en charge")

    query = f"""
        SELECT COUNT(JT_DATEJOURNEETRAVAIL) AS JT_DATEJOURNEETRAVAIL 
        FROM JOURNEETRAVAIL {vap_critere}
    """

    cursor = connexion.cursor()
    try:
        # Exécution de la requête avec les paramètres
        cursor.execute(query, vap_valeur_parametre)
        
        # Récupération du résultat
        row = cursor.fetchone()
        result = {}
        result['JT_COUNT'] = row[0] if row else 0
        return result
    except Exception as e:
        connexion.rollback()  # Annule la transaction en cas d'erreur
        raise Exception(f"Erreur lors de l'exécution de la requête : {str(e)}")
    finally:
        cursor.close()  # Fermeture du curseur dans le bloc finally
        
        
        
def insert_journee_travail(connexion, cls_journeetravail):
    # Préparation des paramètres
    query = """
        INSERT INTO JOURNEETRAVAIL 
        (AG_CODEAGENCE, JT_DATEJOURNEETRAVAIL, JT_STATUT, OP_CODEOPERATEUR)
        VALUES (?, ?, ?, ?)
        """

    # Préparation des paramètres
    params = (
        cls_journeetravail['AG_CODEAGENCE'],
        cls_journeetravail['JT_DATEJOURNEETRAVAIL'],
        cls_journeetravail['JT_STATUT'],
        cls_journeetravail['OP_CODEOPERATEUR']
    )


    try:
        cursor = connexion
        # Exécution de la commande avec les paramètres
        cursor.execute(query, params)
        #connexion.commit()
        
    except Exception as e:
        connexion.rollback()
        raise Exception(f"Erreur lors de l'insertion de la journee de travail: {str(e)}")
    
    
    
def table_libelle_date_systeme_serveur(connexion, *vpp_critere):
    # Définition des critères et des paramètres
    if len(vpp_critere) == 0:
        vap_critere = ""
        vap_valeur_parametre = []
    
    vap_requete = f"""
        SELECT GETDATE() AS DATESYSTEMSERVEUR 
    """

    cursor = connexion.cursor()
    try:
        # Exécution de la requête avec les paramètres
        cursor.execute(vap_requete, vap_valeur_parametre)
        
        # Récupération du résultat
        rows = cursor.fetchone()
        results = []
        for row in rows:
            result = {}
            result['DATESYSTEMSERVEUR'] = row.strftime("%d/%m/%Y")
            # Ajouter le dictionnaire à la liste des résultats
            results.append(result)
        
        
        return results
    
    except Exception as e:
        connexion.rollback()  # Annule la transaction en cas d'erreur
        raise Exception(f"Erreur lors de l'exécution de la requête : {str(e)}")
    
    finally:
        cursor.close()  # Fermeture du curseur dans le bloc finally
        
        
        
# liste des journees
def liste_journee_travail(connexion, *vppCritere):
    cursor = connexion.cursor()
    
    if len(vppCritere) == 0:
        vap_critere = ""
        vap_nom_parametre = []
        vap_valeur_parametre = []
    elif len(vppCritere) == 1:
        vap_critere = " WHERE AG_CODEAGENCE=?"
        vap_nom_parametre = ["AG_CODEAGENCE"]
        vap_valeur_parametre = [vppCritere[0]]
    elif len(vppCritere) == 2:
        annee = vppCritere[1].year   # Extraction des 4 premiers caractères
        vap_critere = " WHERE AG_CODEAGENCE=? AND YEAR(JT_DATEJOURNEETRAVAIL)=?"
        vap_nom_parametre = ["AG_CODEAGENCE", "JT_DATEJOURNEETRAVAIL"]
        vap_valeur_parametre = [vppCritere[0], vppCritere[1]]
    elif len(vppCritere) == 3:
        annee = vppCritere[1].year
        vap_critere = " WHERE AG_CODEAGENCE=? AND YEAR(JT_DATEJOURNEETRAVAIL)=? AND JT_STATUT LIKE '%' + ? + '%'"
        vap_nom_parametre = ["AG_CODEAGENCE", "JT_DATEJOURNEETRAVAIL", "JT_STATUT"]
        vap_valeur_parametre = [vppCritere[0], annee, vppCritere[2]]
    else:
        raise ValueError("Case non pris en charge")

    query = f"""
        SELECT  TOP 10 * FROM JOURNEETRAVAIL 
        {vap_critere}
    """
    """ query = 
        SELECT  TOP 10 * FROM VUE_JOURNEETRAVAIL 
        {vap_critere}
    """
    try:
        cursor.execute(query, vap_valeur_parametre)
    except Exception as e:
        cursor.close()
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible d\'exécuter la procédure stockée : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)
    
    try:
        rows = cursor.fetchall()

        results = []
        for row in rows:
            result = {}
            result['AG_CODEAGENCE'] = row.AG_CODEAGENCE
            result['JT_DATEJOURNEETRAVAIL'] = '01/01/1900'
            if row.JT_DATEJOURNEETRAVAIL is not None:
              result['JT_DATEJOURNEETRAVAIL'] = row.JT_DATEJOURNEETRAVAIL.strftime("%d/%m/%Y")
            if row.JT_STATUT == 'O':
                result['JT_STATUT'] = 'ACTIVE'
            else:
                result['JT_STATUT'] = 'FERMEE'
            result['OP_CODEOPERATEUR'] = row.OP_CODEOPERATEUR  
            
            # Ajouter le dictionnaire à la liste des résultats
            results.append(result)
        return results
    except Exception as e:
        cursor.close()
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible d\'exécuter la procédure stockée : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)



def update_journee_travail_statut(connexion, ag_codeagence, jt_datejourneetravail, nouveau_statut):
    # Préparation de la requête de mise à jour
    query = """
        UPDATE JOURNEETRAVAIL 
        SET JT_STATUT = ? 
        WHERE AG_CODEAGENCE = ? AND JT_DATEJOURNEETRAVAIL = ?
    """

    # Préparation des paramètres
    params = (
        nouveau_statut,
        ag_codeagence,
        jt_datejourneetravail
    )

    try:
        cursor = connexion
        # Exécution de la commande avec les paramètres
        cursor.execute(query, params)
        #get_commit(params)  # Décommenter si vous gérez manuellement la transaction
        
    except Exception as e:
        connexion.rollback()  # Annule la transaction en cas d'erreur
        raise Exception(f"Erreur lors de la mise à jour du statut de la journée de travail : {str(e)}")
    #finally:
    #    cursor.close()  # Fermeture du curseur, décommenter si nécessaire