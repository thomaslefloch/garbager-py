# garbager-py
Script Python, pour "poubelliser" vos données et les masquer. Par le magazine "Pirate Mag'" HS n°2 [Pirates Magazine HS2 (V40S) - ACBM.com](http://www.acbm.com/pirates/num_hs_02/index.html)

Prend en charge les arguments en ligne de commande. -h pour les lister (aide).
Il est utile de se créer un dictionnaire si vous voulez poubelliser vos données une fois l'encodage fait. 

## Quelques exemples

* Encoder en "garbageant" un fichier :
  
  garbager.py -e fichier.source -vfcr -s dico.txt -g fichier.a.ecraser 313 i 0
  
* décoder en utilisant un fichier garbage généré précédemment (la longueur étant à recopier du log de l'exécution initiale) :
  
  gabager.py -dvfcr -s dico.txt -g  fichier.ecrase 313 i 656
  
* encoder directement dans un fichier :
  
  garbager.py -e fichier.entree -vfcr -s  dico.txt -o fichier.sortie
  
* décoder directement un fichier généré par la commande précédente :
  
  garbager.py -d fichier.sortie -vfcr -s dico.txt -o fichier.original
