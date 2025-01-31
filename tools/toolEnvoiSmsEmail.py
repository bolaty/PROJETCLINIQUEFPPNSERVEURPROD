from typing import List
from config import MYSQL_REPONSE, LIENAPISMS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from tools.toolTestDeConnexion import PingHost



class clsAgence:
    def __init__(self):
        self.SO_CODESOCIETE = ''
        self.AG_AGENCECODE = ''
        self.VL_CODEVILLE = ''
        self.AG_RAISONSOCIAL = ''
        self.AG_BOITEPOSTAL = ''
        self.AG_ADRESSEGEOGRAPHIQUE = ''
        self.AG_TELEPHONE = ''
        self.AG_FAX = ''
        self.AG_EMAIL = ''
        self.AG_NUMEROAGREMENT = ''
        self.AG_REFERENCE = ''
        self.AG_DATECREATION = ''
        self.AG_ACTIF = ''
        self.OP_CODEOPERATEUR = ''
        
class clsParams:
    def __init__(self):
        self.LibelleMouchard = ""
        self.LibelleEcran = ""
        self.LG_CODELANGUE = "FR"
        self.SL_LIBELLE1 = ""
        self.SL_LIBELLE2 = ""
        self.CO_CODECOMPTE = ""
        self.LO_LOGICIEL = "1"
        self.OB_NOMOBJET = ""
        self.SL_VALEURRETOURS = ""
        self.INDICATIF = ""
        self.RECIPIENTPHONE = ""
        self.PV_CODEPOINTVENTE = ""
        self.CodeOperateur = ""
        self.SM_DATEPIECE = ""
        self.SM_RAISONNONENVOISMS = ""
        self.TYPEOPERATION = ""
        self.SMSTEXT = ""
        self.MB_IDTIERS = ""
        self.EJ_IDEPARGNANTJOURNALIER = ""
        self.CL_IDCLIENT = ""
        self.TE_CODESMSTYPEOPERATION = ""
        self.SM_NUMSEQUENCE = ""
        self.SM_DATEEMISSIONSMS = ""
        self.MC_NUMPIECE = ""
        self.MC_NUMSEQUENCE = ""
        self.SM_STATUT = ""
        self.SM_NUMSEQUENCE = ""
        self.SMSTEXT = ""
        self.RECIPIENTPHONE = ""
        self.SL_CODEMESSAGE = ""
        self.SL_MESSAGE = ""
        self.SL_RESULTAT = ""
        self.CodeAgence = ""
        
          


def envoi_sms_reedition(connexion, objet_envoi, resultat):
    try:
        LIENDAPISMS = LIENAPISMS + "Service/wsApisms.svc/SendMessage"

        if not IsValidateIP(LIENDAPISMS):
            Objet={}
        else:
            Objet={}
            headers = {'Content-Type': 'application/json'}
            
            Objet={
                    "Objet": [
                        { 
                            "CO_CODECOMPTE": "",
                            "CodeAgence": objet_envoi['AG_CODEAGENCE'],
                            "RECIPIENTPHONE": objet_envoi['CONTACT_DESTI'],
                            "SM_RAISONNONENVOISMS": "xxx",
                            "SM_DATEPIECE": objet_envoi['MC_DATEPIECE'],
                            "LO_LOGICIEL": "01",
                            "OB_NOMOBJET": "test",
                            "SMSTEXT": "",
                            "INDICATIF": "225",
                            "SM_NUMSEQUENCE": "1",
                            "SM_STATUT": "E"
                        }
                    ]
            }
            
            # Construction du message
            Objet['Objet'][0]['SMSTEXT'] = f"""
Bonjour,
De la clinique du FPPN.\n
Ref. pièce: {resultat[0]['MC_REFERENCEPIECE']}
Nom du bénéficiaire ou l'assuré: {resultat[0]['MC_NOMTIERS']}
Nom du tireur: {resultat[0]['OP_NOMPRENOM']}
            """
            
            total_facture = 0
            for operation in resultat:
                if operation['MR_CODEMODEREGLEMENT'] != '008':
                    montant_int = int(operation['MC_MONTANTCREDIT'])
                    Objet['Objet'][0]['SMSTEXT'] += f"\tMode de règlement: {operation['MR_LIBELLE']} | Libellé de l'opération: {operation['MC_LIBELLEOPERATION']} | Montant: {montant_int}\n"
                    total_facture += int(operation['MC_MONTANTCREDIT'])

            Objet['Objet'][0]['SMSTEXT'] += f"""
Total facture:  {total_facture} F CFA\n
            """
            
            Objet['Objet'][0]['SMSTEXT'] += """
Cordialement,
L'équipe
            """
            
            response = requests.request("post", LIENDAPISMS, json=Objet, headers=headers)
            if response.status_code == 200:
                    objList = response.json()
            connexion.close()
    except Exception as e:
        connexion.close() 
        print("Erreur lors du traitement asynchrone:", e)
        
        
        
