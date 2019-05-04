# GoodFat

Du gras, oui, mais de qualité !

## Présentation

L'application est hébergée sur Heroku et accessible via [ce lien](https://purbeurre31.herokuapp.com/)  
Recherchez des produits de substitution plus sains aux produits de consommation courante.  
L'application s'appuie sur les données d'[Open Food Facts](https://fr.openfoodfacts.org/) récupérées pour les catégories sélectionnées par l'administrateur.  

Le principe est le suivant :  

- L'utilisateur entre tout ou partie d'un produit dans le champ de recherche  
- L'application cherche le produit correspondant ou, à défaut, le produit se rapprochant le plus de la recherche
- Une liste de produits de substitution est alors proposée, triés par ordre croissant de score nutrionnel ; à partir de cette liste, il est possible de consulter le détail de chaque produit
- Si l'utilisateur a créé un compte, il peut enregistrer des substituts et retrouver ainsi sa liste ultérieurement

## Installation et exécution

### Initialisation

Pour utiliser le programme dans votre environnement, vous devez créer un environnement virtuel et récupérer les fichiers du dépôt GitHub.
Vous devez obligatoirement créer un superuser pour accéder au panneau d'administration.

Les produits sont chargés lors de l'affichage de la page principale, si l'application détecte que certains catégories ne disposent pas de produits.
Pour initialiser les données, deux options sont ainsi possibles (et complémentaires) :

- Soit vous lancez l'application et, faute de catégorie, vous serez redirigé vers la page d'administration. Connectez-vous pour y saisir des catégories à la main, en vous assurant que la acse "Utiliée" soit cochée. Au prochain affichage de la page d'accueil, les produits de la (des) catégorie(s) correspondante(s) seront chargés.
- Soit vous exécutez la commande loadcats <liste de catégories>. Auquel cas, l'ensemble des catégories de la liste seront créées et, comme précédemment, l'affichage suivant de la page d'accueil engendredra lma récupération des produits correspondants.

### Administration

Dans le panneau d'administration, vous pourrez ajouter, modifier, supprimer les catégories. A l'affichage suivant de la page d'accueil, la base de données sera mise à jour :

- Importation des produits des nouvelles catégories (ou modifiées de telle sorte que l'indicateur "Utilisée" soit vrai)
- Suppression des produits des catégories supprimées (ou modifiées de telle sorte que l'indicateur "Utilisée" soit faux)

### La commande "loadcats"

Cette commande d'administration vous permet de faire des actions en masse en ligne de commande. Sa syntaxe est la suivante :

    python manage.py loadcats [cat1, cat2, ...] [--unused] [--all]

Les paramètres sont :  
[cat1, cat2, ...] : Une ou plusieurs catégories. Utiliser des guillemets si le nom comporte plusieurs mots.  
Par défaut, toutes les catégories ont l'indicateur "utilisée" à vrai ; utiliser l'option --unused pour que cet indicateur soit valorisé à faux.
Ce paramètre est facultatif avec l'option -all

Cet exemple va créer les 3 catégories "Boissons" "Produits laitiers" "Charcuteries" :  

    python manage.py loadcats Boissons "Produits laitiers" Charcuteries

[--unused] :  Utiliser cette option pour rendre les catégories créées ou modifiées unitilisées

[--all] : Modifie toutes les catégories existantes.  
Utilisé seule, cette option rend toutes les catégories "utilisées" ; si l'option [--unused] est également utilisée, alors toutes les catégories seront modifiées pour être "inutilisées"
