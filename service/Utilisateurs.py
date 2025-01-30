import random
import string
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
from config import MYSQL_REPONSE,LIENAPISMS,LIENAPPLICATIONCLIENT,CODECRYPTAGE
import threading
class clsAgence:
    def __init__(self):
        self.AG_RAISONSOCIAL = ''
        self.AG_EMAILMOTDEPASSE = ''
        self.AG_EMAIL = ''
        
        
        
def creation_profil(connection, operateur_info):
    params = {
        'PO_CODEPROFIL': "",
        'PO_LIBELLE': operateur_info['PO_LIBELLE'],
        'CODECRYPTAGE': CODECRYPTAGE,
        'TYPEOPERATION': 0  # 1 pour modification
    }
    

    try:
        cursor = connection
        cursor.execute("EXEC dbo.PC_PROFIL ?, ?, ?, ?", list(params.values()))
        connection.commit()
        get_commit(connection,operateur_info)
        #cursor.close()
    except Exception as e:
        connection.rollback()
        raise Exception(f"Erreur lors de la modification: {str(e.args[1])}")       
        
def update_profil(connection, operateur_info):
    params = {
        'PO_CODEPROFIL': operateur_info['PO_CODEPROFIL'],
        'PO_LIBELLE': operateur_info['PO_LIBELLE'],
        'CODECRYPTAGE': CODECRYPTAGE,
        'TYPEOPERATION': 1  # 1 pour modification
    }
    

    try:
        cursor = connection
        cursor.execute("EXEC dbo.PC_PROFIL ?, ?, ?, ?", list(params.values()))
        connection.commit()
        get_commit(connection,operateur_info)
        #cursor.close()
    except Exception as e:
        connection.rollback()
        raise Exception(f"Erreur lors de la modification: {str(e.args[1])}")            

def delete_profil(connection, operateur_info):
    params = {
        'PO_CODEPROFIL': operateur_info['PO_CODEPROFIL'],
        'PO_LIBELLE': "",
        'CODECRYPTAGE': CODECRYPTAGE,
        'TYPEOPERATION': 2  # 1 pour modification
    }
    

    try:
        cursor = connection
        cursor.execute("EXEC dbo.PC_PROFIL ?, ?, ?, ?", list(params.values()))
        connection.commit()
        get_commit(connection,operateur_info)
        #cursor.close()
    except Exception as e:
        connection.rollback()
        MYSQL_REPONSE = e.args[1]
        if "varchar" in MYSQL_REPONSE:
               MYSQL_REPONSE = MYSQL_REPONSE.split("varchar", 1)[1].split("en type de donn", 1)[0]
               
        raise Exception(MYSQL_REPONSE)            
        
#creation utilisateur...