def envoi_email_reedition(connexion, objet_envoi, resultat):
    try:
        smtpServeur = "smtp.gmail.com"
        portSmtp = 587
        adresseEmail = resultat[0]['AG_EMAIL']
        motDePasse = resultat[0]['AG_EMAILMOTDEPASSE']
        destinataire = objet_envoi['EMAIL_DESTI']
        sujet = "Reçu de caisse"
        corpsMessage = ""
        message = MIMEMultipart()
        message['From'] = adresseEmail
        message['To'] = destinataire
        message['Subject'] = sujet
        
        # Construction du message
        corpsMessage = f"""
            Bonjour,
            De la clinique du FPPN. \n
            Ref. pièce: {resultat[0]['MC_REFERENCEPIECE']}
            Nom du bénéficiaire ou l'assuré: {resultat[0]['MC_NOMTIERS']}
            Nom du tireur: {resultat[0]['OP_NOMPRENOM']}
        """
        
        total_facture = 0
        for operation in resultat:
            if operation['MR_CODEMODEREGLEMENT'] != '008':
                montant_int = int(operation['MC_MONTANTCREDIT'])
                corpsMessage += f"    Mode de règlement: {operation['MR_LIBELLE']} | Libellé de l'opération: {operation['MC_LIBELLEOPERATION']} | Montant: {montant_int}\n"
                total_facture += int(operation['MC_MONTANTCREDIT'])
            
        corpsMessage += f"""
            Total facture:  {total_facture} F CFA\n
        """
        corpsMessage += """
            Cordialement,
            L'équipe
        """

        message.attach(MIMEText(corpsMessage, 'plain'))
        with smtplib.SMTP(smtpServeur, portSmtp) as server:
            server.starttls()
            server.login(adresseEmail, motDePasse)
            server.sendmail(adresseEmail, destinataire, message.as_string())
        connexion.close() 
    except Exception as e:
        connexion.close() 
        print("Erreur lors du traitement asynchrone:", e)
        

        
