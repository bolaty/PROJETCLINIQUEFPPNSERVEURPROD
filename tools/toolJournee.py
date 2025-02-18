from config import CODECRYPTAGE
from tools.toolDate import parse_datetime

# tester si la journee de travail est ouverte ou pas
def test_journee_fermee(connexion, *vppCritere):
    cursor = connexion.cursor()
    
    vppCritere2 = (vppCritere[0], vppCritere[1], 'O')
    criteres, valeurs = pvpChoixCritere(vppCritere2)
    query = f"""
        SELECT COUNT(JT_DATEJOURNEETRAVAIL) AS JT_DATEJOURNEETRAVAIL FROM JOURNEETRAVAIL 
        {criteres}
    """
    
    try:
        # Exécution de la requête
        cursor.execute(query, valeurs)
        rows = cursor.fetchall()

        # Formatage des résultats
        results = []
        for row in rows:
            result = {
                'NBRE': row[0],
            }
            results.append(result)
  
        if results[0]['NBRE'] != 0:
            clsOperateur= pvgTableLabel(connexion, vppCritere);
            if clsOperateur[0]['OP_JOURNEEOUVERTE'] == "N" and clsOperateur[0]['OP_CAISSIER'] == "O":
                result = {
                    'NBRE': '0',
                }
                results.append(result)
        return results
    except Exception as e:
        # En cas d'erreur, lever une exception avec un message approprié
        raise Exception(f"Erreur lors de la récupération des données: {str(e.args[1])}")

def pvgTableLabel(connexion, vppCritere):
    cursor = connexion.cursor()
    
    vppCritere2 = (vppCritere[0], vppCritere[2])
    # vppCritere2 = (vppCritere[0],)
    criteres, valeurs = pvpChoixCritere2(vppCritere2)
    query = f"""
        SELECT
            OP_CODEOPERATEUR, AG_CODEAGENCE, PO_CODEPROFIL, SR_CODESERVICE,
            PL_CODENUMCOMPTECAISSE, PL_CODENUMCOMPTECOFFRE,
            PL_CODENUMCOMPTEPROVISOIRE, OP_NOMPRENOM, OP_LOGIN,
            OP_MOTPASSE, OP_ACTIF, OP_TELEPHONE, OP_EMAIL,
            OP_JOURNEEOUVERTE, 
            OP_CAISSIER, OP_DATESAISIE
        FROM dbo.FT_OPERATEUR('{CODECRYPTAGE}')
        {criteres}
    """
    
    try:
        # Exécution de la requête
        cursor.execute(query, valeurs)
        rows = cursor.fetchall()

        # liste des clés correspondant aux colonnes de la requête
        columns = [
            "OP_CODEOPERATEUR", "AG_CODEAGENCE", "PO_CODEPROFIL", "SR_CODESERVICE",
            "PL_CODENUMCOMPTECAISSE", "PL_CODENUMCOMPTECOFFRE",
            "PL_CODENUMCOMPTEPROVISOIRE", "OP_NOMPRENOM", "OP_LOGIN",
            "OP_MOTPASSE", "OP_ACTIF", "OP_TELEPHONE", "OP_EMAIL", "OP_JOURNEEOUVERTE", "OP_CAISSIER", "OP_DATESAISIE"
        ]

        # conversion en liste d'objets (dictionnaires)
        tab_objects = [dict(zip(columns, row)) for row in rows]       

        # Formatage des résultats
        results = []
        for row in tab_objects:
            result = {
                'OP_CODEOPERATEUR': row['OP_CODEOPERATEUR'],
                'AG_CODEAGENCE': row['AG_CODEAGENCE'],
                'PO_CODEPROFIL': row['PO_CODEPROFIL'],
                'SR_CODESERVICE': row['SR_CODESERVICE'],
                'OP_NOMPRENOM': row['OP_NOMPRENOM'],
                'OP_TELEPHONE': row['OP_TELEPHONE'],
                'OP_EMAIL': row['OP_EMAIL'],
                'OP_LOGIN': row['OP_LOGIN'],
                'OP_MOTPASSE': row['OP_MOTPASSE'],
                'OP_ACTIF': row['OP_ACTIF'],
                'PL_CODENUMCOMPTECAISSE': row['PL_CODENUMCOMPTECAISSE'],
                'PL_CODENUMCOMPTECOFFRE': row['PL_CODENUMCOMPTECOFFRE'],
                'PL_CODENUMCOMPTEPROVISOIRE': row['PL_CODENUMCOMPTEPROVISOIRE'],
                'OP_DATESAISIE': row['OP_DATESAISIE'],
                'OP_JOURNEEOUVERTE': row['OP_JOURNEEOUVERTE'],
                'OP_CAISSIER': row['OP_CAISSIER']
            }
            results.append(result)
        return results
    except Exception as e:
        if len(e.args) == 1:
            raise Exception(f"{e.args[0]}")
        else:
            raise Exception(f"Erreur lors de la récupération des données: {e.args[1]}")
    
    
    
# les criteres de filtre
def pvpChoixCritere(vppCritere2):
    if len(vppCritere2) == 0:
        vap_critere = ""
        vap_valeur_parametre = []
    elif len(vppCritere2) == 1:
        vap_critere = " WHERE AG_CODEAGENCE=? "
        vap_valeur_parametre = [int(vppCritere2[0])]
    elif len(vppCritere2) == 2:
        vap_critere = " WHERE AG_CODEAGENCE=? AND  JT_DATEJOURNEETRAVAIL=? "
        vap_valeur_parametre = [int(vppCritere2[0]), parse_datetime(vppCritere2[1])]
    elif len(vppCritere2) == 3:
        vap_critere = " WHERE AG_CODEAGENCE=? AND  JT_DATEJOURNEETRAVAIL=? AND  JT_STATUT=? "
        vap_valeur_parametre = [int(vppCritere2[0]), parse_datetime(vppCritere2[1]), vppCritere2[2]]
    else:
        raise ValueError("Nombre de critères non pris en charge.")
    
    return vap_critere, vap_valeur_parametre



def pvpChoixCritere2(vppCritere2):
    if len(vppCritere2) == 0:
        vap_critere = ""
        vap_valeur_parametre = []
    elif len(vppCritere2) == 1:
        vap_critere = " WHERE AG_CODEAGENCE=? "
        vap_valeur_parametre = [vppCritere2[0]]
    elif len(vppCritere2) == 2:
        vap_critere = " WHERE AG_CODEAGENCE=? AND  OP_CODEOPERATEUR=? "
        vap_valeur_parametre = [int(vppCritere2[0]), int(vppCritere2[1])]
    elif len(vppCritere2) == 3:
        vap_critere = " WHERE AG_CODEAGENCE=? AND  OP_CODEOPERATEUR=? AND  PO_CODEPROFIL=? "
        vap_valeur_parametre = [int(vppCritere2[0]), int(vppCritere2[1]), vppCritere2[2]]
    elif len(vppCritere2) == 4:
        vap_critere = " WHERE AG_CODEAGENCE=? AND  OP_CODEOPERATEUR=? AND  PO_CODEPROFIL=? AND PL_CODENUMCOMPTE=? "
        vap_valeur_parametre = [int(vppCritere2[0]), int(vppCritere2[1]), vppCritere2[2]]
    else:
        raise ValueError("Nombre de critères non pris en charge.")
    
    return vap_critere, vap_valeur_parametre