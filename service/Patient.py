import sys
sys.path.append("../")
from config import CODECRYPTAGE
import datetime
from datetime import datetime
from tools.toolDate import parse_datetime



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
            result['OP_CODEOPERATEUR'] = row.OP_CODEOPERATEUR
            result['PL_CODENUMCOMPTE'] = row.PL_CODENUMCOMPTE
  
            # Ajouter le dictionnaire à la liste des résultats
            results.append(result)
        
        return results
    except Exception as e:
        # En cas d'erreur, lever une exception avec un message approprié
        raise Exception(f"Erreur lors de la récupération des données: {str(e.args[1])}")   
    
    
    
#creation / modification du patient
def insertpatient(connection, patient_info):
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
        cursor = connection
        cursor.execute("EXEC dbo.PC_PATIENTSIMPLE ?, ?, ?, ?, ?,?, ?, ?, ?, ?,?, ?, ?, ?, ?,?, ?", list(params.values()))
        connection.commit()
        get_commit(connection,patient_info)
        #cursor.close()
    except Exception as e:
        connection.rollback()
        raise Exception(f" {str(e.args[1])}")

#suppression
def deletepatient(connection, patient_info):
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
        cursor = connection
        cursor.execute("EXEC dbo.PC_PATIENTSIMPLE ?, ?, ?, ?, ?,?, ?, ?, ?, ?,?, ?, ?, ?, ?,?, ?", list(params.values()))
        connection.commit()
        get_commit(connection,patient_info)
        #cursor.close()
    except Exception as e:
        connection.rollback()
        MYSQL_REPONSE = e.args[1]
        if "varchar" in MYSQL_REPONSE:
               MYSQL_REPONSE = MYSQL_REPONSE.split("varchar", 1)[1].split("en type de donn", 1)[0]
               
        raise Exception(MYSQL_REPONSE)            
    
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
    