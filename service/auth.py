import requests
from config import CODECRYPTAGE,LIENAPISMS
from tools.toolTestDeConnexion import  PingHost
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
import random
import string

class clsAgence:
    def __init__(self):
        self.AG_RAISONSOCIAL = ''
        self.AG_EMAILMOTDEPASSE = ''
        self.AG_EMAIL = ''


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
            clsUserConnect['AG_CODEAGENCE'] = int(row.AG_CODEAGENCE)
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
            clsUserConnect['EX_EXERCICE'] = row.EX_EXERCICE
            clsUserConnect['EX_DATEDEBUTPREMIEREXERCIE'] = row.EX_DATEDEBUTPREMIEREXERCIE.strftime("%d/%m/%Y")
            clsUserConnect['JT_DATEJOURNEETRAVAIL'] = row.JT_DATEJOURNEETRAVAIL.strftime("%d/%m/%Y")
            if row.EX_DATEDEBUT is not None:
              clsUserConnect['EX_DATEDEBUT'] = row.EX_DATEDEBUT.strftime("%d/%m/%Y")
            else:
              clsUserConnect['EX_DATEDEBUT'] = row.EX_DATEDEBUT    
            if row.EX_DATEFIN is not None:  
              clsUserConnect['EX_DATEFIN'] = row.EX_DATEFIN.strftime("%d/%m/%Y")
            else:
              clsUserConnect['EX_DATEFIN'] = row.EX_DATEDEBUT  
            clsUserConnect['SR_CODESERVICE'] = row.SR_CODESERVICE
            clsUserConnect['PO_LIBELLEPROFIL'] = row.PO_LIBELLEPROFIL
            clsUserConnect['PO_CODEPROFIL'] = row.PO_CODEPROFIL
            clsUserConnect['SO_CODESOCIETE'] = row.SO_CODESOCIETE
            clsUserConnect['AG_BOITEPOSTAL'] = row.AG_BOITEPOSTAL
            RetourUserConnect.append(clsUserConnect)
        # Faites ce que vous voulez avec les données récupérées
        return RetourUserConnect
    except Exception as e:
         # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible de récupérer les résultats de la procédure stockée : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)
    


def pvgUserChangePasswordfist(connection, UserChangePasswordfist):
    # Préparation des paramètres
    params = {
        'PO_CODEPROFIL': UserChangePasswordfist['PO_CODEPROFIL'],
        'OP_MOTPASSEOLD': UserChangePasswordfist['OP_MOTPASSEOLD'],
        'OP_LOGINOLD': UserChangePasswordfist['OP_LOGINOLD'],
        'OP_MOTPASSENEW': UserChangePasswordfist['OP_MOTPASSENEW'],
        'OP_LOGINNEW': UserChangePasswordfist['OP_LOGINNEW'],
        'CODECRYPTAGE':CODECRYPTAGE # UserChangePasswordfist['CODECRYPTAGE']
    }

    # Exécution de la procédure stockée
    try:
        cursor = connection
    except Exception as e:
        cursor.close()
         # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible de récupérer le curseur de la base de données : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)

    # Exécution de la procédure stockée
    try:
        cursor.execute("EXEC PS_USERUPDATELOGINPASSWORDFIRSTCONNEXION ?, ?, ?, ?, ?, ?", list(params.values()))
        #instruction pour valider la commande de mise à jour
        cursor.commit()
    except Exception as e:
        cursor.close()
        # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = str(e.args[1])
        raise Exception(MYSQL_REPONSE)
      
    # Récupération des résultats
    try:
       
        resultatUserforgot = recup_InfoChangePassword(connection,UserChangePasswordfist['OP_MOTPASSENEW'])
        
        
        return resultatUserforgot    
    except Exception as e:
         # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible de récupérer les résultats de la procédure stockée : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)

