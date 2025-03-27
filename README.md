# SAE601-Projet-5
I.	Présentation de la méthode d’ajout et de configuration 

La mise en place d’un backbone opérateur BGP/MPLS peut-être complexe une première fois, mais lorsqu’on vient ajouter des clients sur une architecture déjà existante, la procédure est répétitive et source d’erreurs. C’est pourquoi une solution d’automatisation a été mise en place pour les nouveaux routeurs afin de gagner du temps et de réduire les possibles erreurs.
Pour faire cela, plusieurs méthodes ont étés créées et nous allons voir ici comment les utiliser. 
Le but principal est donc d’ajouter sur Eve NG un nouveau client (routeur) et de le connecter au backbone déjà existant avec du BGP/MPLS/OSPF/VRF de configuré et de lancer des scripts depuis une VM Linux permettant d’automatiser au maximum les taches. 
Avant toute choses, certaines taches devront tout de même être effectué manuellement pour pouvoir relié au minimum le nouveau routeur au backbone afin de lancer les codes. 
Nous allons donc utiliser Ansible depuis une machine Linux présente dans le schéma afin de lancer les scripts. 

II.	Prérequis
1. Sur Linux, il faut tout d'abords installer Ansible et créer le répertoire de travail dans lequel travailler. Ensuite, on va cloner le git afin de récuperer les fichiers. 
```shell
sudo apt update
sudo apt install ansible
mkdir {monautomatisation}
cd {monautomatisation} 
git clone https://github.com/NW03/SAE601-Projet-5.git
```

2.	Ajout et pré-configuration du routeur :
Avant tout, nous devons effectuer quelques configurations manuelles sur le nouveau routeur pour pouvoir le contacter depuis notre machine Linux. 
Pour cela, ajouter un routeur sur votre schéma. 
Ensuite, passer en mode console sur celui-ci. 
Nous allons ajouter la loopback, l’interface auquel le routeur sera connecté et enfin le configuration SSH. 
Tout d’abord la loopback. Pour cela veuillez faire ces commandes :
```shell
R1#conf t
R1(config)#interface loopback0
R1(config-if)#ip address [Votre adresse de Lo0] [Masque de Lo0]
Ensuite nous allons attribuer une adresse à l’interface Ethernet connecté au routeur du backbone. Pour cela, suivez ceci : 
R1(config)#interface Ethernet 0/[n°interface connecté]
R1(config-if)#ip address [Addresse IP] [Masque]
R1(config-if)#no shutdown
Enfin, configurez la connexion SSH, pour cela : 
R1(config)#hostname [Nom du routeur voulu]
R1(config)#ip domain-name [Nom de domaine voulu]
R1(config)#ip ssh version 2
R1(config)#crypto key generate rsa 
Il vous sera demander choisir la taille de la clé, vous pouvez choisir ce qui vous semble le mieux, dans notre cas, nous allons choisir 4096
R1(config)#line vty 0 4
R1(config-line)#login local
R1(config-line)#transport input ssh
R1(config-line)# exit
R1(config)do sh run
```
La connexion SSH devrait être désormais effectué

3.	Connexion SSH : 
Ensuite il faut voir si la machine Linux arrive à bien contacter les routeurs du backbone en SSH. Pour cela, il faut utiliser le playbook permettant de tester la connexion SSH vers les routeurs. 
```shell
# se mettre dans le répertoire ou vous avez fait le git clone
# faire un nano inventory.yml et modifier les adresses IP des routeurs ainsi que les nom en fonction de votre infrastructure 
ansible-playbook -i inventory.yml test_connection.yml -vvv
```
Si la connexion s'effectue correctement, alors vous devriez voir que tout s'affiche en vert avec également les interfaces de vos routeurs. 
Cela veut bien dire que l’on peut désormais push les scripts pour la configuration. 


III.	Configuration des routeurs 
1.	Ajout des VRF dans les routeurs du backbone
<<<<<<< HEAD

Pour commencer, on va lancer le script python. Celui-ci va nous generer un fichier de playbook personnalisé. Celui-ci ressemblera à celui qui est déjà présent et qui sert d'exemple. Ce playbook va permettre de créer les VRFS et de les propager sur les routeurs, de mettre un ip sur le port du routeur de backbone auquel sera ajouté le client et il va également mettre les routes sur le routeur de backbone. 

