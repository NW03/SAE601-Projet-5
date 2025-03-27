I. Présentation de la méthode d’ajout et de configuration

La mise en place d’un backbone opérateur BGP/MPLS peut être complexe une première fois, mais lorsqu’on vient ajouter des clients sur une architecture déjà existante, la procédure est répétitive et source d’erreurs. C’est pourquoi une solution d’automatisation a été mise en place pour les nouveaux routeurs afin de gagner du temps et de réduire les possibles erreurs.

Pour faire cela, plusieurs méthodes ont été créées et nous allons voir ici comment les utiliser.
Le but principal est donc d’ajouter sur Eve NG un nouveau client (routeur) et de le connecter au backbone déjà existant avec du BGP/MPLS/OSPF/VRF configuré et de lancer des scripts depuis une VM Linux permettant d’automatiser au maximum les tâches.
Avant toute chose, certaines tâches devront tout de même être effectuées manuellement pour pouvoir relier au minimum le nouveau routeur au backbone afin de lancer les codes.
Nous allons donc utiliser Ansible depuis une machine Linux présente dans le schéma afin de lancer les scripts.

II. Prérequis
1. Sur Linux, il faut tout d'abord installer Ansible et créer le répertoire de travail dans lequel travailler. Ensuite, on va cloner le Git afin de récupérer les fichiers.
```shell
sudo apt update
sudo apt install ansible
mkdir {monautomatisation}
cd {monautomatisation}
git clone https://github.com/NW03/SAE601-Projet-5.git
```

2. Ajout et pré-configuration du routeur :
Avant tout, nous devons effectuer quelques configurations manuelles sur le nouveau routeur pour pouvoir le contacter depuis notre machine Linux.
Pour cela, ajoutez un routeur sur votre schéma.
Ensuite, passez en mode console sur celui-ci.
Nous allons ajouter la loopback, l’interface à laquelle le routeur sera connecté et enfin la configuration SSH.
Tout d’abord, la loopback. Pour cela, veuillez exécuter ces commandes :
```shell
R1#conf t
R1(config)#interface loopback0
R1(config-if)#ip address [Votre adresse de Lo0] [Masque de Lo0]
```
Ensuite, nous allons attribuer une adresse à l’interface Ethernet connectée au routeur du backbone. Pour cela, suivez ceci :
```shell
R1(config)#interface Ethernet 0/[n°interface connecté]
R1(config-if)#ip address [Adresse IP] [Masque]
R1(config-if)#no shutdown
```
Enfin, configurez la connexion SSH, pour cela :
```shell
R1(config)#hostname [Nom du routeur voulu]
R1(config)#ip domain-name [Nom de domaine voulu]
R1(config)#ip ssh version 2
R1(config)#crypto key generate rsa
```
Il vous sera demandé de choisir la taille de la clé, vous pouvez choisir ce qui vous semble le mieux, dans notre cas, nous allons choisir 4096.
```shell
R1(config)#line vty 0 4
R1(config-line)#login local
R1(config-line)#transport input ssh
R1(config-line)# exit
R1(config)#do sh run
```
La connexion SSH devrait être désormais effectuée.

3. Connexion SSH :
Ensuite, il faut voir si la machine Linux arrive à bien contacter les routeurs du backbone en SSH. Pour cela, il faut utiliser le playbook permettant de tester la connexion SSH vers les routeurs.
```shell
# Se placer dans le répertoire où vous avez fait le git clone
# Faire un nano inventory.yml et modifier les adresses IP des routeurs ainsi que les noms en fonction de votre infrastructure
ansible-playbook -i inventory.yml test_connection.yml -vvv
```
Si la connexion s'effectue correctement, alors vous devriez voir que tout s'affiche en vert avec également les interfaces de vos routeurs.
Cela signifie bien que l’on peut désormais pousser les scripts pour la configuration.

III. Configuration des routeurs
1. Ajout des VRF dans les routeurs du backbone

Pour commencer, on va lancer le script Python. Celui-ci va nous générer un fichier de playbook personnalisé. Celui-ci ressemblera à celui qui est déjà présent et qui sert d'exemple. Ce playbook va permettre de créer les VRF et de les propager sur les routeurs, d'attribuer une IP sur le port du routeur de backbone auquel sera ajouté le client et il va également mettre les routes sur le routeur de backbone.

```shell
# Si vous n'utilisez pas le script Python:
# - Modifier à la main dans playbook.yml :
# - - vrf definition [nomdevotrevrf]
# - - rd [votrerd]
# - - route-target export [votrerd]
# - - route-target import [votrerd]
# - - vrf forwarding [nomdevotrevrf]
# - - ip address [adresse IP de l'interface du routeur] [masque]
# - - parents:  [votreinterface]
# - - when: inventory_hostname == '[votrenomderouteur]'
# - - ip route vrf [nomdevotrevrf] 0.0.0.0 0.0.0.0 [interface d'un de vos routeurs] global
# - - ip route 192.168.50.0 255.255.255.0 [votreinterface] 192.168.50.2

# Une fois les modifications effectuées, enregistrer le fichier puis:

ansible-playbook -i inventory.yml playbook.yml
```

```shell
# Si vous utilisez le script Python:

python3 Creation_de_playbook.py

# Laissez-vous guider
# Une fois que vous avez fini avec le fichier Python, celui-ci va générer un fichier avec le nom du client en .yml
# Réalisez ensuite l'action suivante :

ansible-playbook -i inventory.yml [Client-X].yml
```
Enfin, vous pouvez tester la connexion en lançant un ping depuis votre machine vers le routeur créé :
```shell
ping [ip interface nouveau routeur]
```

Et voilà, votre nouveau routeur est désormais configuré !

