from config import CODECRYPTAGE
from tools.toolDate import parse_datetime



def dashboard(connexion, cls_dashboard):
    # Paramètres de la procédure stockée
    params = {
        'AG_CODEAGENCE': cls_dashboard['AG_CODEAGENCE'],
        'OP_CODEOPERATEUR': cls_dashboard['OP_CODEOPERATEUR'],
        'DATEDEBUT': parse_datetime(cls_dashboard['DATEDEBUT']),
        'DATEFIN': parse_datetime(cls_dashboard['DATEFIN']),
        'TYPEOPERATION': cls_dashboard['TYPEOPERATION'],
        'CODECRYPTAGE': CODECRYPTAGE
    }

     # Récupérer la connexion et le curseur de la base de données depuis cls_donnee
    try:
        cursor = connexion.cursor()
    except Exception as e:
        cursor.close()
         # En cas d'erreur, annuler la transaction
        cursor.execute("ROLLBACK")
        MYSQL_REPONSE = f'Impossible de récupérer le curseur de la base de données : {str(e.args[1])}'
        raise Exception(MYSQL_REPONSE)
    # Exécution de la procédure stockée
    try:
        cursor.execute("EXECUTE PS_STATISTIQUEDASHBOARD  ?, ?, ?, ?, ?, ?", list(params.values()))
        
        rows = cursor.fetchall()
        results = []
        for row in rows:
            result = {}
            
            result['NOMBRE_ACTE'] = row.NOMBRE_ACTE
            result['MONTANT_TOTAL_ACTE'] = row.MONTANT_TOTAL_ACTE
            
            result['NOMBRE_CONSULTATION'] = row.NOMBRE_CONSULTATION
            result['MONTANT_TOTAL_CONSULTATION'] = row.MONTANT_TOTAL_CONSULTATION
            result['NOMBRE_LABO'] = row.NOMBRE_LABO
            result['MONTANT_TOTAL_LABO'] = row.MONTANT_TOTAL_LABO
            result['NOMBRE_PHARMACIE'] = row.NOMBRE_PHARMACIE
            result['MONTANT_TOTAL_PHARMACIE'] = row.MONTANT_TOTAL_PHARMACIE
            result['NOMBRE_HOSPITALISATION'] = row.NOMBRE_HOSPITALISATION
            result['MONTANT_TOTAL_HOSPITALISATION'] = row.MONTANT_TOTAL_HOSPITALISATION
            result['NOMBRE_EXAMEN'] = row.NOMBRE_EXAMEN
            result['MONTANT_TOTAL_EXAMEN'] = row.MONTANT_TOTAL_EXAMEN
            
            result['NOMBRE_ESPECE'] = row.NOMBRE_ESPECE
            result['MONTANT_TOTAL_ESPECE'] = row.MONTANT_TOTAL_ESPECE
            result['NOMBRE_OM'] = row.NOMBRE_OM
            result['MONTANT_TOTAL_OM'] = row.MONTANT_TOTAL_OM
            result['NOMBRE_MOMO'] = row.NOMBRE_MOMO
            result['MONTANT_TOTAL_MOMO'] = row.MONTANT_TOTAL_MOMO
            result['NOMBRE_FLOOZ'] = row.NOMBRE_FLOOZ
            result['MONTANT_TOTAL_FLOOZ'] = row.MONTANT_TOTAL_FLOOZ
            result['NOMBRE_WAVE'] = row.NOMBRE_WAVE
            result['MONTANT_TOTAL_WAVE'] = row.MONTANT_TOTAL_WAVE
            result['NOMBRE_CHEQUE'] = row.NOMBRE_CHEQUE
            result['MONTANT_TOTAL_CHEQUE'] = row.MONTANT_TOTAL_CHEQUE
            result['NOMBRE_VIREMENT'] = row.NOMBRE_VIREMENT
            result['MONTANT_TOTAL_VIREMENT'] = row.MONTANT_TOTAL_VIREMENT
            result['MONTANT_TOTAL_ACTE_GLOBALE'] = row.MONTANT_TOTAL_ACTE_GLOBALE
            result['MONTANT_TOTAL_DEPENSE'] = row.MONTANT_TOTAL_DEPENSE
            result['MONTANT_TOTAL_DEPENSE_GLOBALE'] = row.MONTANT_TOTAL_DEPENSE_GLOBALE
            result['MONTANT_TOTAL_VERSEMENT'] = row.MONTANT_TOTAL_VERSEMENT
            result['MONTANT_TOTAL_RETRAIT'] = row.MONTANT_TOTAL_RETRAIT
            result['MONTANT_TOTAL_VERSEMENT_GLOBAL'] = row.MONTANT_TOTAL_VERSEMENT_GLOBAL
            result['MONTANT_TOTAL_RETRAIT_GLOBAL'] = row.MONTANT_TOTAL_RETRAIT_GLOBAL
            result['MONTANT_TOTAL_RETRAIT_WAVE'] = row.MONTANT_TOTAL_RETRAIT_WAVE
            result['MONTANT_TOTAL_RETRAIT_WAVE_GLOBAL'] = row.MONTANT_TOTAL_RETRAIT_WAVE_GLOBAL
  
            # Ajouter le dictionnaire à la liste des résultats
            results.append(result)
        
        return results
    except Exception as e:
        cursor.close()
        # En cas d'erreur, annuler la transaction
        #cursor.execute("ROLLBACK")
        MYSQL_REPONSE = e.args[1]
        if "varchar" in MYSQL_REPONSE:
            MYSQL_REPONSE = MYSQL_REPONSE.split("varchar", 1)[1].split("en type de donn", 1)[0]
       
        raise Exception(MYSQL_REPONSE)