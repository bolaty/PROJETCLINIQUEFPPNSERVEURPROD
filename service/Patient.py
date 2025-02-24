import sys
sys.path.append("../")
from config import CODECRYPTAGE
import datetime
from datetime import datetime
from tools.toolDate import parse_datetime
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
        

# Liste des Patients
def ListePatient(connexion, Patient_info):
    
     # Préparation des paramètres
    params = {
        'AG_CODEAGENCE': Patient_info['AG_CODEAGENCE'],
        'PT_CODEPATIENT': Patient_info['PT_CODEPATIENT'] or '',
        'PT_MATRICULE': Patient_info['PT_MATRICULE'] or '',
        'PT_NOMPRENOMS': Patient_info['PT_NOMPRENOMS'] or '',
        'DATEDEBUT': datetime.strptime(Patient_info['DATEDEBUT'], "%d/%m/%Y"),
        'DATEFIN': datetime.strptime(Patient_info['DATEFIN'], "%d/%m/%Y"),
        'STAT_CODESTATUT': Patient_info['STAT_CODESTATUT'] or '',
        'PT_CONTACT': Patient_info['PT_CONTACT'],
        'CODECRYPTAGE': CODECRYPTAGE
    }
    
    try:
        cursor = connexion.cursor()
        
        # Exécuter la fonction SQL avec le codecryptage comme paramètre
        #cursor.execute("EXEC FT_PATIENTPARTYPE ?,?,?,?,?,?,?,?,?", list(params.values()))
        cursor.execute("SELECT * FROM dbo.FT_PATIENTPARTYPE(?,?,?,?,?,?,?,?,?)",list(params.values()))
        
        rows = cursor.fetchall()
        results = []
        for row in rows:
            result = {}
            
            result['AG_CODEAGENCE'] = row.AG_CODEAGENCE
            result['PT_IDPATIENT'] = row.PT_IDPATIENT
            result['PT_CODEPATIENT'] = row.PT_CODEPATIENT
            result['PT_MATRICULE'] = row.PT_MATRICULE
            result['PT_CONTACT'] = row.PT_CONTACT
            result['PT_DATESAISIE'] = row.PT_DATESAISIE.strftime("%d/%m/%Y")  # Formatage de la date
            result['PT_NOMPRENOMS'] = row.PT_NOMPRENOMS
            result['PT_EMAIL'] = row.PT_EMAIL 
            result['PT_DATENAISSANCE'] = row.PT_DATENAISSANCE.strftime("%d/%m/%Y")  # Formatage de la date
            result['PT_LIEUHABITATION'] = row.PT_LIEUHABITATION
            result['PT_PROFESSION'] = row.PT_PROFESSION
            result['SX_CODESEXE'] = row.SX_CODESEXE
            result['STAT_CODESTATUT'] = row.STAT_CODESTATUT
            result['STAT_LIBELLE'] = row.STAT_LIBELLE
            result['OP_CODEOPERATEUR'] = row.OP_CODEOPERATEUR
            result['PL_CODENUMCOMPTE'] = row.PL_CODENUMCOMPTE
  
            # Ajouter le dictionnaire à la liste des résultats
            results.append(result)
        
        return results
    except Exception as e:
        # En cas d'erreur, lever une exception avec un message approprié
        raise Exception(f"Erreur lors de la récupération des données: {str(e.args[1])}")   
    
    
    
#creation / modification du patient
def insertpatient(connexion, patient_info):
    params = {
        'PT_IDPATIENT': patient_info.get('PT_IDPATIENT') or None,
        'PT_CODEPATIENT': patient_info.get('PT_CODEPATIENT') or None,
        'PT_MATRICULE': patient_info['PT_MATRICULE'],
        'AG_CODEAGENCE': patient_info['AG_CODEAGENCE'],
        'PT_NOMPRENOMS': patient_info['PT_NOMPRENOMS'],
        'PT_CONTACT': patient_info['PT_CONTACT'],
        'PT_EMAIL': patient_info['PT_EMAIL'],
        'PT_DATENAISSANCE': datetime.strptime(patient_info['PT_DATENAISSANCE'], "%d/%m/%Y"),
        'PT_DATESAISIE': datetime.strptime(patient_info['PT_DATESAISIE'], "%d/%m/%Y"),
        'PT_LIEUHABITATION': patient_info['PT_LIEUHABITATION'],
        'PF_CODEPROFESSION': patient_info.get('PF_CODEPROFESSION') or None,
        'SX_CODESEXE': patient_info['SX_CODESEXE'],
        'STAT_CODESTATUT': patient_info.get('STAT_CODESTATUT') or None,
        'OP_CODEOPERATEUR': patient_info['OP_CODEOPERATEUR'],
        'PL_CODENUMCOMPTE': patient_info.get('PL_CODENUMCOMPTE') or '',
        'CODECRYPTAGE': CODECRYPTAGE,
        'TYPEOPERATION': int(patient_info['TYPEOPERATION']) ,  # 0
    }
    
    try:
        cursor = connexion
        
        try:
            # verifie si le numero de telephone et/ou lemail existe deja. si oui, lever un message d'erreur sinon creer le patient
            cursor.execute("SELECT * FROM dbo.FT_CONTACTEMAILEXIST(?,?,?,?,?,?,?)", (params['AG_CODEAGENCE'], params['PT_CONTACT'], params['PT_EMAIL'], params['PT_CODEPATIENT'], params['PT_MATRICULE'], params['PT_IDPATIENT'], params['CODECRYPTAGE']))
        except Exception as e:
                cursor.rollback()
                raise Exception(f"Erreur lors de l'insertion: {str(e.args[1])}")
            
        # Récupération des résultats
        result = cursor.fetchone()
        if result:
            message = result[0]
            raise Exception(message)
        else:
            try:
                # cursor = cursor.cursor()
                cursor.execute("EXEC dbo.PC_PATIENTSIMPLE ?, ?, ?, ?, ?,?, ?, ?, ?, ?,?, ?, ?, ?, ?,?, ?", list(params.values()))
                cursor.commit()
                
                # Définition de la variable CODECRYPTAGE

                # Requête SQL avec la variable passée comme paramètre
                cursor.execute("""
                    SELECT MAX(PT_IDPATIENT) FROM PATIENT 
                """)
                resultat = cursor.fetchone()[0]
                
                patient_info['PT_IDPATIENT'] = str(resultat)[4:]#resultat
                
                clsAgence = pvgTableLabelAgence(connexion, patient_info['AG_CODEAGENCE'],CODECRYPTAGE)
        
                if clsAgence.AG_EMAIL is not None:
                    # Validation de la transaction
                    get_commit(connexion,patient_info)
                    
                    # Démarrage d'un traitement asynchrone dans un thread
                    thread_traitement = threading.Thread(target=traitement_asynchrone, args=(connexion, clsAgence, patient_info))
                    thread_traitement.daemon = True
                    thread_traitement.start()
                
            except Exception as e:
                cursor.rollback()
                raise Exception(f"Erreur lors de l'insertion: {str(e.args[1])}")
    except Exception as e:
        cursor.rollback()
        # Gérer et formater l'exception correctement
        if len(e.args) == 1:
            raise Exception(f"{e.args[0]}")
        else:
            raise Exception(f"Erreur lors de l'insertion: {e.args[1]}")
        
        
        
