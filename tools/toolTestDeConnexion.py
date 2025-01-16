import requests
import socket
import uuid

def IsNetworkConnected():
    try:
        response = requests.get("http://www.google.com", timeout=5)
        return response.status_code == 200
    except requests.ConnectionError:
        MYSQL_REPONSE = 400#f'Opération impossible veuillez revoir la connexion internet'
        return MYSQL_REPONSE
        #raise Exception(MYSQL_REPONSE) 



def get_ip_address():
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        print("Adresse IP locale : " + ip_address)
        return ip_address
    except Exception as e:
        #print("Erreur lors de la récupération de l'adresse IP : " + str(e))
        MYSQL_REPONSE = f'Erreur lors de la récupération de l adresse IP : {str(e)}'
        raise Exception(MYSQL_REPONSE) 



def get_public_ip_address():
    try:
        response = requests.get('http://icanhazip.com/')
        ip_address = response.text.strip()
        print("Adresse IP publique : " + ip_address)
        return ip_address
    except Exception as e:
        #print("Erreur lors de la récupération de l'adresse IP publique : " + str(e))
        MYSQL_REPONSE = f'Erreur lors de la récupération de l adresse IP publique : : {str(e)}'
        raise Exception(MYSQL_REPONSE) 



def get_mac_address():
    try:
        mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff)
                                for i in range(0,8*6,8)][::-1])
        print("Adresse MAC : " + mac_address)
        return mac_address
    except Exception as e:
        #print("Erreur lors de la récupération de l'adresse MAC : " + str(e))
        MYSQL_REPONSE = f'Erreur lors de la récupération de l adresse MAC : {str(e)}'
        raise Exception(MYSQL_REPONSE)



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