```shell
# Si vous n'utilisez pas le script python:
# - modifier à la main dans playbook.yml :
# - - vrf definition [nomdevotrevrf]
# - - rd [votrerd] 
# - - route-target export [votrerd]
# - - route-target import [votrerd]
# - - vrf forwarding [nomdevotrevrf]
# - - ip address [adresse IP de l'interface du routeur] [masque]
# - - parents:  [votreinterface]
# - - when: inventory_hostname == '[votrenomderouteur]'
# - - ip route vrf [nomdevotrevrf] 0.0.0.0 0.0.0.0 [interface d'un de vos routeurs] global 
# - - ip route vrf [nomdevotrevrf] 0.0.0.0 0.0.0.0 [interface d'un de vos routeurs] global 
# - - ip route 192.168.50.0 255.255.255.0 [votreinterface] 192.168.50.2
# - - when: inventory_hostname == '[votrenomderouteur]'

# Une fois les modifications effectués, enregistrer le fichier puis:

ansible-playbook -i inventory.yml playbook.yml
```
Une fois cela effectué, vous devrez voir les modifications réalisées.  



=======

Pour commencer, on va lancer le script python. Celui-ci va nous generer un fichier de playbook personnalisé. Celui-ci ressemblera à celui qui est déjà présent et qui sert d'exemple. Ce playbook va permettre de créer les VRFS et de les propager sur les routeurs, de mettre un ip sur le port du routeur de backbone auquel sera ajouté le client et il va également mettre les routes sur le routeur de backbone. 

```shell
# Si vous n'utilisez pas le script python:
# - modifier à la main dans playbook.yml :
# - - vrf definition [nomdevotrevrf]
# - - rd [votrerd] 
# - - route-target export [votrerd]
# - - route-target import [votrerd]
# - - vrf forwarding [nomdevotrevrf]
# - - ip address [adresse IP de l'interface du routeur] [masque]
# - - parents:  [votreinterface]
# - - when: inventory_hostname == '[votrenomderouteur]'
# - - ip route vrf [nomdevotrevrf] 0.0.0.0 0.0.0.0 [interface d'un de vos routeurs] global 
# - - ip route vrf [nomdevotrevrf] 0.0.0.0 0.0.0.0 [interface d'un de vos routeurs] global 
# - - ip route 192.168.50.0 255.255.255.0 [votreinterface] 192.168.50.2
# - - when: inventory_hostname == '[votrenomderouteur]'

# Une fois les modifications effectués, enregistrer le fichier puis:

ansible-playbook -i inventory.yml playbook.yml
```
Une fois cela réalise, vous devrez voir les modifications apparaitre dans le terminal. 



>>>>>>> 328c2b4e430969f5ac4571cb457e3f74485dd0c4
Tout d’abord, nous allons ajouter les nouvelles VRF au sein des routeurs du backbone pour qu’ils puissent se contacter entre eux, pour cela nous allons lancer le premier script. 
Pour cela, suivez ces étapes : 
Connectez vous à votre machine Linux et entré dans ce fichier « NOM DU FICHIER OU FAUT METTRE LES INFOS » puis renseigner les informations des VRF pour le nouveau client :
Ensuite lancer le playbook an invite de commande comme ceci : 
Si ceci apparait : 
Alors les changements se sont bien effectué, on peut confirmer en déroulant la configuration de l’un des routeurs 
Enfin, nous allons lancer la configuration sur le nouveau routeur. Pour cela, renseigner dans ce fichier « NOM DU FICHIER POUR LE NEW ROUTEUR » les infos du nouveau routeur.
Ensuite nous allons lancer le playbook avec cette commande : 
Si tout se passe bien, ceci devrait s’afficher : 
Comme pour l’autre script, nous allons vérifier en regardant la configuration du nouveau routeur. 
Si tout se passe bien, vous devriez retrouver vos informations renseigner dans le fichier directement dans votre nouveau routeur comme ceci : 
Pour finir nous allons ping le client depuis notre machine Linux pour tester la connexion : 
Et voilà, votre nouveau routeur est désormais configuré   