def traitement_asynchrone(connexion, clsMouvementcomptable, listOperation):
    try:
        # Votre traitement asynchrone ici
        for idx in range(len(listOperation)):
            if "@" in listOperation[idx]['EJ_EMAILCLIENT']:
                smtpServeur = "smtp.gmail.com"
                portSmtp = 587
                adresseEmail = listOperation[idx]['AG_EMAIL']
                motDePasse = listOperation[idx]['AG_EMAILMOTDEPASSE']
                destinataire = listOperation[idx]['EJ_EMAILCLIENT']#'bolatykouassieuloge@gmail.com'
                sujet = "Code Validation"
                corpsMessage = listOperation[idx]['SL_MESSAGECLIENT']
                message = MIMEMultipart()
                message['From'] = adresseEmail
                message['To'] = destinataire
                message['Subject'] = sujet
                message.attach(MIMEText(corpsMessage, 'plain'))
                with smtplib.SMTP(smtpServeur, portSmtp) as server:
                    server.starttls()
                    server.login(adresseEmail, motDePasse)
                    server.sendmail(adresseEmail, destinataire, message.as_string())
        
        for idx in range(len(listOperation)):
            """
            AG_CODEAGENCE = clsMouvementcomptable['AG_CODEAGENCE']
            vlpEnvoyerSms = pvgDecisionEnvoiSMS(connexion, AG_CODEAGENCE)
            if vlpEnvoyerSms:
                clsParametreAppelApi = {}
                clsParametreAppelApi['AG_CODEAGENCE'] = clsMouvementcomptable['AG_CODEAGENCE']
                clsParametreAppelApi['CL_CONTACT'] = listOperation[idx]["EJ_TELEPHONE"]
                clsParametreAppelApi['OP_CODEOPERATEUR'] = clsMouvementcomptable['OP_CODEOPERATEUR']
                clsParametreAppelApi['SM_DATEPIECE'] = clsMouvementcomptable['MC_DATEPIECE']
                clsParametreAppelApi['SL_MESSAGECLIENT'] = listOperation[idx]["SL_MESSAGECLIENT"]
                #clsParametreAppelApi['SM_NUMSEQUENCE'] = listOperation[idx]["SM_NUMSEQUENCERETOURS"]
                #clsParametreAppelApi['AG_EMAIL'] = listOperation[idx]["AG_EMAIL"]
                #clsParametreAppelApi['AG_EMAILMOTDEPASSE'] = listOperation[idx]["AG_EMAILMOTDEPASSE"]
                #clsParametreAppelApi['SL_MESSAGEOBJET'] = listOperation[idx]["SL_MESSAGEOBJET"]
                #clsParametreAppelApi['EJ_EMAILCLIENT'] = listOperation[idx]["EJ_EMAILCLIENT"]
                clsParametreAppelApi['SL_LIBELLE1'] = ""
                #clsParametreAppelApi['SL_LIBELLE2'] = ""
                clsParametreAppelApis = [clsParametreAppelApi]

                TE_CODESMSTYPEOPERATION = "0005"
                SL_LIBELLE1 = "C"
                clsParametreAppelApi['SL_LIBELLE1'] = SL_LIBELLE1
                #AG_CODEAGENCE, SM_TELEPHONE, OP_CODEOPERATEUR, SM_DATEPIECE, SMSTEXT, TE_CODESMSTYPEOPERATION,
                # SM_NUMSEQUENCE, SM_DATEEMISSIONSMS,  SM_STATUT, TYPEOPERATION, SL_LIBELLE2
                clsParams = pvgTraitementSms(
                    connexion,
                    clsParametreAppelApi['AG_CODEAGENCE'],
                    clsParametreAppelApi['CL_CONTACT'],#"2250788635251"
                    clsParametreAppelApi['OP_CODEOPERATEUR'],
                    clsParametreAppelApi['SM_DATEPIECE'],
                    clsParametreAppelApi['SL_MESSAGECLIENT'],
                    TE_CODESMSTYPEOPERATION,
                    "0",
                    "01/01/1900",
                    "N",
                    "0",
                    clsParametreAppelApi['SL_LIBELLE1']
                )

                clsParametreAppelApis[0]['SL_RESULTATAPI'] = clsParams['SL_RESULTAT']
                clsParametreAppelApis[0]['SL_MESSAGEAPI'] = clsParams['SL_MESSAGE']
                if clsParams['SL_RESULTAT'] == "FALSE":
                    clsParametreAppelApis[0]['SL_MESSAGE'] = clsParametreAppelApis[0]['SL_MESSAGE'] + " " + clsParametreAppelApis[0]['SL_MESSAGEAPI']
                if clsParams['SL_RESULTAT'] == "TRUE":
                    clsParametreAppelApis[0]['SL_MESSAGEAPI'] = ""
            """
            # Préparation de l'appel à l'API SMS et mise à jour du SMS
            LIENDAPISMS = LIENAPISMS + "Service/wsApisms.svc/SendMessage"
            Objet ={}
                # Appel de l'API SMS
            if not IsValidateIP(LIENDAPISMS):
                    Objet["SL_RESULTAT"] = "FALSE"
                    Objet["SL_MESSAGE"] = "L'API SMS doit être configurée !!!"
                    
                    return Objet
            
            reponse = excecuteServiceWebNew(listOperation[idx], "post", LIENDAPISMS,listOperation[idx]["SL_MESSAGECLIENT"])
            
        if reponse or len(reponse) == 0:
            
            pass
        #connexion.close() 
        #pass

    except Exception as e:
        #connexion.close() 
        print("Erreur lors du traitement asynchrone:", e)