def insert_operateur(connection, operateur_info):
    code_aleatoire = generer_code_aleatoire()
    # Préparation des paramètres
    params = {
        'OP_CODEOPERATEUR': int(code_aleatoire),#operateur_info['OP_CODEOPERATEUR'],
        'AG_CODEAGENCE': operateur_info['AG_CODEAGENCE'],
        'PO_CODEPROFIL': operateur_info['PO_CODEPROFIL'],
        'SR_CODESERVICE': operateur_info['SR_CODESERVICE'],
        'OP_NOMPRENOM': operateur_info['OP_NOMPRENOM'],
        'OP_TELEPHONE': operateur_info['OP_TELEPHONE'],
        'OP_EMAIL': operateur_info['OP_EMAIL'],
        'OP_LOGIN': operateur_info['OP_LOGIN'],
        'OP_MOTPASSE': operateur_info['OP_MOTPASSE'],
        'OP_URLPHOTO': operateur_info['OP_URLPHOTO'] if 'OP_URLPHOTO' in operateur_info else None,
        'OP_ACTIF': operateur_info['OP_ACTIF'],
        'PL_CODENUMCOMPTECAISSE': operateur_info.get('PL_CODENUMCOMPTECAISSE'),
        'PL_CODENUMCOMPTECOFFRE': operateur_info.get('PL_CODENUMCOMPTECOFFRE'),
        'PL_CODENUMCOMPTEPROVISOIRE': operateur_info.get('PL_CODENUMCOMPTEPROVISOIRE'),
        'PL_CODENUMCOMPTEWAVE': operateur_info.get('PL_CODENUMCOMPTEWAVE'),
        'PL_CODENUMCOMPTEMTN': operateur_info.get('PL_CODENUMCOMPTEMTN'),
        'PL_CODENUMCOMPTEORANGE': operateur_info.get('PL_CODENUMCOMPTEORANGE'),
        'PL_CODENUMCOMPTEMOOV': operateur_info.get('PL_CODENUMCOMPTEMOOV'),
        'PL_CODENUMCOMPTECHEQUE': operateur_info.get('PL_CODENUMCOMPTECHEQUE'),
        'PL_CODENUMCOMPTEVIREMENT': operateur_info.get('PL_CODENUMCOMPTEVIREMENT'),
        'OP_DATESAISIE': operateur_info['OP_DATESAISIE'],
        'CODECRYPTAGE': CODECRYPTAGE,
        'TYPEOPERATION': 0  # 0 pour insertion
    }

    try:
        # Exécution de la procédure stockée
        cursor = connection
        cursor.execute(
            "EXEC dbo.PC_OPERATEUR ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?",
            list(params.values())
        )
    except Exception as e:
        connection.rollback()
        raise Exception(f"Erreur lors de l'insertion : {str(e.args[1])}")
    
    try:
        # Récupération des informations supplémentaires après insertion
        resultat_operateur = recup_InfoUsercompte(connection, code_aleatoire)
        
        clsAgence = pvgTableLabelAgence(connection, operateur_info['AG_CODEAGENCE'],CODECRYPTAGE)
        
        operateur_info['OP_LOGIN'] = resultat_operateur[0]['OP_LOGIN']
        operateur_info['OP_MOTPASSE'] = resultat_operateur[0]['OP_MOTPASSE']
        
        resultat_operateur[0]['OP_TELEPHONE'] = operateur_info['OP_TELEPHONE']
        resultat_operateur[0]['OP_EMAIL'] = operateur_info['OP_EMAIL']
        resultat_operateur[0]['AG_CODEAGENCE'] = operateur_info['AG_CODEAGENCE']
        
        if resultat_operateur[0]['SL_RESULTAT'] == "TRUE":
            # Validation de la transaction
            get_commit(connection, operateur_info)
            
            # Démarrage d'un traitement asynchrone dans un thread
            thread_traitement = threading.Thread(target=traitement_asynchrone, args=(connection, clsAgence, resultat_operateur))
            thread_traitement.daemon = True
            thread_traitement.start()
        
        return resultat_operateur
    except Exception as e:
        # Gestion des erreurs et rollback
        cursor.execute("ROLLBACK")
        raise Exception(f"Erreur lors de la récupération des résultats : {str(e.args[1])}")
   
    
#mofications
def update_compte_utilisateur(connection, operateur_info):
    params = {
        'OP_CODEOPERATEUR': int(operateur_info['OP_CODEOPERATEUR']),
        'AG_CODEAGENCE': operateur_info['AG_CODEAGENCE'],
        'PO_CODEPROFIL': operateur_info['PO_CODEPROFIL'],
        'SR_CODESERVICE': operateur_info['SR_CODESERVICE'],
        'OP_NOMPRENOM': operateur_info['OP_NOMPRENOM'],
        'OP_TELEPHONE': operateur_info['OP_TELEPHONE'],
        'OP_EMAIL': operateur_info['OP_EMAIL'],
        'OP_LOGIN': operateur_info['OP_LOGIN'],
        'OP_MOTPASSE': operateur_info['OP_MOTPASSE'],
        'OP_URLPHOTO': operateur_info['OP_URLPHOTO'] if 'OP_URLPHOTO' in operateur_info else None,
        'OP_ACTIF': operateur_info['OP_ACTIF'],
        'PL_CODENUMCOMPTECAISSE': operateur_info.get('PL_CODENUMCOMPTECAISSE'),
        'PL_CODENUMCOMPTECOFFRE': operateur_info.get('PL_CODENUMCOMPTECOFFRE'),
        'PL_CODENUMCOMPTEPROVISOIRE': operateur_info.get('PL_CODENUMCOMPTEPROVISOIRE'),
        'PL_CODENUMCOMPTEWAVE': operateur_info.get('PL_CODENUMCOMPTEWAVE'),
        'PL_CODENUMCOMPTEMTN': operateur_info.get('PL_CODENUMCOMPTEMTN'),
        'PL_CODENUMCOMPTEORANGE': operateur_info.get('PL_CODENUMCOMPTEORANGE'),
        'PL_CODENUMCOMPTEMOOV': operateur_info.get('PL_CODENUMCOMPTEMOOV'),
        'PL_CODENUMCOMPTECHEQUE': operateur_info.get('PL_CODENUMCOMPTECHEQUE'),
        'PL_CODENUMCOMPTEVIREMENT': operateur_info.get('PL_CODENUMCOMPTEVIREMENT'),
        'OP_DATESAISIE': operateur_info['OP_DATESAISIE'],
        'CODECRYPTAGE': CODECRYPTAGE,
        'TYPEOPERATION': 1  # 1 pour modification
    }
    

    try:
        cursor = connection
        cursor.execute("EXEC dbo.PC_OPERATEUR ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?", list(params.values()))
        connection.commit()
        get_commit(connection,operateur_info)
        #cursor.close()
    except Exception as e:
        connection.rollback()
        raise Exception(f"Erreur lors de la modification: {str(e.args[1])}")

