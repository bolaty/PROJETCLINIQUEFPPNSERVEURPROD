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
import threading
from tools.toolTestDeConnexion import IsNetworkConnected, get_ip_address, get_public_ip_address, get_mac_address, PingHost
from tools.toolEnvoiSmsEmail import traitement_asynchrone,traitement_asynchroneVersement
from config import MYSQL_REPONSE,LIENAPISMS,CODECRYPTAGE
from tools.toolDate import parse_datetime



def pvgComptabilisationVersement(connection, clsMouvementcomptables):
        try:
            listOperation = []
            statutinternet = IsNetworkConnected()
            if statutinternet != 400:
                vlpNumPiece = pvgNumeroPieceComptable(connection, clsMouvementcomptables[0]['AG_CODEAGENCE'], clsMouvementcomptables[0]['MC_DATEPIECE'],clsMouvementcomptables[0]['OP_CODEOPERATEUR'])
                
                for clsMouvementcomptable in clsMouvementcomptables:
                    ip_address = get_ip_address()
                    public_ip_address = get_public_ip_address()
                    mac_address = get_mac_address()
                    LIBELLEACTION = clsMouvementcomptable['MC_LIBELLEOPERATION']
                    # Mettre ensemble les informations de l'ordinateur et les séparer par des @
                    sticker_code1 = ip_address + "@" + public_ip_address + "@" + mac_address
                    clsMouvementcomptable['MC_NUMPIECE'] = vlpNumPiece[0]['MC_NUMPIECE']
                    clsMouvementcomptable['MC_AUTRE2'] = ''
                    if clsMouvementcomptable['MC_REFERENCEPIECE'] == "":
                        clsMouvementcomptable['MC_REFERENCEPIECE'] = vlpNumPiece[0]['MC_NUMPIECE']
                        clsMouvementcomptable['MC_TERMINAL'] = sticker_code1
                    
                    
                    # 1- Exécution de la fonction pvg_comptabilisation_tontine pour la comptabilisation
                    DataSet = pvg_comptabilisation(connection, clsMouvementcomptable)
                    
                    # Vérifier si la première instruction s'est terminée avec succès
                    if DataSet:
                        if DataSet['EJ_TELEPHONE'] == '' or DataSet['EJ_TELEPHONE'] is None:
                            DataSet['EJ_TELEPHONE'] = clsMouvementcomptable['MC_CONTACTTIERS']
                        if DataSet['SL_MESSAGECLIENT']:
                            listOperation.append(DataSet)
                        # 2- Exécution de la fonction pvgDecisionEnvoiSMS pour l'envoi ou non du sms
                        
                        # 3- Exécution de la fonction pvpGenererMouchard pour l'insertion dans le mouchard DataSet["MC_NUMPIECE"]
                        pvpGenererMouchard(connection, clsMouvementcomptable['AG_CODEAGENCE'], clsMouvementcomptable['OP_CODEOPERATEUR'], vlpNumPiece[0]['MC_NUMPIECE'], "A", sticker_code1, LIBELLEACTION)

                        # 4- Exécution de la fonction pvgBordereau pour obtenir les informations du mouvement comptable
                        clsMouvementcomptable = DataSet  
                       
                
            # 3- Ajout du numéro de bordereau à SL_MESSAGEAPI
                        # Test du lien de l'API SMS
                LIENDAPISMS = LIENAPISMS + "Service/wsApisms.svc/SendMessage"
                clsMouvementcomptable['NUMEROBORDEREAU'] = clsMouvementcomptable['NUMEROBORDEREAU'] #+ "/" + clsParametreAppelApis[0]['SL_MESSAGEAPI']
                Retour = {}
                Retour['NUMEROBORDEREAU'] = clsMouvementcomptable['NUMEROBORDEREAU']
                Retour['MESSAGEAPI'] = ""#clsParametreAppelApis[0]['SL_MESSAGEAPI']
                if not IsValidateIP(LIENDAPISMS):
                        Retour['MESSAGEAPI']  = "L'API SMS doit être configurée !!!"
                Retour['SL_RESULTAT'] = "TRUE"
                        
                        # Démarrer le traitement asynchrone dans un thread
                if listOperation is not None and Retour['SL_RESULTAT'] == "TRUE":
                            get_commit(connection,clsMouvementcomptables)
                            thread_traitement = threading.Thread(target=traitement_asynchroneVersement, args=(connection, clsMouvementcomptables[0], listOperation))
                            thread_traitement.daemon = True  # Définir le thread comme démon
                            thread_traitement.start()
                # 4- Retourner le numéro de bordereau
                return Retour #clsMouvementcomptable['NUMEROBORDEREAU']
            else:
                Retour = {}
                Retour['SL_MESSAGE'] = 'Opération impossible veuillez revoir la connexion internet'
                Retour['SL_RESULTAT'] = "FALSE"
                return Retour
        except Exception as e:
            #connection.execute("ROLLBACK")
            #connection.close()
            Retour = {}
            Retour['SL_MESSAGE'] = str(e.args[0])
            Retour['SL_RESULTAT'] = "FALSE"
            return Retour
 



def pvgComptabilisationOperations(connexion, clsMouvementcomptables):
        try:
            cursor = connexion
            listOperation = []
            statutinternet = IsNetworkConnected()
            if statutinternet != 400:
                # generation du numero de piece pour la facture
                vlpNumPiece = pvgNumeroPiece(cursor, clsMouvementcomptables[0]['AG_CODEAGENCE'], clsMouvementcomptables[0]['MC_DATEPIECE'],clsMouvementcomptables[0]['OP_CODEOPERATEUR'])
                clsMouvementcomptables[0]['MC_NUMPIECE'] = vlpNumPiece[0]['MC_NUMPIECE']
                pvg_constatation_facture(cursor, clsMouvementcomptables[0])
                
                # generation du numero de piece pour le reglement de facture
                vlpNumPiece = pvgNumeroPiece(cursor, clsMouvementcomptables[0]['AG_CODEAGENCE'], clsMouvementcomptables[0]['MC_DATEPIECE'],clsMouvementcomptables[0]['OP_CODEOPERATEUR'])
                clsMouvementcomptables[0]['MC_NUMPIECE'] = vlpNumPiece[0]['MC_NUMPIECE']
                # vlpNumPiece = pvgRecupNumeroPiece(connexion, clsMouvementcomptables[0]['OP_CODEOPERATEUR'])
                for i, clsMouvementcomptable in enumerate(clsMouvementcomptables):
                    if i != len(clsMouvementcomptables) - 1:
                        clsMouvementcomptable['MC_NUMPIECE'] = vlpNumPiece[0]['MC_NUMPIECE']
                        clsMouvementcomptable['MC_REFERENCEPIECE'] = clsMouvementcomptables[0]['MC_REFERENCEPIECE']
                        
                        ip_address = get_ip_address()
                        public_ip_address = get_public_ip_address()
                        mac_address = get_mac_address()
                        LIBELLEACTION = clsMouvementcomptable['MC_LIBELLEOPERATION']
                        # Mettre ensemble les informations de l'ordinateur et les séparer par des @
                        sticker_code1 = ip_address + "@" + public_ip_address + "@" + mac_address
                        # 1- Exécution de la fonction pvg_comptabilisation_operation pour la comptabilisation
                        DataSet = pvg_comptabilisation_operation1(cursor, clsMouvementcomptable)
                    else:
                        # Dernière itération
                        clsMouvementcomptable['MC_NUMPIECE'] = vlpNumPiece[0]['MC_NUMPIECE']
                        clsMouvementcomptable['MC_REFERENCEPIECE'] = clsMouvementcomptables[0]['MC_REFERENCEPIECE']
                        
                        ip_address = get_ip_address()
                        public_ip_address = get_public_ip_address()
                        mac_address = get_mac_address()
                        LIBELLEACTION = clsMouvementcomptable['MC_LIBELLEOPERATION']
                        # Mettre ensemble les informations de l'ordinateur et les séparer par des @
                        sticker_code1 = ip_address + "@" + public_ip_address + "@" + mac_address
                        # 1- Exécution de la fonction pvg_comptabilisation_operation pour la comptabilisation
                        DataSet = pvg_comptabilisation_operation2(cursor, clsMouvementcomptable)
                        
                        # Vérifier si la première instruction s'est terminée avec succès
                        if DataSet:
                            listOperation.append(DataSet)
                            # 2- Exécution de la fonction pvgDecisionEnvoiSMS pour l'envoi ou non du sms
                            # 3- Exécution de la fonction pvpGenererMouchard pour l'insertion dans le mouchard DataSet["MC_NUMPIECE"]
                            pvpGenererMouchard(cursor, clsMouvementcomptable['AG_CODEAGENCE'], clsMouvementcomptable['OP_CODEOPERATEUR'], vlpNumPiece[0]['MC_NUMPIECE'], "A", sticker_code1, LIBELLEACTION)

                            # 4- Exécution de la fonction pvgBordereau pour obtenir les informations du mouvement comptable
                            clsMouvementcomptable = DataSet
                            
                        # 3- Ajout du numéro de bordereau à SL_MESSAGEAPI
                        # Test du lien de l'API SMS
                        LIENDAPISMS = LIENAPISMS + "Service/wsApisms.svc/SendMessage"
                        clsMouvementcomptable['NUMEROBORDEREAU'] = clsMouvementcomptable['NUMEROBORDEREAU'] #+ "/" + clsParametreAppelApis[0]['SL_MESSAGEAPI']
                        Retour = {}
                        Retour['NUMEROBORDEREAU'] = clsMouvementcomptable['NUMEROBORDEREAU']
                        Retour['MC_LIBELLEOPERATION'] = clsMouvementcomptable['MC_LIBELLEOPERATION']
                        Retour['MESSAGEAPI'] = ""#clsParametreAppelApis[0]['SL_MESSAGEAPI']
                        if not IsValidateIP(LIENDAPISMS):
                            Retour['MESSAGEAPI']  = "L'API SMS doit être configurée !!!"
                        Retour['SL_RESULTAT'] = "TRUE"
                        
                        # Démarrer le traitement asynchrone dans un thread
                        if listOperation is not None and Retour['SL_RESULTAT'] == "TRUE":
                            get_commit(cursor, clsMouvementcomptables)
                            thread_traitement = threading.Thread(target=traitement_asynchrone, args=(cursor, clsMouvementcomptables[0], listOperation))
                            thread_traitement.daemon = True  # Définir le thread comme démon
                            thread_traitement.start()
                
                # 4- Retourner le numéro de bordereau
                return Retour #clsMouvementcomptable['NUMEROBORDEREAU']
            else:
                Retour = {}
                Retour['SL_MESSAGE'] = 'Opération impossible veuillez revoir la connexion internet'
                Retour['SL_RESULTAT'] = "FALSE"
                return Retour
        except Exception as e:
            #connexion.execute("ROLLBACK")
            #connexion.close()
            Retour = {}
            Retour['SL_MESSAGE'] = str(e.args[0])
            Retour['SL_RESULTAT'] = "FALSE"
            return Retour
        
