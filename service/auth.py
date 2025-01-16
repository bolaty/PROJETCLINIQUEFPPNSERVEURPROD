from config import CODECRYPTAGE



def connexion_utilisateur(connexion, clsInfoUsersconnect):
    # Préparation des paramètres
    params = {
        'OP_LOGIN': clsInfoUsersconnect['OP_LOGIN'],
        'OP_MOTPASSE': clsInfoUsersconnect['OP_MOTPASSE'],
        'CODECRYPTAGE': CODECRYPTAGE
    }

    # Exécution de la procédure stockée
    try:
        cursor = connexion
    except Exception as e:
        cursor.close()
         # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible de récupérer le curseur de la base de données : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)

    # Exécution de la procédure stockée
    try:
        cursor.execute("EXEC PS_LOGIN ?, ?, ?", list(params.values()))
    except Exception as e:
        cursor.close()
        # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = str(e.args[1])
        raise Exception(MYSQL_REPONSE)
      
    # Récupération des résultats
    try:
        rows = cursor.fetchall()
        RetourUserConnect = []
        # Création d'un dictionnaire pour stocker les données récupérées
        # Traitement des résultats
        for row in rows:
            clsUserConnect = {}
            clsUserConnect['OP_CODEOPERATEUR'] = row.OP_CODEOPERATEUR
            clsUserConnect['AG_CODEAGENCE'] = row.AG_CODEAGENCE
            clsUserConnect['PO_CODEPROFIL'] = row.PO_CODEPROFIL
            clsUserConnect['OP_URLPHOTO'] = row.OP_URLPHOTO
            clsUserConnect['OP_NOMPRENOM'] = row.OP_NOMPRENOM
            clsUserConnect['OP_TELEPHONE'] = row.OP_TELEPHONE
            clsUserConnect['OP_EMAIL'] = row.OP_EMAIL
            clsUserConnect['OP_LOGIN'] = row.OP_LOGIN
            clsUserConnect['OP_MOTPASSE'] = row.OP_MOTPASSE
            clsUserConnect['OP_DATESAISIE'] = row.OP_DATESAISIE.strftime("%d/%m/%Y")
            clsUserConnect['OP_NOMBRECONNEXION'] = row.OP_NOMBRECONNEXION
            clsUserConnect['AG_RAISONSOCIAL'] = row.AG_RAISONSOCIAL
            clsUserConnect['AG_ADRESSEGEOGRAPHIQUE'] = row.AG_ADRESSEGEOGRAPHIQUE
            clsUserConnect['AG_TELEPHONE'] = row.AG_TELEPHONE
            clsUserConnect['AG_EMAIL'] = row.AG_EMAIL
            clsUserConnect['OP_ACTIF'] = row.OP_ACTIF
            
            clsUserConnect['PL_CODENUMCOMPTECAISSE'] = row.PL_CODENUMCOMPTECAISSE
            clsUserConnect['PL_CODENUMCOMPTECOFFRE'] = row.PL_CODENUMCOMPTECOFFRE
            clsUserConnect['PL_CODENUMCOMPTEPROVISOIRE'] = row.PL_CODENUMCOMPTEPROVISOIRE
            clsUserConnect['PL_CODENUMCOMPTEWAVE'] = row.PL_CODENUMCOMPTEWAVE
            clsUserConnect['PL_CODENUMCOMPTEMTN'] = row.PL_CODENUMCOMPTEMTN
            clsUserConnect['PL_CODENUMCOMPTEORANGE'] = row.PL_CODENUMCOMPTEORANGE
            clsUserConnect['PL_CODENUMCOMPTEMOOV'] = row.PL_CODENUMCOMPTEMOOV
            clsUserConnect['PL_CODENUMCOMPTECHEQUE'] = row.PL_CODENUMCOMPTECHEQUE
            clsUserConnect['PL_CODENUMCOMPTEVIREMENT'] = row.PL_CODENUMCOMPTEVIREMENT

            RetourUserConnect.append(clsUserConnect)
        # Faites ce que vous voulez avec les données récupérées
        return RetourUserConnect
    except Exception as e:
         # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible de récupérer les résultats de la procédure stockée : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)