#suppression
def delete_compte_utilisateur(connection, operateur_info):
    params = {
        'OP_CODEOPERATEUR': operateur_info['OP_CODEOPERATEUR'],
        'AG_CODEAGENCE': operateur_info['AG_CODEAGENCE'],
        'PO_CODEPROFIL':  "",
        'SR_CODESERVICE':  "",
        'OP_NOMPRENOM':  "",
        'OP_TELEPHONE':  "",
        'OP_EMAIL':  "",
        'OP_LOGIN':  "",
        'OP_MOTPASSE':  "",
        'OP_URLPHOTO': None,
        'OP_ACTIF':  "",
        'PL_CODENUMCOMPTECAISSE': "",
        'PL_CODENUMCOMPTECOFFRE':  "",
        'PL_CODENUMCOMPTEPROVISOIRE':  "",
        'PL_CODENUMCOMPTEWAVE': "",
        'PL_CODENUMCOMPTEMTN':  "",
        'PL_CODENUMCOMPTEORANGE':  "",
        'PL_CODENUMCOMPTEMOOV':  "",
        'PL_CODENUMCOMPTECHEQUE':  "",
        'PL_CODENUMCOMPTEVIREMENT':  "",
        'OP_DATESAISIE': parse_datetime('01/01/1900'),
        'CODECRYPTAGE': CODECRYPTAGE,
        'TYPEOPERATION': 2  # 2 pour suppression
    }

    try:
        cursor = connection
        cursor.execute("EXEC dbo.PC_OPERATEUR ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?", list(params.values()))
        connection.commit()
        get_commit(connection,operateur_info)
        #cursor.close()
    except Exception as e:
        connection.rollback()
        raise Exception(f"Erreur lors de la suppression: {str(e.args[1])}")


def Activation_DesActivation_utilisateur(connection, operateur_info):
    params = {
        'OP_CODEOPERATEUR': operateur_info['OP_CODEOPERATEUR'],
        'AG_CODEAGENCE': operateur_info['AG_CODEAGENCE'],
        'PO_CODEPROFIL':  "",
        'SR_CODESERVICE':  "",
        'OP_NOMPRENOM':  "",
        'OP_TELEPHONE':  "",
        'OP_EMAIL':  "",
        'OP_LOGIN':  "",
        'OP_MOTPASSE':  "",
        'OP_URLPHOTO': None,
        'OP_ACTIF':  "",
        'PL_CODENUMCOMPTECAISSE': "",
        'PL_CODENUMCOMPTECOFFRE':  "",
        'PL_CODENUMCOMPTEPROVISOIRE':  "",
        'PL_CODENUMCOMPTEWAVE': "",
        'PL_CODENUMCOMPTEMTN':  "",
        'PL_CODENUMCOMPTEORANGE':  "",
        'PL_CODENUMCOMPTEMOOV':  "",
        'PL_CODENUMCOMPTECHEQUE':  "",
        'PL_CODENUMCOMPTEVIREMENT':  "",
        'OP_DATESAISIE': parse_datetime('01/01/1900'),
        'CODECRYPTAGE': CODECRYPTAGE,
        'TYPEOPERATION': operateur_info['TYPEOPERATION'],  # 2 pour suppression
    }

    try:
        cursor = connection.cursor()
        cursor.execute("EXEC dbo.PC_OPERATEUR ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?", list(params.values()))
        connection.commit()
        get_commit(connection,operateur_info)
        #cursor.close()
    except Exception as e:
        connection.rollback()
        raise Exception(f"Erreur lors de la suppression: {str(e.args[1])}")