def pvgComptabilisationOperationsFacture(connexion, clsMouvementcomptables):
        try:
            listOperation = []
            statutinternet = IsNetworkConnected()
            if statutinternet != 400:
                vlpNumPiece = pvgNumeroPiece(connexion, clsMouvementcomptables[0]['AG_CODEAGENCE'], clsMouvementcomptables[0]['MC_DATEPIECE'],clsMouvementcomptables[0]['OP_CODEOPERATEUR'])
                clsMouvementcomptables[0]['MC_NUMPIECE'] = vlpNumPiece[0]['MC_NUMPIECE']
                clsMouvementcomptables[0]['MC_REFERENCEPIECE'] = vlpNumPiece[0]['MC_REFERENCEPIECE']
                
                for i, clsMouvementcomptable in enumerate(clsMouvementcomptables):
                    
                        # Dernière itération
                        clsMouvementcomptable['MC_NUMPIECE'] = vlpNumPiece[0]['MC_NUMPIECE']
                        clsMouvementcomptable['MC_REFERENCEPIECE'] = vlpNumPiece[0]['MC_REFERENCEPIECE']
                        
                        ip_address = get_ip_address()
                        public_ip_address = get_public_ip_address()
                        mac_address = get_mac_address()
                        LIBELLEACTION = clsMouvementcomptable['MC_LIBELLEOPERATION']
                        # Mettre ensemble les informations de l'ordinateur et les séparer par des @
                        sticker_code1 = ip_address + "@" + public_ip_address + "@" + mac_address
                        # 1- Exécution de la fonction pvg_comptabilisation_operation pour la comptabilisation
                        DataSet = pvg_comptabilisation_operation2(connexion, clsMouvementcomptable)
                        
                        # Vérifier si la première instruction s'est terminée avec succès
                        if DataSet:
                            listOperation.append(DataSet)
                            # 2- Exécution de la fonction pvgDecisionEnvoiSMS pour l'envoi ou non du sms
                            # 3- Exécution de la fonction pvpGenererMouchard pour l'insertion dans le mouchard DataSet["MC_NUMPIECE"]
                            pvpGenererMouchard(connexion, clsMouvementcomptable['AG_CODEAGENCE'], clsMouvementcomptable['OP_CODEOPERATEUR'], vlpNumPiece[0]['MC_NUMPIECE'], "A", sticker_code1, LIBELLEACTION)

                            # 4- Exécution de la fonction pvgBordereau pour obtenir les informations du mouvement comptable
                            clsMouvementcomptable = DataSet
                            
                        # 3- Ajout du numéro de bordereau à SL_MESSAGEAPI
                        # Test du lien de l'API SMS
                        LIENDAPISMS = LIENAPISMS + "Service/wsApisms.svc/SendMessage"
                        clsMouvementcomptable['NUMEROBORDEREAU'] = clsMouvementcomptable['NUMEROBORDEREAU'] #+ "/" + clsParametreAppelApis[0]['SL_MESSAGEAPI']
                        Retour = {}
                        Retour['NUMEROBORDEREAU'] = clsMouvementcomptable['NUMEROBORDEREAU']
                        Retour['MC_LIBELLEOPERATION'] = clsMouvementcomptable['MC_LIBELLEOPERATION']
                        Retour['MESSAGEAPI'] = ""#clsParametreAppelApis[0]['SL_MESSAGEAPI']
                        if not IsValidateIP(LIENDAPISMS):
                            Retour['MESSAGEAPI']  = "L'API SMS doit être configurée !!!"
                        Retour['SL_RESULTAT'] = "TRUE"
                        
                        # Démarrer le traitement asynchrone dans un thread
                        if listOperation is not None and Retour['SL_RESULTAT'] == "TRUE":
                            get_commit(connexion, clsMouvementcomptables)
                            thread_traitement = threading.Thread(target=traitement_asynchrone, args=(connexion, clsMouvementcomptables[0], listOperation))
                            thread_traitement.daemon = True  # Définir le thread comme démon
                            thread_traitement.start()
                
                # 4- Retourner le numéro de bordereau
                return Retour #clsMouvementcomptable['NUMEROBORDEREAU']
            else:
                Retour = {}
                Retour['SL_MESSAGE'] = 'Opération impossible veuillez revoir la connexion internet'
                Retour['SL_RESULTAT'] = "FALSE"
                return Retour
        except Exception as e:
            #connexion.execute("ROLLBACK")
            #connexion.close()
            Retour = {}
            Retour['SL_MESSAGE'] = str(e.args[0])
            Retour['SL_RESULTAT'] = "FALSE"
            return Retour        
        
def pvgComptabilisationOperationsCaisse(cursor, clsMouvementcomptables):
    try:
        listOperation = []
        statutinternet = IsNetworkConnected()
        if statutinternet != 400:
            vlpNumPiece = pvgNumeroPiece(cursor, clsMouvementcomptables[0]['AG_CODEAGENCE'], clsMouvementcomptables[0]['MC_DATEPIECE'],clsMouvementcomptables[0]['OP_CODEOPERATEUR'])
            clsMouvementcomptables[0]['MC_NUMPIECE'] = vlpNumPiece[0]['MC_NUMPIECE']
            # clsMouvementcomptables[0]['MC_REFERENCEPIECE'] = vlpNumPiece[0]['MC_REFERENCEPIECE']

            for i, clsMouvementcomptable in enumerate(clsMouvementcomptables):
                if i != len(clsMouvementcomptables) - 1:
                    clsMouvementcomptable['MC_NUMPIECE'] = vlpNumPiece[0]['MC_NUMPIECE']
                    # clsMouvementcomptable['MC_REFERENCEPIECE'] = vlpNumPiece[0]['MC_REFERENCEPIECE']
                    
                    ip_address = get_ip_address()
                    public_ip_address = get_public_ip_address()
                    mac_address = get_mac_address()
                    LIBELLEACTION = clsMouvementcomptable['MC_LIBELLEOPERATION']
                    # Mettre ensemble les informations de l'ordinateur et les séparer par des @
                    sticker_code1 = ip_address + "@" + public_ip_address + "@" + mac_address
                    # 1- Exécution de la fonction pvg_comptabilisation_operation pour la comptabilisation
                    if clsMouvementcomptable['TS_CODETYPESCHEMACOMPTABLE'] == '00005': DataSet = pvg_comptabilisation_operation_caisse1(cursor, clsMouvementcomptable)
                    if clsMouvementcomptable['TS_CODETYPESCHEMACOMPTABLE'] != '00005': DataSet = pvg_comptabilisation_operation_caisse2(cursor, clsMouvementcomptable)
                else:
                    # Dernière itération
                    clsMouvementcomptable['MC_NUMPIECE'] = vlpNumPiece[0]['MC_NUMPIECE']
                    # clsMouvementcomptable['MC_REFERENCEPIECE'] = vlpNumPiece[0]['MC_REFERENCEPIECE']
                    
                    ip_address = get_ip_address()
                    public_ip_address = get_public_ip_address()
                    mac_address = get_mac_address()
                    LIBELLEACTION = clsMouvementcomptable['MC_LIBELLEOPERATION']
                    # Mettre ensemble les informations de l'ordinateur et les séparer par des @
                    sticker_code1 = ip_address + "@" + public_ip_address + "@" + mac_address
                    # 1- Exécution de la fonction pvg_comptabilisation_operation pour la comptabilisation
                    if clsMouvementcomptable['TS_CODETYPESCHEMACOMPTABLE'] == '00005': DataSet = pvg_comptabilisation_operation_caisse3(cursor, clsMouvementcomptable)
                    if clsMouvementcomptable['TS_CODETYPESCHEMACOMPTABLE'] != '00005': DataSet = pvg_comptabilisation_operation_caisse4(cursor, clsMouvementcomptable)
                    
                    # Vérifier si la première instruction s'est terminée avec succès
                    if DataSet:
                        if clsMouvementcomptable['MC_EMAILTIERS'] != '':
                              DataSet['EJ_EMAILCLIENT'] = clsMouvementcomptable['MC_EMAILTIERS']
                        if clsMouvementcomptable['MC_CONTACTTIERS'] != '':
                              DataSet['EJ_TELEPHONE'] = clsMouvementcomptable['MC_CONTACTTIERS']
                        listOperation.append(DataSet)
                        # 2- Exécution de la fonction pvgDecisionEnvoiSMS pour l'envoi ou non du sms
                        # 3- Exécution de la fonction pvpGenererMouchard pour l'insertion dans le mouchard DataSet["MC_NUMPIECE"]
                        pvpGenererMouchard(cursor, clsMouvementcomptable['AG_CODEAGENCE'], clsMouvementcomptable['OP_CODEOPERATEUR'], vlpNumPiece[0]['MC_NUMPIECE'], "A", sticker_code1, LIBELLEACTION)

                        # 4- Exécution de la fonction pvgBordereau pour obtenir les informations du mouvement comptable
                        clsMouvementcomptable = DataSet
                        
                    # 3- Ajout du numéro de bordereau à SL_MESSAGEAPI
                    # Test du lien de l'API SMS
                    LIENDAPISMS = LIENAPISMS + "Service/wsApisms.svc/SendMessage"
                    clsMouvementcomptable['NUMEROBORDEREAU'] = clsMouvementcomptable['NUMEROBORDEREAU'] #+ "/" + clsParametreAppelApis[0]['SL_MESSAGEAPI']
                    Retour = {}
                    Retour['NUMEROBORDEREAU'] = clsMouvementcomptable['NUMEROBORDEREAU']
                    Retour['MC_LIBELLEOPERATION'] = clsMouvementcomptable['MC_LIBELLEOPERATION']
                    Retour['MESSAGEAPI'] = ""#clsParametreAppelApis[0]['SL_MESSAGEAPI']
                    if not IsValidateIP(LIENDAPISMS):
                        Retour['MESSAGEAPI']  = "L'API SMS doit être configurée !!!"
                    Retour['SL_RESULTAT'] = "TRUE"
                    
                    # Démarrer le traitement asynchrone dans un thread
                    if listOperation is not None and Retour['SL_RESULTAT'] == "TRUE":
                        get_commit(cursor, clsMouvementcomptables)
                        thread_traitement = threading.Thread(target=traitement_asynchrone, args=(cursor, clsMouvementcomptables[0], listOperation))
                        thread_traitement.daemon = True  # Définir le thread comme démon
                        thread_traitement.start()
            
            # 4- Retourner le numéro de bordereau
            return Retour #clsMouvementcomptable['NUMEROBORDEREAU']
        else:
            Retour = {}
            Retour['SL_MESSAGE'] = 'Opération impossible veuillez revoir la connexion internet'
            Retour['SL_RESULTAT'] = "FALSE"
            return Retour
    except Exception as e:
        #connexion.execute("ROLLBACK")
        #connexion.close()
        Retour = {}
        Retour['SL_MESSAGE'] = str(e.args[0])
        Retour['SL_RESULTAT'] = "FALSE"
        return Retour

