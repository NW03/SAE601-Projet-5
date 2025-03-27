# Importation des bibliothèques nécessaires
import yaml  # Bibliothèque pour gérer les fichiers YAML
from collections import OrderedDict  # Pour maintenir l'ordre des éléments dans un dictionnaire
import ipaddress  # Pour valider les adresses IP

# Fonction pour représenter correctement OrderedDict lors de la sérialisation YAML
def represent_ordereddict(dumper, data):
    """
    Permet de convertir un OrderedDict en format YAML en préservant l'ordre original
    - dumper : l'objet responsable de la conversion YAML
    - data : l'OrderedDict à convertir
    """
    return dumper.represent_mapping('tag:yaml.org,2002:map', data.items())

# Ajout d'un représentateur personnalisé pour OrderedDict dans PyYAML
yaml.add_representer(OrderedDict, represent_ordereddict)

def validate_ip(ip_str):
    """
    Valide une adresse IP
    - ip_str : chaîne de caractères représentant l'adresse IP
    - Retourne l'adresse IP si valide, None sinon
    """
    try:
        # Tente de convertir la chaîne en une adresse IP valide
        ipaddress.ip_address(ip_str)
        return ip_str
    except ValueError:
        # Affiche un message d'erreur si l'IP est invalide
        print("Adresse IP invalide. Veuillez recommencez.")
        return None

def get_input(prompt, validator=None):
    """
    Fonction générique pour obtenir une entrée utilisateur avec validation
    - prompt : message à afficher pour guider l'utilisateur
    - validator : fonction optionnelle de validation de l'entrée
    - Retourne la valeur validée
    """
    while True:
        # Demande une entrée et supprime les espaces avant/après
        value = input(prompt).strip()
        
        # Vérifie que l'entrée n'est pas vide
        if not value:
            print("Cette espace ne peut pas être vide.")
            continue
        
        # Applique la validation si un validateur est fourni
        if validator:
            validated = validator(value)
            if validated is None:
                continue
            return validated
        
        return value

def generate_playbook():
    """
    Fonction principale pour générer un playbook Ansible
    - Collecte les informations nécessaires auprès de l'utilisateur
    - Crée un playbook YAML pour la configuration réseau
    """
    # Collecte des détails VRF
    vrf_name = get_input("Renseigner le Nom VRF voulu (ex : Client-R2): ")
    vrf_id = get_input("Renseigner l'ID de VRF voulu (ex : 200:1): ")
    
    # Collecte des détails de l'équipement
    hostname = get_input("Renseigner l'hostname voulu (ex : R12): ")
    device_vrf = get_input("Renseigner le nom de l'équipement VRF voulu (ex : Client-R2): ")
    
    # Collecte des informations IP et interfaces
    ip_address = get_input("Renseigner une Adresse IP valide: ", validate_ip)
    interface = get_input("Renseigner l'interface voulu (ex : ethernet0/3): ")
    
    # Collecte des routes IP
    routes = []
    while True:
        # Demande à l'utilisateur s'il souhaite ajouter une route
        add_route = input("Voulez-vous ajouter une IP route? (yes/no): ").lower()
        if add_route != 'yes':
            break
        
        # Collecte des détails de la route
        route_destination = get_input("Renseigner la route de destination (ex : 0.0.0.0): ", validate_ip)
        route_mask = get_input("Renseigner le masque (ex : 0.0.0.0): ", validate_ip)
        route_next_hop = get_input("Renseigner le Next-Hop: ", validate_ip)
        route_interface = get_input("Renseigner l'interace voulu ( ex : ethernet0/3): ")
        
        # Ajoute la route à la liste des routes
        routes.append({
            'destination': route_destination,
            'mask': route_mask,
            'next_hop': route_next_hop,
            'interface': route_interface
        })
    
    # Construction du playbook avec un OrderedDict pour préserver l'ordre
    playbook_item = OrderedDict([
        ('hosts', 'backbone_routers'),  # Groupe de routeurs cibles
        ('gather_facts', 'no'),  # Désactive la collecte automatique de facts
        ('tasks', [
            # Tâche de configuration de la VRF
            OrderedDict([
                ('name', f'Config {hostname}'),
                ('ios_config', {
                    'lines': [
                        f'vrf definition {vrf_name}',
                        f'address-family ipv4',
                        f'route-target export {vrf_id}:1',
                        f'route-target import {vrf_id}:1'
                    ]
                })
            ]),
            # Tâche de configuration d'interface IP
            OrderedDict([
                ('name', f'Ip sur {hostname}'),
                ('ios_config', {
                    'lines': [
                        f'vrf forwarding {device_vrf}',
                        f'ip address {ip_address}'
                    ],
                    'parents': ['interface ' + interface]
                })
            ])
        ])
    ])
    
    # Ajout des routes IP si présentes
    if routes:
        route_task = OrderedDict([
            ('name', f'Iproute sur {hostname}'),
            ('ios_config', {
                'lines': [
                    # Génère les commandes de route pour chaque route définie
                    f'ip route vrf {device_vrf} {route["destination"]} {route["mask"]} {route["next_hop"]} {route["interface"]} global'
                    for route in routes
                ]
            })
        ])
        playbook_item['tasks'].append(route_task)
    
    # Création du playbook final (liste de playbook_item)
    playbook = [playbook_item]
    
    # Génération du fichier YAML
    filename = f'{hostname}_playbook.yml'
    with open(filename, 'w') as file:
        # Écrit le playbook dans un fichier YAML
        yaml.dump(playbook, file, default_flow_style=False)
    
    print(f"Playbook généré: {filename}")

# Point d'entrée du script
if __name__ == "__main__":
    generate_playbook()