#suppression
def deletepatient(connexion, patient_info):
    params = {
        
        'PT_IDPATIENT': patient_info.get('PT_IDPATIENT') or None,
        'PT_CODEPATIENT':  None,
        'PT_MATRICULE': '',
        'AG_CODEAGENCE': '',
        'PT_NOMPRENOMS': '',
        'PT_CONTACT': '',
        'PT_EMAIL': '',
        'PT_DATENAISSANCE': parse_datetime('01/01/1900'),
        'PT_DATESAISIE': parse_datetime('01/01/1900'),
        'PT_LIEUHABITATION': '',
        'PF_CODEPROFESSION':  None,
        'SX_CODESEXE': None,
        'STAT_CODESTATUT':  None,
        'OP_CODEOPERATEUR': '',
        'PL_CODENUMCOMPTE': '',
        'CODECRYPTAGE': CODECRYPTAGE,
        'TYPEOPERATION': 2  # 2 pour suppression
    }

    try:
        cursor = connexion
        cursor.execute("EXEC dbo.PC_PATIENTSIMPLE ?, ?, ?, ?, ?,?, ?, ?, ?, ?,?, ?, ?, ?, ?,?, ?", list(params.values()))
        cursor.commit()
        get_commit(cursor,patient_info)
        #cursor.close()
    except Exception as e:
        cursor.rollback()
        MYSQL_REPONSE = e.args[1]
        if "varchar" in MYSQL_REPONSE:
               MYSQL_REPONSE = MYSQL_REPONSE.split("varchar", 1)[1].split("en type de donn", 1)[0]
               
        raise Exception(MYSQL_REPONSE)            
    
def get_commit(connexion,clsBilletages):
    try:
       for row in clsBilletages: 
        cursor = connexion
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
        if "@" in resultatUserCreation['PT_EMAIL']:
            if "@" in resultatUserCreation['PT_EMAIL']:
                smtpServeur = "smtp.gmail.com"
                portSmtp = 587
                adresseEmail = clsAgence.AG_EMAIL
                motDePasse = clsAgence.AG_EMAILMOTDEPASSE
                destinataire = resultatUserCreation['PT_EMAIL']#'bolatykouassieuloge@gmail.com'LIENAPPLICATIONCLIENT
                sujet = "Informations de Connexion"
                corpsMessage = (
                    "Bienvenue au C M P  \n\n"
                    "Votre dossier vient d'être créé.\n"
                    "Numéro dossier : " + resultatUserCreation['PT_IDPATIENT'] + "\n\n"
                    "La clinique C M P vous souhaite un prompt rétablissement !"
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
                    "Bienvenue au C M P  \n\n"
                    "Votre dossier vient d'être créé.\n"
                    "Numéro dossier : " + resultatUserCreation['PT_IDPATIENT'] + "\n\n"
                    "La clinique C M P vous souhaite un prompt rétablissement !"
                )
        reponse = excecuteServiceWeb(resultatUserCreation, "post", LIENDAPISMS,corpsMessagesms)
        
        if reponse or len(reponse) == 0:
           #connection.close() 
           pass

    except Exception as e:
        #connection.close() 
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
                    "CodeAgence": Objetenv['AG_CODEAGENCE'],
                    "RECIPIENTPHONE": Objetenv['PT_CONTACT'],
                    "SM_RAISONNONENVOISMS": "xxx",
                    "SM_DATEPIECE": "14-01-2025",
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
    