def pvgNumeroPieceComptable(connexion, _AG_CODEAGENCE, _MC_DATEPIECE, _OP_CODEOPERATEUR):
    params = {
        'AG_CODEAGENCE': _AG_CODEAGENCE,
        'MC_DATEPIECE': datetime.strptime(_MC_DATEPIECE, "%d/%m/%Y"),
        'OP_CODEOPERATEUR': _OP_CODEOPERATEUR
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
        cursor.execute("EXEC PS_INCREMENTNEW ?, ?, ?", list(params.values()))
    except Exception as e:
        cursor.close()
        # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = str(e.args[1])
        raise Exception(MYSQL_REPONSE)
      
    # Récupération des résultats
    try:
        resultatIncrement = recup_info_increment_piece(connexion, _OP_CODEOPERATEUR)
         
        return resultatIncrement    
    except Exception as e:
         # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible de récupérer les résultats de la procédure stockée : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)



def pvgNumeroPiece(curseur, _AG_CODEAGENCE, _MC_DATEPIECE, _OP_CODEOPERATEUR):
    params = {
        'AG_CODEAGENCE': _AG_CODEAGENCE,
        'MC_DATEPIECE': datetime.strptime(_MC_DATEPIECE, "%d/%m/%Y"),
        'OP_CODEOPERATEUR': _OP_CODEOPERATEUR
    }

    # Exécution de la procédure stockée
    try:
        cursor = curseur
    except Exception as e:
        cursor.close()
         # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible de récupérer le curseur de la base de données : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)

    # Exécution de la procédure stockée
    try:
        cursor.execute("EXEC PS_INCREMENTNEW ?, ?, ?", list(params.values()))
    except Exception as e:
        cursor.close()
        # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = str(e.args[1])
        raise Exception(MYSQL_REPONSE)
      
    # Récupération des résultats
    try:
        resultatIncrement = recup_info_increment_piece_op(curseur, _OP_CODEOPERATEUR)
         
        return resultatIncrement    
    except Exception as e:
         # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible de récupérer les résultats de la procédure stockée : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)



def recup_info_increment_piece(connexion, _OP_CODEOPERATEUR):
    try:
        cursor = connexion
        query = "SELECT * FROM dbo.TEMPINCREMENTRESULTAT{}".format(_OP_CODEOPERATEUR)
        # Exécution de la fonction SQL
        cursor.execute(query)

        # Récupération des résultats
        rows = cursor.fetchall()
        RetourNumResultat = []
        # Création d'un dictionnaire pour stocker les données récupérées
        # Traitement des résultats
        for row in rows:
            clsSms = {}
            clsSms['MC_NUMPIECE'] = row.MC_NUMPIECE
            clsSms['MC_REFERENCEPIECE'] = row.MC_REFERENCEPIECE
            RetourNumResultat.append(clsSms)
        # Faites ce que vous voulez avec les données récupérées
        return RetourNumResultat
    except Exception as e:
        MYSQL_REPONSE = str(e.args[1])
        raise Exception(MYSQL_REPONSE)

def recup_info_increment_piece_op(cursor, _OP_CODEOPERATEUR):
    try:
        query = "SELECT * FROM dbo.TEMPINCREMENTRESULTAT{}".format(_OP_CODEOPERATEUR)
        # Exécution de la fonction SQL
        cursor.execute(query)

        # Récupération des résultats
        rows = cursor.fetchall()
        RetourNumResultat = []
        # Création d'un dictionnaire pour stocker les données récupérées
        # Traitement des résultats
        for row in rows:
            clsSms = {}
            clsSms['MC_NUMPIECE'] = row.MC_NUMPIECE
            clsSms['MC_REFERENCEPIECE'] = row.MC_REFERENCEPIECE
            RetourNumResultat.append(clsSms)
        # Faites ce que vous voulez avec les données récupérées
        return RetourNumResultat
    except Exception as e:
        MYSQL_REPONSE = str(e.args[1])
        raise Exception(MYSQL_REPONSE)
    
    
    
def pvgRecupNumeroPiece(connexion, _OP_CODEOPERATEUR):
    try:
        cursor = connexion
        query = "SELECT * FROM dbo.TEMPMC_NUMPIECERESULTAT{}".format(_OP_CODEOPERATEUR)
        # Exécution de la fonction SQL
        cursor.execute(query)

        # Récupération des résultats
        rows = cursor.fetchall()
        RetourNumResultat = []
        # Création d'un dictionnaire pour stocker les données récupérées
        # Traitement des résultats
        for row in rows:
            clsSms = {}
            clsSms['MC_NUMPIECE'] = row.MC_NUMPIECE
            RetourNumResultat.append(clsSms)
        # Faites ce que vous voulez avec les données récupérées
        return RetourNumResultat
    except Exception as e:
        MYSQL_REPONSE = str(e.args[1])
        raise Exception(MYSQL_REPONSE)
    
    

def pvg_constatation_facture(curseur, cls_mouvement_comptable):
    # Paramètres de la procédure stockée
    params = {
        'AG_CODEAGENCE': cls_mouvement_comptable['AG_CODEAGENCE'],
        'MC_DATEPIECE': parse_datetime(cls_mouvement_comptable['MC_DATEPIECE']),
        'MC_NUMPIECE': cls_mouvement_comptable['MC_NUMPIECE'],
        'MC_NUMSEQUENCE': cls_mouvement_comptable['MC_NUMSEQUENCE'],
        'MR_CODEMODEREGLEMENT': cls_mouvement_comptable['MR_CODEMODEREGLEMENT'] if 'MR_CODEMODEREGLEMENT' in cls_mouvement_comptable and cls_mouvement_comptable['MR_CODEMODEREGLEMENT'] else None,
        'PT_IDPATIENT': cls_mouvement_comptable.get('PT_IDPATIENT') or None,
        'FT_CODEFACTURE': cls_mouvement_comptable.get('FT_CODEFACTURE') or None,
        'OP_CODEOPERATEUR': cls_mouvement_comptable['OP_CODEOPERATEUR'],
        'MC_MONTANTDEBIT': cls_mouvement_comptable['MC_MONTANTDEBIT'] if 'MC_MONTANTDEBIT' in cls_mouvement_comptable and cls_mouvement_comptable['MC_MONTANTDEBIT'] else 0,
        'MC_MONTANTCREDIT': cls_mouvement_comptable['MC_MONTANTCREDIT'] if 'MC_MONTANTCREDIT' in cls_mouvement_comptable and cls_mouvement_comptable['MC_MONTANTCREDIT'] else 0,
        'MC_DATESAISIE': parse_datetime(cls_mouvement_comptable['MC_DATESAISIE']),
        'MC_ANNULATION': cls_mouvement_comptable['MC_ANNULATION'],
        'JO_CODEJOURNAL': cls_mouvement_comptable['JO_CODEJOURNAL'] if 'JO_CODEJOURNAL' in cls_mouvement_comptable and cls_mouvement_comptable['JO_CODEJOURNAL'] else None,
        'MC_REFERENCEPIECE': cls_mouvement_comptable['MC_REFERENCEPIECE'],
        'MC_LIBELLEOPERATION': cls_mouvement_comptable['MC_LIBELLEOPERATION'],
        'PL_CODENUMCOMPTE': cls_mouvement_comptable['PL_CODENUMCOMPTE'] if 'PL_CODENUMCOMPTE' in cls_mouvement_comptable and cls_mouvement_comptable['PL_CODENUMCOMPTE'] else None,
        'MC_NOMTIERS': cls_mouvement_comptable['MC_NOMTIERS'],
        'MC_CONTACTTIERS': cls_mouvement_comptable['MC_CONTACTTIERS'],
        'MC_EMAILTIERS': cls_mouvement_comptable['MC_EMAILTIERS'],
        'MC_NUMPIECETIERS': cls_mouvement_comptable['MC_NUMPIECETIERS'],
        'MC_TERMINAL': cls_mouvement_comptable['MC_TERMINAL'],
        'MC_AUTRE': cls_mouvement_comptable['MC_AUTRE'],
        'MC_AUTRE1': cls_mouvement_comptable['MC_AUTRE1'],
        'MC_AUTRE2': cls_mouvement_comptable['MC_AUTRE2'],
        'MC_AUTRE3': cls_mouvement_comptable['MC_AUTRE3'],
        'TS_CODETYPESCHEMACOMPTABLE': '00001', # facture patient --cls_mouvement_comptable['TS_CODETYPESCHEMACOMPTABLE'],
        'MC_SENSBILLETAGE': cls_mouvement_comptable['MC_SENSBILLETAGE'],
        'MC_LIBELLEBANQUE': cls_mouvement_comptable['MC_LIBELLEBANQUE'],
        'CODECRYPTAGE': CODECRYPTAGE,
        'TYPEOPERATION': '',
        'MONTANT': cls_mouvement_comptable['MC_MONTANT_CONSTATIONFACTURE'] if 'MC_MONTANT_CONSTATIONFACTURE' in cls_mouvement_comptable and cls_mouvement_comptable['MC_MONTANT_CONSTATIONFACTURE'] else 0,
        'ACT_CODEACTE': cls_mouvement_comptable.get('ACT_CODEACTE') or None,
        'OP_CODEOPERATION': cls_mouvement_comptable.get('OP_CODEOPERATION') or None,
        'OP_CODEOPERATEURPASSATIONFOND': cls_mouvement_comptable.get('OP_CODEOPERATEURPASSATIONFOND') or None,
        'AS_CODEASSURANCE': cls_mouvement_comptable.get('AS_CODEASSURANCE') or None
    }

    # Récupérer la connexion et le curseur de la base de données depuis cls_donnee
    try:
        cursor = curseur
    except Exception as e:
        cursor.close()
         # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible de récupérer le curseur de la base de données : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)
    # Exécution de la procédure stockée
    try:
        # cursor.execute("EXECUTE PS_COMPTABILISATION  ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?,?,?", list(params.values()))
        cursor.execute("EXECUTE PS_COMPTABILISATIONCONSTATATIONFACTURE  ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?,?,?", list(params.values()))
    except Exception as e:
        cursor.close()
        # En cas d'erreur, annuler la transaction
        #cursor.execute("ROLLBACK")
        MYSQL_REPONSE = e.args[1]
        if "varchar" in MYSQL_REPONSE:
            MYSQL_REPONSE = MYSQL_REPONSE.split("varchar", 1)[1].split("en type de donn", 1)[0]
       
        raise Exception(MYSQL_REPONSE)
        
       # return {'error': f'Impossible d\'exécuter la procédure stockée : {str(e.args[1])}'}
  
def pvg_comptabilisation(connexion, cls_mouvement_comptable):
    # Paramètres de la procédure stockée
    params = {
        'AG_CODEAGENCE': cls_mouvement_comptable.get('AG_CODEAGENCE'),
        'MC_DATEPIECE': parse_datetime(cls_mouvement_comptable.get('MC_DATEPIECE')),
        'MC_NUMPIECE': cls_mouvement_comptable.get('MC_NUMPIECE'),
        'MC_NUMSEQUENCE': cls_mouvement_comptable.get('MC_NUMSEQUENCE'),
        'MR_CODEMODEREGLEMENT': cls_mouvement_comptable.get('MR_CODEMODEREGLEMENT'),
        'PT_IDPATIENT': cls_mouvement_comptable.get('PT_IDPATIENT') or None,
        'FT_CODEFACTURE': cls_mouvement_comptable.get('FT_CODEFACTURE') or None,
        'OP_CODEOPERATEUR': cls_mouvement_comptable.get('OP_CODEOPERATEUR'),
        'MC_MONTANTDEBIT': cls_mouvement_comptable.get('MC_MONTANTDEBIT'),
        'MC_MONTANTCREDIT': cls_mouvement_comptable.get('MC_MONTANTCREDIT'),
        'MC_DATESAISIE': parse_datetime(cls_mouvement_comptable.get('MC_DATESAISIE')),
        'MC_ANNULATION': cls_mouvement_comptable.get('MC_ANNULATION'),
        'JO_CODEJOURNAL': cls_mouvement_comptable.get('JO_CODEJOURNAL'),
        'MC_REFERENCEPIECE': cls_mouvement_comptable.get('MC_REFERENCEPIECE'),
        'MC_LIBELLEOPERATION': cls_mouvement_comptable.get('MC_LIBELLEOPERATION'),
        'PL_CODENUMCOMPTE': cls_mouvement_comptable.get('PL_CODENUMCOMPTE'),
        'MC_NOMTIERS': cls_mouvement_comptable.get('MC_NOMTIERS'),
        'MC_CONTACTTIERS': cls_mouvement_comptable.get('MC_CONTACTTIERS'),
        'MC_EMAILTIERS': cls_mouvement_comptable.get('MC_EMAILTIERS'),
        'MC_NUMPIECETIERS': cls_mouvement_comptable.get('MC_NUMPIECETIERS'),
        'MC_TERMINAL': cls_mouvement_comptable.get('MC_TERMINAL'),
        'MC_AUTRE': cls_mouvement_comptable.get('MC_AUTRE'),
        'MC_AUTRE1': cls_mouvement_comptable.get('MC_AUTRE1'),
        'MC_AUTRE2': cls_mouvement_comptable.get('MC_AUTRE2'),
        'MC_AUTRE3': cls_mouvement_comptable.get('MC_AUTRE3'),
        'TS_CODETYPESCHEMACOMPTABLE': cls_mouvement_comptable.get('TS_CODETYPESCHEMACOMPTABLE'),
        'MC_SENSBILLETAGE': cls_mouvement_comptable.get('MC_SENSBILLETAGE'),
        'MC_LIBELLEBANQUE': cls_mouvement_comptable.get('MC_LIBELLEBANQUE'),
        'CODECRYPTAGE': CODECRYPTAGE,#cls_mouvement_comptable.get('CODECRYPTAGE'),
        'TYPEOPERATION': 0 #cls_mouvement_comptable.get('TYPEOPERATION')
    }

     # Récupérer la connexion et le curseur de la base de données depuis cls_donnee
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
        cursor.execute("EXECUTE PC_MOUVEMENTCOMPTABLE  ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?", list(params.values()))
    except Exception as e:
        cursor.close()
        # En cas d'erreur, annuler la transaction
        MYSQL_REPONSE = e.args[1]
        if "varchar" in MYSQL_REPONSE:
            MYSQL_REPONSE = MYSQL_REPONSE.split("varchar", 1)[1].split("en type de donn", 1)[0]
       
        raise Exception(MYSQL_REPONSE)
    
  
    # Récupération des résultats
    try:

        # Convertir la chaîne de caractères en entier
        montant_debit_int = cls_mouvement_comptable.get('EM_MONTANT')#int(montant_debit_str)
        resultat = recupnum_bordereau(connexion, cls_mouvement_comptable['AG_CODEAGENCE'], cls_mouvement_comptable['MC_DATEPIECE'], cls_mouvement_comptable.get('TS_CODETYPESCHEMACOMPTABLE'), cls_mouvement_comptable.get('PT_IDPATIENT'), cls_mouvement_comptable['OP_CODEOPERATEUR'],  montant_debit_int, CODECRYPTAGE)
           
        return resultat    
    except Exception as e:
         # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible de récupérer les résultats de la procédure stockée : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)


  
  
def pvg_comptabilisation_operation1(curseur, cls_mouvement_comptable):
    # Paramètres de la procédure stockée
    params = {
        'AG_CODEAGENCE': cls_mouvement_comptable['AG_CODEAGENCE'],
        'MC_DATEPIECE': parse_datetime(cls_mouvement_comptable['MC_DATEPIECE']),
        'MC_NUMPIECE': cls_mouvement_comptable['MC_NUMPIECE'],
        'MC_NUMSEQUENCE': cls_mouvement_comptable['MC_NUMSEQUENCE'],
        'MR_CODEMODEREGLEMENT': cls_mouvement_comptable['MR_CODEMODEREGLEMENT'] if 'MR_CODEMODEREGLEMENT' in cls_mouvement_comptable and cls_mouvement_comptable['MR_CODEMODEREGLEMENT'] else None,
        'PT_IDPATIENT': cls_mouvement_comptable.get('PT_IDPATIENT') or None,
        'FT_CODEFACTURE': cls_mouvement_comptable.get('FT_CODEFACTURE') or None,
        'OP_CODEOPERATEUR': cls_mouvement_comptable['OP_CODEOPERATEUR'],
        'MC_MONTANTDEBIT': cls_mouvement_comptable['MC_MONTANTDEBIT'],
        'MC_MONTANTCREDIT': cls_mouvement_comptable['MC_MONTANTCREDIT'],
        'MC_DATESAISIE': parse_datetime(cls_mouvement_comptable['MC_DATESAISIE']),
        'MC_ANNULATION': cls_mouvement_comptable['MC_ANNULATION'],
        'JO_CODEJOURNAL': cls_mouvement_comptable['JO_CODEJOURNAL'] if 'JO_CODEJOURNAL' in cls_mouvement_comptable and cls_mouvement_comptable['JO_CODEJOURNAL'] else None,
        'MC_REFERENCEPIECE': cls_mouvement_comptable['MC_REFERENCEPIECE'],
        'MC_LIBELLEOPERATION': cls_mouvement_comptable['MC_LIBELLEOPERATION'],
        'PL_CODENUMCOMPTE': cls_mouvement_comptable['PL_CODENUMCOMPTE'] if 'PL_CODENUMCOMPTE' in cls_mouvement_comptable and cls_mouvement_comptable['PL_CODENUMCOMPTE'] else None,
        'MC_NOMTIERS': cls_mouvement_comptable['MC_NOMTIERS'],
        'MC_CONTACTTIERS': cls_mouvement_comptable['MC_CONTACTTIERS'],
        'MC_EMAILTIERS': cls_mouvement_comptable['MC_EMAILTIERS'],
        'MC_NUMPIECETIERS': cls_mouvement_comptable['MC_NUMPIECETIERS'],
        'MC_TERMINAL': cls_mouvement_comptable['MC_TERMINAL'],
        'MC_AUTRE': cls_mouvement_comptable['MC_AUTRE'],
        'MC_AUTRE1': cls_mouvement_comptable['MC_AUTRE1'],
        'MC_AUTRE2': cls_mouvement_comptable['MC_AUTRE2'],
        'MC_AUTRE3': cls_mouvement_comptable['MC_AUTRE3'],
        'TS_CODETYPESCHEMACOMPTABLE': '00002', # reglement facture patient --cls_mouvement_comptable['TS_CODETYPESCHEMACOMPTABLE'],
        'MC_SENSBILLETAGE': cls_mouvement_comptable['MC_SENSBILLETAGE'],
        'MC_LIBELLEBANQUE': cls_mouvement_comptable['MC_LIBELLEBANQUE'],
        'CODECRYPTAGE': CODECRYPTAGE,
        'TYPEOPERATION': '',
        'MONTANT': cls_mouvement_comptable['MC_MONTANT_FACTURE'],
        'ACT_CODEACTE': cls_mouvement_comptable.get('ACT_CODEACTE') or None,
        'OP_CODEOPERATION': cls_mouvement_comptable.get('OP_CODEOPERATION') or None,
        'OP_CODEOPERATEURPASSATIONFOND': cls_mouvement_comptable.get('OP_CODEOPERATEURPASSATIONFOND') or None,
        'AS_CODEASSURANCE': cls_mouvement_comptable.get('AS_CODEASSURANCE') or None
    }

    # Récupérer la connexion et le curseur de la base de données depuis cls_donnee
    try:
        cursor = curseur
    except Exception as e:
        cursor.close()
         # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible de récupérer le curseur de la base de données : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)
    # Exécution de la procédure stockée
    try:
        cursor.execute("EXECUTE PS_COMPTABILISATIONREGLEMENTFACTURE  ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?,?,?", list(params.values()))
    except Exception as e:
        cursor.close()
        # En cas d'erreur, annuler la transaction
        #cursor.execute("ROLLBACK")
        MYSQL_REPONSE = e.args[1]
        if "varchar" in MYSQL_REPONSE:
            MYSQL_REPONSE = MYSQL_REPONSE.split("varchar", 1)[1].split("en type de donn", 1)[0]
       
        raise Exception(MYSQL_REPONSE)



def pvg_comptabilisation_operation2(curseur, cls_mouvement_comptable):
    # Paramètres de la procédure stockée
    params = {
        'AG_CODEAGENCE': cls_mouvement_comptable['AG_CODEAGENCE'],
        'MC_DATEPIECE': parse_datetime(cls_mouvement_comptable['MC_DATEPIECE']),
        'MC_NUMPIECE': cls_mouvement_comptable['MC_NUMPIECE'],
        'MC_NUMSEQUENCE': cls_mouvement_comptable['MC_NUMSEQUENCE'],
        'MR_CODEMODEREGLEMENT': cls_mouvement_comptable['MR_CODEMODEREGLEMENT'] if 'MR_CODEMODEREGLEMENT' in cls_mouvement_comptable and cls_mouvement_comptable['MR_CODEMODEREGLEMENT'] else None,
        'PT_IDPATIENT': cls_mouvement_comptable.get('PT_IDPATIENT') or None,
        'FT_CODEFACTURE': cls_mouvement_comptable.get('FT_CODEFACTURE') or None,
        'OP_CODEOPERATEUR': cls_mouvement_comptable['OP_CODEOPERATEUR'],
        'MC_MONTANTDEBIT': cls_mouvement_comptable['MC_MONTANTDEBIT'],
        'MC_MONTANTCREDIT': cls_mouvement_comptable['MC_MONTANTCREDIT'],
        'MC_DATESAISIE': parse_datetime(cls_mouvement_comptable['MC_DATESAISIE']),
        'MC_ANNULATION': cls_mouvement_comptable['MC_ANNULATION'],
        'JO_CODEJOURNAL': cls_mouvement_comptable['JO_CODEJOURNAL'] if 'JO_CODEJOURNAL' in cls_mouvement_comptable and cls_mouvement_comptable['JO_CODEJOURNAL'] else None,
        'MC_REFERENCEPIECE': cls_mouvement_comptable['MC_REFERENCEPIECE'],
        'MC_LIBELLEOPERATION': cls_mouvement_comptable['MC_LIBELLEOPERATION'],
        'PL_CODENUMCOMPTE': cls_mouvement_comptable['PL_CODENUMCOMPTE'] if 'PL_CODENUMCOMPTE' in cls_mouvement_comptable and cls_mouvement_comptable['PL_CODENUMCOMPTE'] else None,
        'MC_NOMTIERS': cls_mouvement_comptable['MC_NOMTIERS'],
        'MC_CONTACTTIERS': cls_mouvement_comptable['MC_CONTACTTIERS'],
        'MC_EMAILTIERS': cls_mouvement_comptable['MC_EMAILTIERS'],
        'MC_NUMPIECETIERS': cls_mouvement_comptable['MC_NUMPIECETIERS'],
        'MC_TERMINAL': cls_mouvement_comptable['MC_TERMINAL'],
        'MC_AUTRE': cls_mouvement_comptable['MC_AUTRE'],
        'MC_AUTRE1': cls_mouvement_comptable['MC_AUTRE1'],
        'MC_AUTRE2': cls_mouvement_comptable['MC_AUTRE2'],
        'MC_AUTRE3': cls_mouvement_comptable['MC_AUTRE3'],
        'TS_CODETYPESCHEMACOMPTABLE': '00002', # reglement facture patient --cls_mouvement_comptable['TS_CODETYPESCHEMACOMPTABLE'],
        'MC_SENSBILLETAGE': cls_mouvement_comptable['MC_SENSBILLETAGE'],
        'MC_LIBELLEBANQUE': cls_mouvement_comptable['MC_LIBELLEBANQUE'],
        'CODECRYPTAGE': CODECRYPTAGE,
        'TYPEOPERATION': '',
        'MONTANT': cls_mouvement_comptable['MC_MONTANT_FACTURE'],
        'ACT_CODEACTE': cls_mouvement_comptable.get('ACT_CODEACTE') or None,
        'OP_CODEOPERATION': cls_mouvement_comptable.get('OP_CODEOPERATION') or None,
        'OP_CODEOPERATEURPASSATIONFOND': cls_mouvement_comptable.get('OP_CODEOPERATEURPASSATIONFOND') or None,
        'AS_CODEASSURANCE': cls_mouvement_comptable.get('AS_CODEASSURANCE') or None
    }

    # Récupérer la connexion et le curseur de la base de données depuis cls_donnee
    try:
        cursor = curseur
    except Exception as e:
        cursor.close()
         # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible de récupérer le curseur de la base de données : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)
    # Exécution de la procédure stockée
    try:
        cursor.execute("EXECUTE PS_COMPTABILISATIONREGLEMENTFACTURE  ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?,?,?", list(params.values()))
    except Exception as e:
        cursor.close()
        # En cas d'erreur, annuler la transaction
        #cursor.execute("ROLLBACK")
        MYSQL_REPONSE = e.args[1]
        if "varchar" in MYSQL_REPONSE:
            MYSQL_REPONSE = MYSQL_REPONSE.split("varchar", 1)[1].split("en type de donn", 1)[0]
       
        raise Exception(MYSQL_REPONSE)
        
       # return {'error': f'Impossible d\'exécuter la procédure stockée : {str(e.args[1])}'}
    
  
    # Récupération des résultats
    try:
        # Assurez-vous que la valeur est une chaîne de caractères pour pouvoir la convertir en entier
        # montant_debit_str = cls_mouvement_comptable['MONTANT'][0]

        # Convertir la chaîne de caractères en entier
        montant_debit_int = cls_mouvement_comptable['MC_MONTANT_FACTURE']#int(montant_debit_str)
        resultat = recup_info_num_bordereau(curseur, cls_mouvement_comptable['AG_CODEAGENCE'], cls_mouvement_comptable['MC_DATEPIECE'], '00002', cls_mouvement_comptable['FT_CODEFACTURE'], cls_mouvement_comptable['OP_CODEOPERATEUR'],  montant_debit_int, CODECRYPTAGE)
        """
        if resultat:
           result= recup_info_apisms_clientpiece(connexion,cls_mouvement_comptable['OP_CODEOPERATEUR'])
           resultat["MC_NUMPIECE"]= result
        """   
        return resultat    
    except Exception as e:
         # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible de récupérer les résultats de la procédure stockée : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)

    # Retour des résultats
   # return rows



def pvg_comptabilisation_operation_caisse1(curseur, cls_mouvement_comptable):
    # Paramètres de la procédure stockée
    params = {
        'AG_CODEAGENCE': cls_mouvement_comptable['AG_CODEAGENCE'],
        'MC_DATEPIECE': parse_datetime(cls_mouvement_comptable['MC_DATEPIECE']),
        'MC_NUMPIECE': int(cls_mouvement_comptable['MC_NUMPIECE']),
        'MC_NUMSEQUENCE': cls_mouvement_comptable['MC_NUMSEQUENCE'],
        'MR_CODEMODEREGLEMENT': cls_mouvement_comptable['MR_CODEMODEREGLEMENT'] if 'MR_CODEMODEREGLEMENT' in cls_mouvement_comptable and cls_mouvement_comptable['MR_CODEMODEREGLEMENT'] else '',#None,
        'PT_IDPATIENT': cls_mouvement_comptable.get('PT_IDPATIENT') or '',#None,
        'FT_CODEFACTURE': cls_mouvement_comptable.get('FT_CODEFACTURE') or '',#None,
        'OP_CODEOPERATEUR': cls_mouvement_comptable['OP_CODEOPERATEUR'],
        'MC_MONTANTDEBIT': cls_mouvement_comptable.get('MC_MONTANTDEBIT') or 0,
        'MC_MONTANTCREDIT': cls_mouvement_comptable.get('MC_MONTANTCREDIT') or 0,
        'MC_DATESAISIE': parse_datetime(cls_mouvement_comptable['MC_DATESAISIE']),
        'MC_ANNULATION': cls_mouvement_comptable['MC_ANNULATION'],
        'JO_CODEJOURNAL': cls_mouvement_comptable['JO_CODEJOURNAL'] if 'JO_CODEJOURNAL' in cls_mouvement_comptable and cls_mouvement_comptable['JO_CODEJOURNAL'] else '',#None,
        'MC_REFERENCEPIECE': cls_mouvement_comptable['MC_REFERENCEPIECE'],
        'MC_LIBELLEOPERATION': cls_mouvement_comptable['MC_LIBELLEOPERATION'],
        'PL_CODENUMCOMPTE': cls_mouvement_comptable['PL_CODENUMCOMPTE'] if 'PL_CODENUMCOMPTE' in cls_mouvement_comptable and cls_mouvement_comptable['PL_CODENUMCOMPTE'] else '',#None,
        'MC_NOMTIERS': cls_mouvement_comptable['MC_NOMTIERS'],
        'MC_CONTACTTIERS': cls_mouvement_comptable['MC_CONTACTTIERS'],
        'MC_EMAILTIERS': cls_mouvement_comptable['MC_EMAILTIERS'],
        'MC_NUMPIECETIERS': cls_mouvement_comptable['MC_NUMPIECETIERS'],
        'MC_TERMINAL': cls_mouvement_comptable['MC_TERMINAL'],
        'MC_AUTRE': cls_mouvement_comptable['MC_AUTRE'],
        'MC_AUTRE1': cls_mouvement_comptable['MC_AUTRE1'],
        'MC_AUTRE2': cls_mouvement_comptable['MC_AUTRE2'],
        'MC_AUTRE3': cls_mouvement_comptable['MC_AUTRE3'],
        'TS_CODETYPESCHEMACOMPTABLE': cls_mouvement_comptable['TS_CODETYPESCHEMACOMPTABLE'],# '00003', # operation de caisse --cls_mouvement_comptable['TS_CODETYPESCHEMACOMPTABLE'],
        'MC_SENSBILLETAGE': cls_mouvement_comptable['MC_SENSBILLETAGE'],
        'MC_LIBELLEBANQUE': cls_mouvement_comptable['MC_LIBELLEBANQUE'],
        'CODECRYPTAGE': CODECRYPTAGE,
        'TYPEOPERATION': '',
        'MONTANT': cls_mouvement_comptable.get('MC_MONTANT_FACTURE') or 0,
        'ACT_CODEACTE': cls_mouvement_comptable.get('ACT_CODEACTE') or None,#None,
        'OP_CODEOPERATION': cls_mouvement_comptable.get('OP_CODEOPERATION') or '',#None,
        'OP_CODEOPERATEURPASSATIONFOND': cls_mouvement_comptable.get('OP_CODEOPERATEURPASSATIONFOND') or '',
        'AS_CODEASSURANCE': cls_mouvement_comptable.get('AS_CODEASSURANCE') or None
    }

    # Récupérer la connexion et le curseur de la base de données depuis cls_donnee
    try:
        cursor = curseur
    except Exception as e:
        cursor.close()
         # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible de récupérer le curseur de la base de données : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)
    # Exécution de la procédure stockée
    try:
        cursor.execute("EXECUTE PS_COMPTABILISATIONOPERATIONCAISSE2  ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?,?,?", list(params.values()))
        cursor.nextset()
    except Exception as e:
        cursor.close()
        # En cas d'erreur, annuler la transaction
        #cursor.execute("ROLLBACK")
        MYSQL_REPONSE = e.args[1]
        if "varchar" in MYSQL_REPONSE:
            MYSQL_REPONSE = MYSQL_REPONSE.split("varchar", 1)[1].split("en type de donn", 1)[0]
       
        raise Exception(MYSQL_REPONSE)
    
    

def pvg_comptabilisation_operation_caisse2(curseur, cls_mouvement_comptable):
    # Paramètres de la procédure stockée
    params = {
        'AG_CODEAGENCE': cls_mouvement_comptable['AG_CODEAGENCE'],
        'MC_DATEPIECE': parse_datetime(cls_mouvement_comptable['MC_DATEPIECE']),
        'MC_NUMPIECE': int(cls_mouvement_comptable['MC_NUMPIECE']),
        'MC_NUMSEQUENCE': cls_mouvement_comptable['MC_NUMSEQUENCE'],
        'MR_CODEMODEREGLEMENT': cls_mouvement_comptable['MR_CODEMODEREGLEMENT'] if 'MR_CODEMODEREGLEMENT' in cls_mouvement_comptable and cls_mouvement_comptable['MR_CODEMODEREGLEMENT'] else '',#None,
        'PT_IDPATIENT': cls_mouvement_comptable.get('PT_IDPATIENT') or '',#None,
        'FT_CODEFACTURE': cls_mouvement_comptable.get('FT_CODEFACTURE') or '',#None,
        'OP_CODEOPERATEUR': cls_mouvement_comptable['OP_CODEOPERATEUR'],
        'MC_MONTANTDEBIT': cls_mouvement_comptable.get('MC_MONTANTDEBIT') or 0,
        'MC_MONTANTCREDIT': cls_mouvement_comptable.get('MC_MONTANTCREDIT') or 0,
        'MC_DATESAISIE': parse_datetime(cls_mouvement_comptable['MC_DATESAISIE']),
        'MC_ANNULATION': cls_mouvement_comptable['MC_ANNULATION'],
        'JO_CODEJOURNAL': cls_mouvement_comptable['JO_CODEJOURNAL'] if 'JO_CODEJOURNAL' in cls_mouvement_comptable and cls_mouvement_comptable['JO_CODEJOURNAL'] else '',#None,
        'MC_REFERENCEPIECE': cls_mouvement_comptable['MC_REFERENCEPIECE'],
        'MC_LIBELLEOPERATION': cls_mouvement_comptable['MC_LIBELLEOPERATION'],
        'PL_CODENUMCOMPTE': cls_mouvement_comptable['PL_CODENUMCOMPTE'] if 'PL_CODENUMCOMPTE' in cls_mouvement_comptable and cls_mouvement_comptable['PL_CODENUMCOMPTE'] else '',#None,
        'MC_NOMTIERS': cls_mouvement_comptable['MC_NOMTIERS'],
        'MC_CONTACTTIERS': cls_mouvement_comptable['MC_CONTACTTIERS'],
        'MC_EMAILTIERS': cls_mouvement_comptable['MC_EMAILTIERS'],
        'MC_NUMPIECETIERS': cls_mouvement_comptable['MC_NUMPIECETIERS'],
        'MC_TERMINAL': cls_mouvement_comptable['MC_TERMINAL'],
        'MC_AUTRE': cls_mouvement_comptable['MC_AUTRE'],
        'MC_AUTRE1': cls_mouvement_comptable['MC_AUTRE1'],
        'MC_AUTRE2': cls_mouvement_comptable['MC_AUTRE2'],
        'MC_AUTRE3': cls_mouvement_comptable['MC_AUTRE3'],
        'TS_CODETYPESCHEMACOMPTABLE': cls_mouvement_comptable['TS_CODETYPESCHEMACOMPTABLE'],# '00003', # operation de caisse --cls_mouvement_comptable['TS_CODETYPESCHEMACOMPTABLE'],
        'MC_SENSBILLETAGE': cls_mouvement_comptable['MC_SENSBILLETAGE'],
        'MC_LIBELLEBANQUE': cls_mouvement_comptable['MC_LIBELLEBANQUE'],
        'CODECRYPTAGE': CODECRYPTAGE,
        'TYPEOPERATION': '',
        'MONTANT': cls_mouvement_comptable.get('MC_MONTANT_FACTURE') or 0,
        'ACT_CODEACTE': cls_mouvement_comptable.get('ACT_CODEACTE') or None,#None,
        'OP_CODEOPERATION': cls_mouvement_comptable.get('OP_CODEOPERATION') or '',#None,
        'OP_CODEOPERATEURPASSATIONFOND': cls_mouvement_comptable.get('OP_CODEOPERATEURPASSATIONFOND') or '',
        'AS_CODEASSURANCE': cls_mouvement_comptable.get('AS_CODEASSURANCE') or None
    }

    # Récupérer la connexion et le curseur de la base de données depuis cls_donnee
    try:
        cursor = curseur
    except Exception as e:
        cursor.close()
         # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible de récupérer le curseur de la base de données : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)
    # Exécution de la procédure stockée
    try:
        cursor.execute("EXECUTE PS_COMPTABILISATIONOPERATIONCAISSE1  ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?,?,?", list(params.values()))
        cursor.nextset()
    except Exception as e:
        cursor.close()
        # En cas d'erreur, annuler la transaction
        #cursor.execute("ROLLBACK")
        MYSQL_REPONSE = e.args[1]
        if "varchar" in MYSQL_REPONSE:
            MYSQL_REPONSE = MYSQL_REPONSE.split("varchar", 1)[1].split("en type de donn", 1)[0]
       
        raise Exception(MYSQL_REPONSE)



def pvg_comptabilisation_operation_caisse3(curseur, cls_mouvement_comptable):
    # Paramètres de la procédure stockée
    params = {
        'AG_CODEAGENCE': cls_mouvement_comptable['AG_CODEAGENCE'],
        'MC_DATEPIECE': parse_datetime(cls_mouvement_comptable['MC_DATEPIECE']),
        'MC_NUMPIECE': int(cls_mouvement_comptable['MC_NUMPIECE']),
        'MC_NUMSEQUENCE': cls_mouvement_comptable['MC_NUMSEQUENCE'],
        'MR_CODEMODEREGLEMENT': cls_mouvement_comptable['MR_CODEMODEREGLEMENT'] if 'MR_CODEMODEREGLEMENT' in cls_mouvement_comptable and cls_mouvement_comptable['MR_CODEMODEREGLEMENT'] else '',
        'PT_IDPATIENT': cls_mouvement_comptable.get('PT_IDPATIENT') or '',
        'FT_CODEFACTURE': cls_mouvement_comptable.get('FT_CODEFACTURE') or '',
        'OP_CODEOPERATEUR': cls_mouvement_comptable['OP_CODEOPERATEUR'],
        'MC_MONTANTDEBIT': cls_mouvement_comptable.get('MC_MONTANTDEBIT') or 0,
        'MC_MONTANTCREDIT': cls_mouvement_comptable.get('MC_MONTANTCREDIT') or 0,
        'MC_DATESAISIE': parse_datetime(cls_mouvement_comptable['MC_DATESAISIE']),
        'MC_ANNULATION': cls_mouvement_comptable['MC_ANNULATION'],
        'JO_CODEJOURNAL': cls_mouvement_comptable['JO_CODEJOURNAL'] if 'JO_CODEJOURNAL' in cls_mouvement_comptable and cls_mouvement_comptable['JO_CODEJOURNAL'] else '',
        'MC_REFERENCEPIECE': cls_mouvement_comptable['MC_REFERENCEPIECE'],
        'MC_LIBELLEOPERATION': cls_mouvement_comptable['MC_LIBELLEOPERATION'],
        'PL_CODENUMCOMPTE': cls_mouvement_comptable['PL_CODENUMCOMPTE'] if 'PL_CODENUMCOMPTE' in cls_mouvement_comptable and cls_mouvement_comptable['PL_CODENUMCOMPTE'] else '',
        'MC_NOMTIERS': cls_mouvement_comptable['MC_NOMTIERS'],
        'MC_CONTACTTIERS': cls_mouvement_comptable['MC_CONTACTTIERS'],
        'MC_EMAILTIERS': cls_mouvement_comptable['MC_EMAILTIERS'],
        'MC_NUMPIECETIERS': cls_mouvement_comptable['MC_NUMPIECETIERS'],
        'MC_TERMINAL': cls_mouvement_comptable['MC_TERMINAL'],
        'MC_AUTRE': cls_mouvement_comptable['MC_AUTRE'],
        'MC_AUTRE1': cls_mouvement_comptable['MC_AUTRE1'],
        'MC_AUTRE2': cls_mouvement_comptable['MC_AUTRE2'],
        'MC_AUTRE3': cls_mouvement_comptable['MC_AUTRE3'],
        'TS_CODETYPESCHEMACOMPTABLE': cls_mouvement_comptable['TS_CODETYPESCHEMACOMPTABLE'],#'00003', # operation de caisse --cls_mouvement_comptable['TS_CODETYPESCHEMACOMPTABLE'],
        'MC_SENSBILLETAGE': cls_mouvement_comptable['MC_SENSBILLETAGE'],
        'MC_LIBELLEBANQUE': cls_mouvement_comptable['MC_LIBELLEBANQUE'],
        'CODECRYPTAGE': CODECRYPTAGE,
        'TYPEOPERATION': '',
        'MONTANT': cls_mouvement_comptable.get('MC_MONTANT_FACTURE') or 0,
        'ACT_CODEACTE': cls_mouvement_comptable.get('ACT_CODEACTE') or None,
        'OP_CODEOPERATION': cls_mouvement_comptable.get('OP_CODEOPERATION') or '',
        'OP_CODEOPERATEURPASSATIONFOND': cls_mouvement_comptable.get('OP_CODEOPERATEURPASSATIONFOND') or '',
        'AS_CODEASSURANCE': cls_mouvement_comptable.get('AS_CODEASSURANCE') or None
    }

    # Récupérer la connexion et le curseur de la base de données depuis cls_donnee
    try:
        cursor = curseur
    except Exception as e:
        cursor.close()
         # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible de récupérer le curseur de la base de données : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)
    # Exécution de la procédure stockée
    try:
        cursor.execute("EXECUTE PS_COMPTABILISATIONOPERATIONCAISSE2  ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?,?,?", list(params.values()))
        cursor.nextset()
    except Exception as e:
        cursor.close()
        # En cas d'erreur, annuler la transaction
        #cursor.execute("ROLLBACK")
        MYSQL_REPONSE = e.args[1]
        if "varchar" in MYSQL_REPONSE:
            MYSQL_REPONSE = MYSQL_REPONSE.split("varchar", 1)[1].split("en type de donn", 1)[0]
       
        raise Exception(MYSQL_REPONSE)
        
       # return {'error': f'Impossible d\'exécuter la procédure stockée : {str(e.args[1])}'}
    
  
    # Récupération des résultats
    try:
        # Assurez-vous que la valeur est une chaîne de caractères pour pouvoir la convertir en entier
        # montant_debit_str = cls_mouvement_comptable['MONTANT'][0]

        # Convertir la chaîne de caractères en entier
        montant_debit_int = cls_mouvement_comptable['MC_MONTANT_FACTURE']#int(montant_debit_str)
        resultat = recupinfos_num_bordereau(curseur, cls_mouvement_comptable['AG_CODEAGENCE'], cls_mouvement_comptable['MC_DATEPIECE'], cls_mouvement_comptable['TS_CODETYPESCHEMACOMPTABLE'], None, cls_mouvement_comptable['OP_CODEOPERATEUR'],  montant_debit_int, CODECRYPTAGE)
        """
        if resultat:
           result= recup_info_apisms_clientpiece(connexion,cls_mouvement_comptable['OP_CODEOPERATEUR'])
           resultat["MC_NUMPIECE"]= result
        """   
        return resultat
    except Exception as e:
         # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible de récupérer les résultats de la procédure stockée : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)

    # Retour des résultats
   # return rows



def pvg_comptabilisation_operation_caisse4(curseur, cls_mouvement_comptable):
    # Paramètres de la procédure stockée
    params = {
        'AG_CODEAGENCE': cls_mouvement_comptable['AG_CODEAGENCE'],
        'MC_DATEPIECE': parse_datetime(cls_mouvement_comptable['MC_DATEPIECE']),
        'MC_NUMPIECE': int(cls_mouvement_comptable['MC_NUMPIECE']),
        'MC_NUMSEQUENCE': cls_mouvement_comptable['MC_NUMSEQUENCE'],
        'MR_CODEMODEREGLEMENT': cls_mouvement_comptable['MR_CODEMODEREGLEMENT'] if 'MR_CODEMODEREGLEMENT' in cls_mouvement_comptable and cls_mouvement_comptable['MR_CODEMODEREGLEMENT'] else '',
        'PT_IDPATIENT': cls_mouvement_comptable.get('PT_IDPATIENT') or '',
        'FT_CODEFACTURE': cls_mouvement_comptable.get('FT_CODEFACTURE') or '',
        'OP_CODEOPERATEUR': cls_mouvement_comptable['OP_CODEOPERATEUR'],
        'MC_MONTANTDEBIT': cls_mouvement_comptable.get('MC_MONTANTDEBIT') or 0,
        'MC_MONTANTCREDIT': cls_mouvement_comptable.get('MC_MONTANTCREDIT') or 0,
        'MC_DATESAISIE': parse_datetime(cls_mouvement_comptable['MC_DATESAISIE']),
        'MC_ANNULATION': cls_mouvement_comptable['MC_ANNULATION'],
        'JO_CODEJOURNAL': cls_mouvement_comptable['JO_CODEJOURNAL'] if 'JO_CODEJOURNAL' in cls_mouvement_comptable and cls_mouvement_comptable['JO_CODEJOURNAL'] else '',
        'MC_REFERENCEPIECE': cls_mouvement_comptable['MC_REFERENCEPIECE'],
        'MC_LIBELLEOPERATION': cls_mouvement_comptable['MC_LIBELLEOPERATION'],
        'PL_CODENUMCOMPTE': cls_mouvement_comptable['PL_CODENUMCOMPTE'] if 'PL_CODENUMCOMPTE' in cls_mouvement_comptable and cls_mouvement_comptable['PL_CODENUMCOMPTE'] else '',
        'MC_NOMTIERS': cls_mouvement_comptable['MC_NOMTIERS'],
        'MC_CONTACTTIERS': cls_mouvement_comptable['MC_CONTACTTIERS'],
        'MC_EMAILTIERS': cls_mouvement_comptable['MC_EMAILTIERS'],
        'MC_NUMPIECETIERS': cls_mouvement_comptable['MC_NUMPIECETIERS'],
        'MC_TERMINAL': cls_mouvement_comptable['MC_TERMINAL'],
        'MC_AUTRE': cls_mouvement_comptable['MC_AUTRE'],
        'MC_AUTRE1': cls_mouvement_comptable['MC_AUTRE1'],
        'MC_AUTRE2': cls_mouvement_comptable['MC_AUTRE2'],
        'MC_AUTRE3': cls_mouvement_comptable['MC_AUTRE3'],
        'TS_CODETYPESCHEMACOMPTABLE': cls_mouvement_comptable['TS_CODETYPESCHEMACOMPTABLE'],#'00003', # operation de caisse --cls_mouvement_comptable['TS_CODETYPESCHEMACOMPTABLE'],
        'MC_SENSBILLETAGE': cls_mouvement_comptable['MC_SENSBILLETAGE'],
        'MC_LIBELLEBANQUE': cls_mouvement_comptable['MC_LIBELLEBANQUE'],
        'CODECRYPTAGE': CODECRYPTAGE,
        'TYPEOPERATION': '',
        'MONTANT': cls_mouvement_comptable.get('MC_MONTANT_FACTURE') or 0,
        'ACT_CODEACTE': cls_mouvement_comptable.get('ACT_CODEACTE') or None,
        'OP_CODEOPERATION': cls_mouvement_comptable.get('OP_CODEOPERATION') or '',
        'OP_CODEOPERATEURPASSATIONFOND': cls_mouvement_comptable.get('OP_CODEOPERATEURPASSATIONFOND') or '',
        'AS_CODEASSURANCE': cls_mouvement_comptable.get('AS_CODEASSURANCE') or None
    }

    # Récupérer la connexion et le curseur de la base de données depuis cls_donnee
    try:
        cursor = curseur
    except Exception as e:
        cursor.close()
         # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible de récupérer le curseur de la base de données : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)
    # Exécution de la procédure stockée
    try:
        cursor.execute("EXECUTE PS_COMPTABILISATIONOPERATIONCAISSE1  ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?,?,?", list(params.values()))
        cursor.nextset()
    except Exception as e:
        cursor.close()
        # En cas d'erreur, annuler la transaction
        #cursor.execute("ROLLBACK")
        MYSQL_REPONSE = e.args[1]
        if "varchar" in MYSQL_REPONSE:
            MYSQL_REPONSE = MYSQL_REPONSE.split("varchar", 1)[1].split("en type de donn", 1)[0]
       
        raise Exception(MYSQL_REPONSE)
        
       # return {'error': f'Impossible d\'exécuter la procédure stockée : {str(e.args[1])}'}
    
  
    # Récupération des résultats
    try:
        # Assurez-vous que la valeur est une chaîne de caractères pour pouvoir la convertir en entier
        # montant_debit_str = cls_mouvement_comptable['MONTANT'][0]

        # Convertir la chaîne de caractères en entier
        montant_debit_int = cls_mouvement_comptable['MC_MONTANT_FACTURE']#int(montant_debit_str)
        resultat = recupinfos_num_bordereau(curseur, cls_mouvement_comptable['AG_CODEAGENCE'], cls_mouvement_comptable['MC_DATEPIECE'], cls_mouvement_comptable['TS_CODETYPESCHEMACOMPTABLE'], None, cls_mouvement_comptable['OP_CODEOPERATEUR'],  montant_debit_int, CODECRYPTAGE)
        """
        if resultat:
           result= recup_info_apisms_clientpiece(connexion,cls_mouvement_comptable['OP_CODEOPERATEUR'])
           resultat["MC_NUMPIECE"]= result
        """   
        return resultat    
    except Exception as e:
         # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible de récupérer les résultats de la procédure stockée : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)

    # Retour des résultats
   # return rows



def recupinfos_num_bordereau(cursor, AG_CODEAGENCE,MC_DATEPIECE,TS_CODETYPESCHEMACOMPTABLE,FT_CODEFACTURE,OP_CODEOPERATEUR,MONTANT,ALPHA):
    try:
        # Exécution de la fonction SQL
        cursor.execute("SELECT * FROM dbo.FC_RECUPNUMEROBORDEREAUOPERATION(?, ?, ?, ?, ?, ?, ?)",
                       (AG_CODEAGENCE,parse_datetime(MC_DATEPIECE),TS_CODETYPESCHEMACOMPTABLE,FT_CODEFACTURE,OP_CODEOPERATEUR,MONTANT,ALPHA))

        # Récupération des résultats
        rows = cursor.fetchall()
        # Création d'un dictionnaire pour stocker les données récupérées
        borderau = {}
        # Traitement des résultats
        for row in rows:
            borderau['AG_CODEAGENCE'] = row.AG_CODEAGENCE
            borderau['MC_DATEPIECE'] = row.MC_DATEPIECE
            borderau['NUMEROBORDEREAU'] = row.NUMEROBORDEREAU
            borderau['PT_IDPATIENT'] = row.PT_IDPATIENT
            borderau['EJ_TELEPHONE'] = row.EJ_TELEPHONE
            borderau['SL_MESSAGECLIENT'] = row.SL_MESSAGECLIENT
            borderau['AG_EMAIL'] = row.AG_EMAIL
            borderau['AG_EMAILMOTDEPASSE'] = row.AG_EMAILMOTDEPASSE
            borderau['SL_MESSAGEOBJET'] = row.SL_MESSAGEOBJET
            borderau['EJ_EMAILCLIENT'] = row.EJ_EMAILCLIENT
            borderau['MC_LIBELLEOPERATION'] = row.MC_LIBELLEOPERATION
            # Faites ce que vous voulez avec les données récupérées
            return borderau
    except Exception as e:
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = str(e.args[1])
        raise Exception(MYSQL_REPONSE)
   
   
    
def recupnum_bordereau(connexion, AG_CODEAGENCE,MC_DATEPIECE,TS_CODETYPESCHEMACOMPTABLE,PT_IDPATIENT,OP_CODEOPERATEUR,MONTANT,ALPHA):
    try:
        cursor = connexion
        
        # Exécution de la fonction SQL
        cursor.execute("SELECT * FROM dbo.FC_RECUPNUMEROBORDEREAU(?, ?, ?, ?, ?, ?, ?)",
                       (AG_CODEAGENCE,parse_datetime(MC_DATEPIECE),TS_CODETYPESCHEMACOMPTABLE,PT_IDPATIENT,OP_CODEOPERATEUR,MONTANT,ALPHA))

        # Récupération des résultats
        rows = cursor.fetchall()
        # Création d'un dictionnaire pour stocker les données récupérées
        borderau = {}
        # Traitement des résultats
        for row in rows:
            borderau['AG_CODEAGENCE'] = row.AG_CODEAGENCE
            borderau['MC_DATEPIECE'] = row.MC_DATEPIECE
            borderau['NUMEROBORDEREAU'] = row.NUMEROBORDEREAU
            borderau['PT_IDPATIENT'] = row.PT_IDPATIENT
            borderau['EJ_TELEPHONE'] = row.EJ_TELEPHONE
            borderau['SL_MESSAGECLIENT'] = row.SL_MESSAGECLIENT
            borderau['AG_EMAIL'] = row.AG_EMAIL
            borderau['AG_EMAILMOTDEPASSE'] = row.AG_EMAILMOTDEPASSE
            borderau['SL_MESSAGEOBJET'] = row.SL_MESSAGEOBJET
            borderau['EJ_EMAILCLIENT'] = row.EJ_EMAILCLIENT
            borderau['MC_LIBELLEOPERATION'] = row.MC_LIBELLEOPERATION
            # Faites ce que vous voulez avec les données récupérées
            return borderau
    except Exception as e:
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = str(e.args[1])
        raise Exception(MYSQL_REPONSE)    

def recup_info_num_bordereau(cursor, AG_CODEAGENCE,MC_DATEPIECE,TS_CODETYPESCHEMACOMPTABLE,FT_CODEFACTURE,OP_CODEOPERATEUR,MONTANT,ALPHA):
    try:
        # Exécution de la fonction SQL
        cursor.execute("SELECT * FROM dbo.FC_RECUPNUMEROBORDEREAUOPERATION(?, ?, ?, ?, ?, ?, ?)",
                       (AG_CODEAGENCE,parse_datetime(MC_DATEPIECE),TS_CODETYPESCHEMACOMPTABLE,FT_CODEFACTURE,OP_CODEOPERATEUR,MONTANT,ALPHA))

        # Récupération des résultats
        rows = cursor.fetchall()
        # Création d'un dictionnaire pour stocker les données récupérées
        borderau = {}
        # Traitement des résultats
        for row in rows:
            borderau['AG_CODEAGENCE'] = row.AG_CODEAGENCE
            borderau['MC_DATEPIECE'] = row.MC_DATEPIECE
            borderau['NUMEROBORDEREAU'] = row.NUMEROBORDEREAU
            borderau['PT_IDPATIENT'] = row.PT_IDPATIENT
            borderau['EJ_TELEPHONE'] = row.EJ_TELEPHONE
            borderau['SL_MESSAGECLIENT'] = row.SL_MESSAGECLIENT
            borderau['AG_EMAIL'] = row.AG_EMAIL
            borderau['AG_EMAILMOTDEPASSE'] = row.AG_EMAILMOTDEPASSE
            borderau['SL_MESSAGEOBJET'] = row.SL_MESSAGEOBJET
            borderau['EJ_EMAILCLIENT'] = row.EJ_EMAILCLIENT
            borderau['MC_LIBELLEOPERATION'] = row.MC_LIBELLEOPERATION
            # Faites ce que vous voulez avec les données récupérées
            return borderau
    except Exception as e:
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = str(e.args[1])
        raise Exception(MYSQL_REPONSE)



def pvpGenererMouchard(cursor,clsObjetEnvoiOE_A, clsObjetEnvoiOE_Y, vppAction, vppTypeAction,TERMINALIDENTIFIANT,MC_LIBELLEOPERATION):
    clsMouchard = {}
    clsMouchard['AG_CODEAGENCE'] = clsObjetEnvoiOE_A
    clsMouchard['OP_CODEOPERATEUR'] = clsObjetEnvoiOE_Y
    
    if vppTypeAction == "A":
        # clsMouchard['MO_ACTION'] = "MOUVEMENTCOMPTABLE " + MC_LIBELLEOPERATION[0] + ' : ' + vppAction
        clsMouchard['MO_ACTION'] = "MOUVEMENTCOMPTABLE " + MC_LIBELLEOPERATION + ' : ' + vppAction
    elif vppTypeAction == "M":
        clsMouchard['MO_ACTION'] = "MOUVEMENTCOMPTABLE (Modification) : " + vppAction
    elif vppTypeAction == "S":
        clsMouchard['MO_ACTION'] = "MOUVEMENTCOMPTABLE (Suppression) : " + vppAction
    elif vppTypeAction == "E":
        clsMouchard['MO_ACTION'] = "MOUVEMENTCOMPTABLE (Edition de l'etat) : " + vppAction

    if clsMouchard['OP_CODEOPERATEUR'] == "":
        clsMouchard['OP_CODEOPERATEUR'] = None
    # Préparation des paramètres
        
    params = {}
    #return clsSmsouts
    params = {
        'AG_CODEAGENCE': clsMouchard['AG_CODEAGENCE'],
        'OP_CODEOPERATEUR': clsMouchard['OP_CODEOPERATEUR'],
        'MO_ACTION': clsMouchard['MO_ACTION'],
        'MO_TERMINALIDENTIFIANT': TERMINALIDENTIFIANT,
        'MO_TERMINALDESCRIPTION':  TERMINALIDENTIFIANT,
        'CODECRYPTAGE': CODECRYPTAGE,
        'TYPEOPERATION': 0
    }

    """ # Récupérer la connexion et le curseur de la base de données depuis cls_donnee
    try:
        cursor = connexion
    except Exception as e:
        cursor.close()
         # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible de récupérer le curseur de la base de données : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE) """

    # Exécution de la procédure stockée
    try:
        cursor.execute("EXECUTE PC_MOUCHARD   ?, ?, ?, ?, ?, ?, ?", list(params.values()))
        #instruction pour valider la commande de mise à jour
        #connexion.commit()
    except Exception as e:
        MYSQL_REPONSE = e.args[1]
        if "varchar" in MYSQL_REPONSE:
            MYSQL_REPONSE = MYSQL_REPONSE.split("varchar", 1)[1].split("en type de donn", 1)[0]
            
        raise Exception(MYSQL_REPONSE)




# -----------------------------------------------------------------------------------------------------------------------------
def IsValidateIP(ipaddress):
    ValidateIP = False
    ipaddress = ipaddress.replace("/ZenithwebClasse.svc/", "")
    ipaddress = ipaddress.replace("/Service/wsApisms.svc/SendMessage", "")

    if not ipaddress:
        return ValidateIP

    if "http://" in ipaddress:
        ipaddress = ipaddress.replace("http://", "")

    if "https://" in ipaddress:
        ipaddress = ipaddress.replace("https://", "")

    adresse = ipaddress.split(':')

    if len(adresse) != 2:
        return ValidateIP

    HostURI = adresse[0]
    PortNumber = adresse[1].replace("/", "")

    ValidateIP = PingHost(HostURI, int(PortNumber))
    return ValidateIP



def get_commit(cursor, clsMouvementcomptables):
    try:
        params = {
            'AG_CODEAGENCE3': '1000',
            'MC_DATEPIECE3': '01/01/1900'
        }
        try:
            cursor.commit()
            cursor.execute("EXECUTE [PC_COMMIT]  ?, ?", list(params.values()))
            #instruction pour valider la commande de mise à jour
            cursor.commit()
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