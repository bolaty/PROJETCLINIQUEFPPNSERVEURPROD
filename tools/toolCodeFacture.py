import datetime
import json
import os

# Chemin pour stocker l'état du compteur
STATE_FILE = "facture_state.json"

def load_state():
    # Charge l'état sauvegardé
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as file:
            return json.load(file)
    return {"date": None, "counter": 0}

def save_state(state):
    # Sauvegarde l'état
    with open(STATE_FILE, "w") as file:
        json.dump(state, file)

def generer_code_facture(prefix):
    """
    Génère un code de facture.
    
    Args:
        prefix (int): Les 4 premiers chiffres du code, fournis en paramètre -AG_CODEAGENCE-
    
    Returns:
        str: Le code de facture généré.
    """
    # Conversion du préfixe en entier
    if not (isinstance(prefix, str) and prefix.isdigit() and len(prefix) == 4):
        raise ValueError("Le préfixe doit être une chaîne de 4 chiffres.")
    prefix_int = int(prefix)
    
    state = load_state()
    today = datetime.datetime.now().strftime("%Y%m%d")
    
    # Réinitialiser le compteur si la journée a changé
    if state["date"] != today:
        state["date"] = today
        state["counter"] = 1
    else:
        state["counter"] += 1
    
    # Générer le code de facture
    code_facture = f"{prefix_int}{today}{state['counter']:05d}"
    
    # Sauvegarder l'état mis à jour
    save_state(state)
    
    return code_facture