def recup_InfoUsercompte(connection,OP_CODEOPERATEUR):
    try:
        cursor = connection
        varreq="SELECT * FROM TEMPCOMPTEUTULISATEURRESULTAT"+OP_CODEOPERATEUR
        # Exécution de la fonction SQL
        cursor.execute(varreq)

        # Récupération des résultats
        rows = cursor.fetchall()
        RetourUsercomptes = []
        # Création d'un dictionnaire pour stocker les données récupérées
        # Traitement des résultats
        for row in rows:
            RetourUsercompte = {}
            RetourUsercompte['OP_LOGIN'] = row.OP_LOGIN
            RetourUsercompte['OP_MOTPASSE'] = row.OP_MOTPASSE
            RetourUsercompte['OP_CODEOPERATEUR'] = row.OP_CODEOPERATEUR
            RetourUsercompte['OP_TELEPHONE'] = ""
            RetourUsercompte['OP_EMAIL'] = ""
            RetourUsercompte['AG_CODEAGENCE'] = ""
            RetourUsercompte['SL_RESULTAT'] = "TRUE"
            RetourUsercomptes.append(RetourUsercompte)
        # Faites ce que vous voulez avec les données récupérées
        return RetourUsercomptes
    except Exception as e:
        MYSQL_REPONSE = str(e.args[1])
        raise Exception(MYSQL_REPONSE)   
    