def recup_InfoChangePassword(connection,OP_MOTPASSENEW):
    try:
        cursor = connection
        varreq="SELECT * FROM TEMPUSERCHANGEPASSWORDRESULTAT"+OP_MOTPASSENEW
        # Exécution de la fonction SQL
        cursor.execute(varreq)

        # Récupération des résultats
        rows = cursor.fetchall()
        RetourUserChangePasswordConnects = []
        # Création d'un dictionnaire pour stocker les données récupérées
        # Traitement des résultats
        for row in rows:
            RetourUserChangePasswordConnect = {}
            RetourUserChangePasswordConnect['SL_RESULTAT'] = row.SL_RESULTAT
            RetourUserChangePasswordConnect['SL_CODEMESSAGE'] = row.SL_CODEMESSAGE
            RetourUserChangePasswordConnect['SL_MESSAGE'] = row.SL_MESSAGE   


            RetourUserChangePasswordConnects.append(RetourUserChangePasswordConnect)
        # Faites ce que vous voulez avec les données récupérées
        return RetourUserChangePasswordConnects
    except Exception as e:
        MYSQL_REPONSE = str(e.args[1])
        raise Exception(MYSQL_REPONSE)    
 
 
    
def pvgUserDemandePassword(connection, clsInfoUsersconnect):
    code_aleatoire = generer_code_aleatoire()
    # Préparation des paramètres
    params = {
        'CODE_ALEATOIRE': code_aleatoire,
        'OP_TELEPHONE': clsInfoUsersconnect['OP_TELEPHONE'],
        'OP_LOGIN': clsInfoUsersconnect['OP_LOGIN'],
        #'TYPEOPERATION': clsInfoUsersconnect['TYPEOPERATION'],
        'CODECRYPTAGE': CODECRYPTAGE #clsInfoUsersconnect['CODECRYPTAGE']
    }

    # Exécution de la procédure stockée
    try:
        cursor = connection
    except Exception as e:
        cursor.close()
         # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible de récupérer le curseur de la base de données : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)

    # Exécution de la procédure stockée
    try:
        cursor.execute("EXEC PS_MOBILEDEMANDEMOTDEPASSE  ?, ?, ?, ?", list(params.values()))
        #instruction pour valider la commande de mise à jour
        #connection.commit()
    except Exception as e:
        cursor.close()
        # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = str(e.args[1])
        raise Exception(MYSQL_REPONSE)
      
    # Récupération des résultats
    try:
       
        resultatUserforgot = recup_InfoUserforgot(connection,code_aleatoire)
        
        clsAgence = pvgTableLabelAgence(connection, resultatUserforgot[0]['AG_CODEAGENCE'],CODECRYPTAGE)
        
        # Démarrer le traitement asynchrone dans un thread
        if resultatUserforgot[0]['SL_RESULTAT'] == "TRUE"  :
            if "@" in clsInfoUsersconnect['OP_TELEPHONE']:
                thread_traitement = threading.Thread(target=traitement_asynchrone, args=(connection, clsAgence, resultatUserforgot))
                thread_traitement.daemon = True  # Définir le thread comme démon
                thread_traitement.start()
            else :
                thread_traitement = threading.Thread(target=traitement_asynchroneSMS, args=(connection, clsAgence, resultatUserforgot))
                thread_traitement.daemon = True  # Définir le thread comme démon
                thread_traitement.start()
                
        return resultatUserforgot    
    except Exception as e:
         # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible de récupérer les résultats de la procédure stockée : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)

def recup_InfoUserforgot(connection,OP_TELEPHONE):
    try:
        cursor = connection
        varreq="SELECT * FROM TEMPUSERFOTGOTPASSWORDRESULTAT"+OP_TELEPHONE
        # Exécution de la fonction SQL
        cursor.execute(varreq)

        # Récupération des résultats
        rows = cursor.fetchall()
        RetourUserforgotConnects = []
        # Création d'un dictionnaire pour stocker les données récupérées
        # Traitement des résultats
        for row in rows:
            RetourUserforgotConnect = {}
            RetourUserforgotConnect['AG_CODEAGENCE'] = row.AG_CODEAGENCE
            RetourUserforgotConnect['MO_DATE'] = row.MO_DATE
            if row.MO_DATE is not None:  
              RetourUserforgotConnect['MO_DATE'] = row.MO_DATE.strftime("%d/%m/%Y")
            else:
              RetourUserforgotConnect['MO_DATE'] = row.MO_DATE
            RetourUserforgotConnect['MO_NUMEROSEQUENCE'] = row.MO_NUMEROSEQUENCE
            RetourUserforgotConnect['OP_CODEOPERATEUR'] = row.OP_CODEOPERATEUR
            RetourUserforgotConnect['OP_TELEPHONE'] = row.OP_TELEPHONE
            RetourUserforgotConnect['OP_EMAIL'] = row.OP_EMAIL
            RetourUserforgotConnect['MO_HEURE'] = row.MO_HEURE
            RetourUserforgotConnect['OP_LOGIN'] = row.OP_LOGIN
            RetourUserforgotConnect['OP_MOTPASSE'] = row.OP_MOTPASSE
            
            if row.MO_DATEVALIDATION is not None:  
              RetourUserforgotConnect['MO_DATEVALIDATION'] = row.MO_DATEVALIDATION.strftime("%d/%m/%Y")
            else:
              RetourUserforgotConnect['MO_DATEVALIDATION'] = row.MO_DATEVALIDATION
            
            RetourUserforgotConnect['SL_RESULTAT'] = row.SL_RESULTAT
            RetourUserforgotConnect['SL_CODEMESSAGE'] = row.SL_CODEMESSAGE
            RetourUserforgotConnect['SL_MESSAGE'] = row.SL_MESSAGE   


            RetourUserforgotConnects.append(RetourUserforgotConnect)
        # Faites ce que vous voulez avec les données récupérées
        return RetourUserforgotConnects
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
    