def excecuteServiceWebNew(Objetenv, method, url,corpsMessagesms):
    objList = []
    Objet={}
    headers = {'Content-Type': 'application/json'}
    try:
        Objet={
            "Objet": [
                { 
                    "CO_CODECOMPTE": "",
                    "CodeAgence": Objetenv['AG_CODEAGENCE'],
                    "RECIPIENTPHONE": Objetenv['EJ_TELEPHONE'],
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

def pvgDecisionEnvoiSMS(connexion, *vppCritere):
    # Appeler la fonction pvgTableLabel avec le paramètre AG_CODEAGENCE et récupérer la réponse dans l'objet clsAgence
    clsAgence = pvgTableLabelAgence(connexion, *vppCritere)
    # Vérifier si la première instruction s'est terminée avec succès
    vlpEnvoyerSms = False
    if clsAgence:
        # Appeler à nouveau la fonction pvgTableLabel avec le paramètre clsAgence.SO_CODESOCIETE et "ENVS" et récupérer la réponse dans l'objet clsParametre
        clsParametre = pvgTableLabel(connexion, clsAgence.SO_CODESOCIETE, "ENVS")

        # Appliquer la logique en Python
        
        #if clsParametre is not None:
        #    if clsParametre['PP_VALEUR'] in ["2", "3"]:
        #        vlpEnvoyerSms = True

    # Retourner vlpEnvoyerSms
    return True #vlpEnvoyerSms



def pvgTableLabel(connexion, *vppCritere):
    cursor = connexion

    if len(vppCritere) == 2:
        vapCritere = " WHERE SO_CODESOCIETE=? AND PP_CODEPARAMETRE=?"
        vapNomParametre = ('@SO_CODESOCIETE','PP_CODEPARAMETRE')
        vapValeurParametre = (vppCritere[0],vppCritere[1])
    else:
        vapCritere = ""
        vapNomParametre = ()
        vapValeurParametre = ()

    vapRequete = f"SELECT PP_LIBELLE,PP_BORNEMIN,PP_BORNEMAX,PP_MONTANTMINI,PP_MONTANTMAXI,PP_TAUX,PP_MONTANT,PP_VALEUR,PL_CODENUMCOMPTE,PP_AFFICHER FROM PARAMETRE {vapCritere}"
    try:
        cursor.execute(vapRequete, vapValeurParametre)
    except Exception as e:
        cursor.close()
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible d\'exécuter la procédure stockée : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)
    
    try:
        rows = cursor.fetchall()

        cls_parametre =  {}

        for row in rows:
            cls_parametre['PP_LIBELLE'] = str(row[0])
            cls_parametre['PP_BORNEMIN'] = float(row[1])
            cls_parametre['PP_BORNEMAX'] = float(row[2])
            cls_parametre['PP_MONTANTMINI'] = float(row[3])
            cls_parametre['PP_MONTANTMAXI'] = float(row[4])
            cls_parametre['PP_TAUX'] = str(row[5])
            cls_parametre['PP_MONTANT'] = float(row[6])
            cls_parametre['PP_VALEUR'] = str(row[7])
            cls_parametre['PL_CODENUMCOMPTE'] = str(row[8])
            cls_parametre['PP_AFFICHER'] = str(row[9])

        # Retourne l'objet
        return cls_parametre
    except Exception as e:
        cursor.close()
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible d\'exécuter la procédure stockée : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)
    
    

def pvgTableLabelAgence(connexion, *vppCritere):
    cursor = connexion

    if len(vppCritere) == 1:
        vapCritere = " WHERE AG_CODEAGENCE=? AND AG_ACTIF='O'"
        vapNomParametre = ('@AG_CODEAGENCE',)
        vapValeurParametre = (vppCritere[0],)
    else:
        vapCritere = ""
        vapNomParametre = ()
        vapValeurParametre = ()

    vapRequete = f"SELECT SO_CODESOCIETE, AG_AGENCECODE, VL_CODEVILLE, AG_RAISONSOCIAL,AG_ADRESSEGEOGRAPHIQUE, AG_BOITEPOSTAL, AG_TELEPHONE, AG_FAX, AG_EMAIL,AG_ACTIF FROM AGENCE {vapCritere}"
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
            clsAgenceObj.SO_CODESOCIETE = row[0]
            clsAgenceObj.AG_AGENCECODE = row[1]
            clsAgenceObj.VL_CODEVILLE = row[2]
            clsAgenceObj.AG_RAISONSOCIAL = row[3]
            clsAgenceObj.AG_BOITEPOSTAL = row[4]
            clsAgenceObj.AG_ADRESSEGEOGRAPHIQUE = row[5]
            clsAgenceObj.AG_TELEPHONE = row[6]
            clsAgenceObj.AG_FAX = row[7]
            clsAgenceObj.AG_EMAIL = row[8]
            clsAgenceObj.AG_ACTIF = row[9]

        # Retourne l'objet
        return clsAgenceObj
    except Exception as e:
        cursor.close()
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible d\'exécuter la procédure stockée : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)



def pvgTraitementSms(clsDonnee, AG_CODEAGENCE, SM_TELEPHONE, OP_CODEOPERATEUR, SM_DATEPIECE, SMSTEXT, TE_CODESMSTYPEOPERATION, SM_NUMSEQUENCE, SM_DATEEMISSIONSMS,  SM_STATUT, TYPEOPERATION, SL_LIBELLE2):
    # Processus d'envoi du SMS
    clsParams = {}  # BOJ modèle de retour
    clsParamss = []  # Liste BOJ selon modèle retourné
    Objet = []  # BOJ ou liste BOJ envoyée
    #clsSmsoutWSDAL = clsSmsoutWSDAL()  # Remplacez clsSmsoutWSDAL par la classe réelle
    #date_piece_str = SM_DATEPIECE
    #date_piece = datetime.strptime(date_piece_str, "%d/%m/%Y")
    #SM_DATEPIECE = date_piece
    
    
    #date_piece_str1 = SM_DATEEMISSIONSMS
    #date_piece1 = datetime.strptime(date_piece_str1, "%d/%m/%Y")
    #SM_DATEEMISSIONSMS = date_piece1
    # Préparation de l'envoi du SMS
    Objet = pvpPreparationSms(clsDonnee, AG_CODEAGENCE, SM_TELEPHONE, OP_CODEOPERATEUR, SM_DATEPIECE, SMSTEXT, TE_CODESMSTYPEOPERATION, SM_NUMSEQUENCE, SM_DATEEMISSIONSMS, SM_STATUT, TYPEOPERATION, SL_LIBELLE2)
    if Objet:    
        try:
            # Préparation de l'appel à l'API SMS et mise à jour du SMS
            LIENDAPISMS = LIENAPISMS + "Service/wsApisms.svc/SendMessage"
            # Appel de l'API SMS
            if Objet[0]["SL_RESULTAT"] != "TRUE":
                return Objet[0]

            if not IsValidateIP(LIENDAPISMS):
                Objet[0]["SL_RESULTAT"] = "FALSE"
                Objet[0]["SL_MESSAGE"] = "L'API SMS doit être configurée !!!"
                #pvgMobileSmsUpdateStatut(clsDonnee, AG_CODEAGENCE, SM_DATEPIECE, SM_DATEPIECE, Objet[0]["SM_NUMSEQUENCE"], "N", "L'API SMS doit être configurée !!!",OP_CODEOPERATEUR)
                return Objet[0]
            Objet[0]['SM_DATEPIECE'] = SM_DATEPIECE#date_piece_str
            Objet[0]['SM_DATEEMISSIONSMS'] = SM_DATEEMISSIONSMS#date_piece_str1
            Objet[0]['RECIPIENTPHONE'] = SM_TELEPHONE #'2250788635251'
            Objet[0]['CL_IDCLIENT'] = ""
            Objet[0]['MC_NUMSEQUENCE'] = ""
            clsParams = excecuteServiceWeb(clsParams, Objet, "post", LIENDAPISMS)

            if clsParams:
                # Mise à jour du statut du SMS
                if clsParams[0]["SL_RESULTAT"] == "TRUE":
                    pvgMobileSmsUpdateStatut(clsDonnee, AG_CODEAGENCE, SM_DATEPIECE, SM_DATEPIECE, Objet[0]["SM_NUMSEQUENCE"], "E", "OK",OP_CODEOPERATEUR)
                elif clsParams[0]["SL_RESULTAT"] == "FALSE":
                    pvgMobileSmsUpdateStatut(clsDonnee, AG_CODEAGENCE, SM_DATEPIECE, SM_DATEPIECE, Objet[0]["SM_NUMSEQUENCE"], "N", clsParams[0]["SL_MESSAGE"],OP_CODEOPERATEUR)
                    Objet[0]["SL_RESULTAT"] = clsParams[0]["SL_RESULTAT"]
                    Objet[0]["SL_MESSAGE"] = clsParams[0]["SL_MESSAGE"]
        except requests.exceptions.RequestException as e:
            Objet[0]["SL_RESULTAT"] = "FALSE"
            Objet[0]["SL_MESSAGE"] = str(e)
            pvgMobileSmsUpdateStatut(clsDonnee, AG_CODEAGENCE, SM_DATEPIECE, SM_DATEPIECE, Objet[0]["SM_NUMSEQUENCE"], "N", str(e),OP_CODEOPERATEUR)
        except Exception as ex:
            clsParams = {
                "SL_RESULTAT": "FALSE",
                "SL_MESSAGE": str(ex)
            }
            clsParamss.append(clsParams)
            pvgMobileSmsUpdateStatut(clsDonnee, AG_CODEAGENCE, SM_DATEPIECE, SM_DATEPIECE, Objet[0]["SM_NUMSEQUENCE"], "N", str(ex),OP_CODEOPERATEUR)

    return Objet[0]



def excecuteServiceWeb(data, Objetenv, method, url):
    objList = []
    Objet={}
    headers = {'Content-Type': 'application/json'}
    try:
        Objet={
            "Objet": [
                { 
                    "CO_CODECOMPTE": "",
                    "CodeAgence": Objetenv[0]['CodeAgence'],
                    "RECIPIENTPHONE": Objetenv[0]['RECIPIENTPHONE'],
                    "SM_RAISONNONENVOISMS": "xxx",
                    "SM_DATEPIECE": "12-05-2022",
                    "LO_LOGICIEL": "01",
                    "OB_NOMOBJET": "test",
                    "SMSTEXT": Objetenv[0]['SMSTEXT'],
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



def pvpPreparationSms(connexion, AG_CODEAGENCE, CL_TELEPHONE, OP_CODEOPERATEUR, CL_DATECREATION, SMSTEXT, TE_CODESMSTYPEOPERATION, SM_NUMSEQUENCE, SM_DATEEMISSIONSMS, SM_STATUT, TYPEOPERATION, SL_LIBELLE2) -> List[clsParams]:
    clsParamss = []
    #clsParamss: List[clsParams] = []
    clsParams = {}

    clsParams['SL_LIBELLE2'] = SL_LIBELLE2
    clsParams['LO_LOGICIEL'] = "1"
    clsParams['AG_CODEAGENCE'] = AG_CODEAGENCE
    clsParams['RECIPIENTPHONE'] = CL_TELEPHONE
    clsParams['OP_CODEOPERATEUR'] = OP_CODEOPERATEUR
    clsParams['SM_DATEPIECE'] = CL_DATECREATION #CL_DATECREATION.strftime("%d-%m-%Y")
    clsParams['SM_RAISONNONENVOISMS'] = ""
    clsParams['TYPEOPERATION'] = TYPEOPERATION
    clsParams['SMSTEXT'] = SMSTEXT
    clsParams['TE_CODESMSTYPEOPERATION'] = TE_CODESMSTYPEOPERATION
    clsParams['SM_NUMSEQUENCE'] = SM_NUMSEQUENCE
    clsParams['SM_DATEEMISSIONSMS'] = SM_DATEEMISSIONSMS 
    clsParams['SM_STATUT'] = SM_STATUT
    

    # Appel à une fonction externe pour l'envoi des SMS
    clsSmsouts = pvgMobileSms(connexion, clsParams)

    # Traitement des résultats des SMS envoyés
    if clsSmsouts:
        clsParams['SM_NUMSEQUENCE'] = clsSmsouts[0]['SM_NUMSEQUENCE']
        clsParams['SMSTEXT'] = clsSmsouts[0]['SM_MESSAGE']
        clsParams['RECIPIENTPHONE'] = clsSmsouts[0]['SM_TELEPHONE']
        clsParams['SL_CODEMESSAGE'] = clsSmsouts[0]['SL_CODEMESSAGE']
        clsParams['SL_MESSAGE']= clsSmsouts[0]['SL_MESSAGE']
        clsParams['SL_RESULTAT'] = clsSmsouts[0]['SL_RESULTAT']
        clsParams['CodeAgence'] = AG_CODEAGENCE

    clsParamss.append(clsParams)

    return clsParamss



def pvgMobileSms(connexion, clsParams):
    clsSmss = []
    resulttel = clsParams['RECIPIENTPHONE'] if clsParams['RECIPIENTPHONE'] != None else ""
    # Paramètres de la procédure stockée
    params = {
        'LG_CODELANGUE':'fr',
        'AG_CODEAGENCE': clsParams['AG_CODEAGENCE'],
        'CL_TELEPHONE': resulttel,
        'SM_RAISONNONENVOISMS': clsParams['SM_RAISONNONENVOISMS'],
        'SL_MESSAGECLIENT' : clsParams['SMSTEXT'],
        'SM_DATEPIECE' : clsParams['SM_DATEPIECE'],
        'LO_LOGICIEL' : clsParams['LO_LOGICIEL'],
        'OP_CODEOPERATEUR' : clsParams['OP_CODEOPERATEUR'],
        'TE_CODESMSTYPEOPERATION' 	: clsParams['TE_CODESMSTYPEOPERATION'],
        'SM_NUMSEQUENCE' : clsParams['SM_NUMSEQUENCE'],
        'SM_STATUT' : clsParams['SM_STATUT'],
        'TYPEOPERATION' : clsParams['TYPEOPERATION'],
        'SL_LIBELLE2' : clsParams['SL_LIBELLE2'],
        'CODECRYPTAGE': 'Y}@128eVIXfoi7'
    }

     # Récupérer la connexion et le curseur de la base de données depuis cls_donnee
    try:
        cursor = connexion
    except Exception as e:
        # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        cursor.close()
        MYSQL_REPONSE = f'Impossible de récupérer le curseur de la base de données : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)

    # Exécution de la procédure stockée
    try:
        cursor.execute("EXECUTE PS_APISMS  ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?", list(params.values()))
        #instruction pour valider la commande de mise à jour
        #connexion.commit()
    except Exception as e:
        # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        cursor.close()
        MYSQL_REPONSE = e.args[1]
        if "varchar" in MYSQL_REPONSE:
            MYSQL_REPONSE = MYSQL_REPONSE.split("varchar", 1)[1].split("en type de donn", 1)[0]
            
        raise Exception(MYSQL_REPONSE)
       # return {'error': f'Impossible d\'exécuter la procédure stockée : {str(e.args[1])}'}
    clsSmss = recup_info_apisms_client(connexion, clsParams['OP_CODEOPERATEUR'])
    
    return clsSmss



def recup_info_apisms_client(connexion, OP_CODEOPERATEUR):
    try:
        cursor = connexion
        varreq="SELECT * FROM TEMPAPISMSRESULTAT"+OP_CODEOPERATEUR
        # Exécution de la fonction SQL
        cursor.execute(varreq)

        # Récupération des résultats
        rows = cursor.fetchall()
        RetourSmss = []
        # Création d'un dictionnaire pour stocker les données récupérées
        # Traitement des résultats
        for row in rows:
            clsSms = {}
            clsSms['SL_RESULTAT'] = row.SL_RESULTAT
            clsSms['SL_MESSAGE'] = row.SL_MESSAGE
            clsSms['SM_TELEPHONE'] = row.CL_TELEPHONE
            clsSms['SM_MESSAGE'] = row.SL_MESSAGECLIENT
            clsSms['SL_CODEMESSAGE'] = row.SL_CODEMESSAGE
            clsSms['SM_NUMSEQUENCE'] = row.SM_NUMSEQUENCERETOURS
            RetourSmss.append(clsSms)
            
        if not RetourSmss:
            clsSms = {}
            clsSms['SL_RESULTAT'] = "FALSE"
            clsSms['SL_MESSAGE'] = "Le formatage du Sms Client a échoué"
            clsSms['SM_TELEPHONE'] ='' # clsParams['RECIPIENTPHONE']
            clsSms['SM_MESSAGE'] = ""
            clsSms['SL_CODEMESSAGE'] = ""#datetime.datetime(1900, 1, 1)
            clsSms['SM_NUMSEQUENCE'] = "0"
            RetourSmss.append(clsSms)    
        # Faites ce que vous voulez avec les données récupérées
        return RetourSmss
    except Exception as e:
        cursor.execute("ROLLBACK")
        cursor.close()
        MYSQL_REPONSE = str(e.args[1])
        raise Exception(MYSQL_REPONSE)
        #print(f"Une erreur s'est produite : {str(e.args[1])}")   



def pvgMobileSmsUpdateStatut(connexion, AG_CODEAGENCE, SM_DATEPIECE, SM_DATEEMISSIONSMS, SM_NUMSEQUENCE, SM_STATUT, SM_RAISONNONENVOISMS,OP_CODEOPERATEUR):
    params = {}
    #return clsSmsouts
    params = {
        'AG_CODEAGENCE': AG_CODEAGENCE,
        'SM_DATEPIECE': SM_DATEPIECE,
        'SM_DATEEMISSIONSMS': SM_DATEEMISSIONSMS,
        'SM_NUMSEQUENCE': SM_NUMSEQUENCE,
        'SM_STATUT': SM_STATUT,
        'SM_RAISONNONENVOISMS': SM_RAISONNONENVOISMS,
        'OP_CODEOPERATEUR': OP_CODEOPERATEUR,
        'CODECRYPTAGE':'Y}@128eVIXfoi7'
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
        cursor.execute("EXECUTE PS_MOBILESMSUPDATESTATUTNEW  ?, ?, ?, ?, ?, ?, ?,?", list(params.values()))
        #instruction pour valider la commande de mise à jour
        #connexion.commit()
    except Exception as e:
        MYSQL_REPONSE = str(e)
        raise Exception(MYSQL_REPONSE)

    # Récupération des résultats
    try:
        # Assurez-vous que la valeur est une chaîne de caractères pour pouvoir la convertir en entier
         recup_info_apisms_clientresultat(connexion, OP_CODEOPERATEUR)
    except Exception as e:
         # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible de récupérer les résultats de la procédure stockée : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)



def recup_info_apisms_clientresultat(connexion, co_codeoperateur):
    try:
        cursor = connexion.cursor()
        varreq="SELECT * FROM TEMPAPISMSSTATUT"+co_codeoperateur
        # Exécution de la fonction SQL
        cursor.execute(varreq)

        # Récupération des résultats
        rows = cursor.fetchall()
        RetourSmssResultat = []
        # Création d'un dictionnaire pour stocker les données récupérées
        # Traitement des résultats
        for row in rows:
            clsSms = {}
            clsSms['AG_CODEAGENCE'] = row.AG_CODEAGENCE
            clsSms['SL_RESULTAT'] = row.SL_RESULTAT
            clsSms['SL_MESSAGE'] = row.SL_MESSAGE
            RetourSmssResultat.append(clsSms)
        # Faites ce que vous voulez avec les données récupérées
        #return RetourSmssResultat
    except Exception as e:
        MYSQL_REPONSE = str(e.args[1])
        raise Exception(MYSQL_REPONSE)
        #print(f"Une erreur s'est produite : {str(e)}")  