def pvgTableLabelAgence(connection, *vppCritere):
    cursor = connection

    if len(vppCritere) == 1:
        vapCritere = " WHERE AG_CODEAGENCE=? AND AG_ACTIF='O'"
        vapNomParametre = ('@AG_CODEAGENCE',)
        vapValeurParametre = (vppCritere[0])
    else:
        vapCritere = ""
        vapNomParametre = ()
        vapValeurParametre = ()

    vapRequete = f"""
        SELECT 
            CAST(DECRYPTBYPASSPHRASE('{vppCritere[1]}', AG_EMAIL) AS varchar(150)) AS AG_EMAIL,
            CAST(DECRYPTBYPASSPHRASE('{vppCritere[1]}', AG_EMAILMOTDEPASSE) AS varchar(150)) AS AG_EMAILMOTDEPASSE,
            AG_RAISONSOCIAL
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

        for row in rows:
            clsAgenceObj.AG_EMAIL = row[0]
            clsAgenceObj.AG_EMAILMOTDEPASSE = row[1]
            clsAgenceObj.AG_RAISONSOCIAL = row[2]

        # Retourne l'objet
        return clsAgenceObj
    except Exception as e:
        cursor.close()
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible d\'exécuter la procédure stockée : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)  
    
def traitement_asynchrone(connection, clsAgence, resultatUserCreation):
    try:
        # Votre traitement asynchrone ici
        for idx in range(len(resultatUserCreation)):
            if "@" in resultatUserCreation[idx]['OP_EMAIL']:
                smtpServeur = "smtp.gmail.com"
                portSmtp = 587
                adresseEmail = clsAgence.AG_EMAIL
                motDePasse = clsAgence.AG_EMAILMOTDEPASSE
                destinataire = resultatUserCreation[idx]['OP_EMAIL']#'bolatykouassieuloge@gmail.com'LIENAPPLICATIONCLIENT
                sujet = "Informations de Connexion"
                corpsMessage = (
                        "Bonjour,\n\n"
                        "Votre compte a été créé avec succès. Voici vos informations de connexion :\n\n"
                        "Login : " + resultatUserCreation[idx]['OP_LOGIN'] + "\n"
                        "Mot de passe : " + resultatUserCreation[idx]['OP_MOTPASSE'] + "\n\n"
                        "Vous pouvez vous connecter à l'application en suivant ce lien : " + LIENAPPLICATIONCLIENT + "\n\n"
                        "Veuillez vous connecter et changer votre mot de passe dès que possible pour des raisons de sécurité.\n\n"
                        "Cordialement,\n"
                        "L'équipe de support"
                    )
                message = MIMEMultipart()
                message['From'] = adresseEmail
                message['To'] = destinataire
                message['Subject'] = sujet
                message.attach(MIMEText(corpsMessage, 'plain'))
                with smtplib.SMTP(smtpServeur, portSmtp) as server:
                    server.starttls()
                    server.login(adresseEmail, motDePasse)
                    server.sendmail(adresseEmail, destinataire, message.as_string())
        
        
        # Préparation de l'appel à l'API SMS et mise à jour du SMS
        LIENDAPISMS = LIENAPISMS + "Service/wsApisms.svc/SendMessage"
        Objet ={}
            # Appel de l'API SMS
        if not IsValidateIP(LIENDAPISMS):
                Objet["SL_RESULTAT"] = "FALSE"
                Objet["SL_MESSAGE"] = "L'API SMS doit être configurée !!!"
                
                return Objet
        corpsMessagesms = (
                        "Bonjour,\n\n"
                        "Votre compte a été créé avec succès. Voici vos informations de connexion :\n\n"
                        "Login : " + resultatUserCreation[idx]['OP_LOGIN'] + "\n"
                        "Mot de passe : " + resultatUserCreation[idx]['OP_MOTPASSE'] + "\n\n"
                        "Vous pouvez vous connecter à l'application en suivant ce lien : " + LIENAPPLICATIONCLIENT + "\n\n"
                        "Veuillez vous connecter et changer votre mot de passe dès que possible pour des raisons de sécurité.\n\n"
                        "Cordialement,\n"
                        "L'équipe de support"
                    )
        reponse = excecuteServiceWeb(resultatUserCreation, "post", LIENDAPISMS,corpsMessagesms)
        
        if reponse or len(reponse) == 0:
           connection.close() 
           pass

    except Exception as e:
        connection.close() 
        print("Erreur lors du traitement asynchrone:", e)       


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

def PingHost(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)  # Timeout de 1 seconde
        result = sock.connect_ex((host, port))
        if result == 0:
            return True
        else:
            return False
    except Exception as e:
        print("Erreur lors de la tentative de ping :", e)
        return False



def excecuteServiceWeb(Objetenv, method, url,corpsMessagesms):
    objList = []
    Objet={}
    headers = {'Content-Type': 'application/json'}
    try:
        Objet={
            "Objet": [
                { 
                    "CO_CODECOMPTE": "",
                    "CodeAgence": Objetenv[0]['AG_CODEAGENCE'],
                    "RECIPIENTPHONE": Objetenv[0]['CU_CONTACT'],
                    "SM_RAISONNONENVOISMS": "xxx",
                    "SM_DATEPIECE": "12-05-2022",
                    "LO_LOGICIEL": "01",
                    "OB_NOMOBJET": "test",
                    "SMSTEXT": corpsMessagesms,
                    "INDICATIF": "225",
                    "SM_NUMSEQUENCE": "1",
                    "SM_STATUT": "E"
                }
            ]
        }
        response = requests.request(method, url, json=Objet, headers=headers)
        if response.status_code == 200:
            objList = response.json()
    except requests.exceptions.RequestException as e:
        # Log.Error("Testing log4net error logging - Impossible d'atteindre le service Web")
        pass
    except Exception as ex:
        # Log.Error("Testing log4net error logging - " + str(ex))
        pass
    return objList





    
def get_commit(connection,clsBilletages):
    try:
       for row in clsBilletages: 
        cursor = connection
        params = {
            'AG_CODEAGENCE3': '1000',
            'MC_DATEPIECE3': '01/01/1900'
        }
        try:
            connection.commit()
            cursor.execute("EXECUTE [PC_COMMIT]  ?, ?", list(params.values()))
            #instruction pour valider la commande de mise à jour
            connection.commit()
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


# Fonction pour générer un code aléatoire
def generer_code_aleatoire(taille=10):
    chiffres = string.digits  # Contient uniquement les chiffres de 0 à 9
    return ''.join(random.choice(chiffres) for _ in range(taille))