def traitement_asynchrone(connection, clsAgence, resultatUserforgot):
    try:
        # Votre traitement asynchrone ici
        for idx in range(len(resultatUserforgot)):
            if "@" in resultatUserforgot[idx]['OP_EMAIL']:
                smtpServeur = "smtp.gmail.com"
                portSmtp = 587
                adresseEmail = clsAgence.AG_EMAIL
                motDePasse = clsAgence.AG_EMAILMOTDEPASSE
                destinataire = resultatUserforgot[idx]['OP_EMAIL']#'bolatykouassieuloge@gmail.com'
                sujet = "Mot de Passe"
                corpsMessage = "Votre mot de passe est : " + resultatUserforgot[idx]['OP_MOTPASSE']
                message = MIMEMultipart()
                message['From'] = adresseEmail
                message['To'] = destinataire
                message['Subject'] = sujet
                message.attach(MIMEText(corpsMessage, 'plain'))
                with smtplib.SMTP(smtpServeur, portSmtp) as server:
                    server.starttls()
                    server.login(adresseEmail, motDePasse)
                    server.sendmail(adresseEmail, destinataire, message.as_string())
        
        connection.close() 
        pass

    except Exception as e:
        connection.close() 
        print("Erreur lors du traitement asynchrone:", e)       
 
def traitement_asynchroneSMS(connection, clsAgence, resultatUserforgot):
    try:
        # Votre traitement asynchrone ici
        # Préparation de l'appel à l'API SMS et mise à jour du SMS
        LIENDAPISMS = LIENAPISMS + "Service/wsApisms.svc/SendMessage"
        # Appel de l'API SMS
        

        if not IsValidateIP(LIENDAPISMS):
            Objet={}
        else:
            Objet={}
            headers = {'Content-Type': 'application/json'}
            
            Objet={
                    "Objet": [
                        { 
                            "CO_CODECOMPTE": "",
                            "CodeAgence": resultatUserforgot[0]['AG_CODEAGENCE'],
                            "RECIPIENTPHONE": resultatUserforgot[0]['OP_TELEPHONE'],
                            "SM_RAISONNONENVOISMS": "xxx",
                            "SM_DATEPIECE": "12-05-2022",
                            "LO_LOGICIEL": "01",
                            "OB_NOMOBJET": "test",
                            "SMSTEXT": "Votre mot de passe est : " + resultatUserforgot[0]['OP_MOTPASSE'],
                            "INDICATIF": "225",
                            "SM_NUMSEQUENCE": "1",
                            "SM_STATUT": "E"
                        }
                    ]
            }
            response = requests.request("post", LIENDAPISMS, json=Objet, headers=headers)
            if response.status_code == 200:
                    objList = response.json()
            connection.close() 
                

    except Exception as e:
        connection.close() 
        print("Erreur lors du traitement asynchrone:", e)             
        
# Fonction pour générer un code aléatoire
def generer_code_aleatoire(taille=10):
    lettres_chiffres = string.ascii_uppercase + string.digits
    return ''.join(random.choice(lettres_chiffres) for _ in range(taille))       



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
