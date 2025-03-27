import yaml
from collections import OrderedDict
import ipaddress

def represent_ordereddict(dumper, data):
    return dumper.represent_mapping('tag:yaml.org,2002:map', data.items())

yaml.add_representer(OrderedDict, represent_ordereddict)

def validate_ip(ip_str):
    """Entrer une Adresse IP Valide """
    try:
        ipaddress.ip_address(ip_str)
        return ip_str
    except ValueError:
        print("Adresse IP invalide. Veuillez recommencez.")
        return None

def get_input(prompt, validator=None):
    """Get validate input from user."""
    while True:
        value = input(prompt).strip()
        if not value:
            print("Cette espace ne peut pas être vide.")
            continue
        if validator:
            validated = validator(value)
            if validated is None:
                continue
            return validated
        return value

def generate_playbook():
    """Generation du Playbook."""
    # Détails VRF
    vrf_name = get_input("Renseigner le Nom VRF voulu (ex : Client-R2): ")
    vrf_id = get_input("Renseigner l'ID de VRF voulu (ex : 200:1): ")
    
    # Détails équipement
    hostname = get_input("Renseigner l'hostname voulu (ex : R12): ")
    device_vrf = get_input("Renseigner le nom de l'équipement VRF voulu (ex : Client-R2): ")
    
    # Détails des IP et des interfaces 
    ip_address = get_input("Renseigner une Adresse IP valide: ", validate_ip)
    interface = get_input("Renseigner l'interface voulu (ex : ethernet0/3): ")
    
    # Détails des IP Routes
    routes = []
    while True:
        add_route = input("Voulez-vous ajouter une IP route? (yes/no): ").lower()
        if add_route != 'yes':
            break
        
        route_destination = get_input("Renseigner la route de destination (ex : 0.0.0.0): ", validate_ip)
        route_mask = get_input("Renseigner le masque (ex : 0.0.0.0): ", validate_ip)
        route_next_hop = get_input("Renseigner le Next-Hop: ", validate_ip)
        route_interface = get_input("Renseigner l'interace voulu ( ex : ethernet0/3): ")
        
        routes.append({
            'destination': route_destination,
            'mask': route_mask,
            'next_hop': route_next_hop,
            'interface': route_interface
        })
    
    playbook_item = OrderedDict([
        ('hosts', 'backbone_routers'),  # Déplacé en premier
        ('gather_facts', 'no'),  # Déplacé en second
        ('tasks', [
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
    
    if routes:
        route_task = OrderedDict([
            ('name', f'Iproute sur {hostname}'),
            ('ios_config', {
                'lines': [
                    f'ip route vrf {device_vrf} {route["destination"]} {route["mask"]} {route["next_hop"]} {route["interface"]} global'
                    for route in routes
                ]
            })
        ])
        playbook_item['tasks'].append(route_task)
    
    # Création du Playbook
    playbook = [playbook_item]
    
    # Fichier YAML
    filename = f'{hostname}_playbook.yml'
    with open(filename, 'w') as file:
        yaml.dump(playbook, file, default_flow_style=False)
    
    print(f"Playbook généré: {filename}")

if __name__ == "__main__":
    generate_playbook()
