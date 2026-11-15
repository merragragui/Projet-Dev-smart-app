# Fiche de suivi des projets agents IA

Master • Présentation de l'avancement et plan de correction

**Groupe :** 5IADO G2 | **Projet n° :** 22 | **Date :** 15/11/2026

**Intitulé du projet :** Agent de contrôle qualité visuel

**Membres :** Omar TAZI, Meriam ERRAGRAGUI, Wissal LAMHAL

**Jalon examiné :** cadrage, choix du produit, grille de gravité, objectifs, dataset et analyse exploratoire

**Prochain point :** baseline + premier modèle entraîné et évalué sur le jeu de validation

> Légende des statuts : **Prévu** = décidé, pas encore commencé ; **Commencé** = code ou document écrit, pas encore démontré ; **Démontré** = scénario reproductible avec résultat vérifiable ; **Bloqué**. Les éléments marqués **[à confirmer]** doivent être vérifiés par le groupe avant la présentation (ne cocher « Démontré » que si vous avez réellement exécuté le script et gardé la preuve).

## Bilan et périmètre

**1. Quel problème métier traitez-vous, pour quel utilisateur et avec quel résultat attendu ?**

Problème : en sortie d'une ligne de laminage d'acier à chaud, les défauts de surface (craquelures, inclusions, rayures, etc.) sont contrôlés à l'œil ou de façon incomplète, ce qui laisse passer des pièces défectueuses ou fait rejeter des pièces saines. Utilisateur : le responsable qualité / l'opérateur de fin de ligne. Résultat attendu : un agent qui analyse l'image de chaque pièce, détecte et classe les défauts par type et gravité, décide ACCEPTER / REJETER / CONTRÔLE MANUEL, tient des statistiques par lot et alerte quand un type de défaut augmente (signe d'un outil usé ou d'un mauvais réglage). Critères de réussite mesurables (cahier des charges) : rappel sur défauts critiques ≥ 95 % ; mAP@0.5 ≥ 70 % ; faux rejets ≤ 5 % ; latence CPU < 100 ms/image (p95) ; cadence simulée ≥ 5 pièces/s ; perte de mAP < 10 points à ±30 % de luminosité.

**2. Quel périmètre MVP avez-vous retenu et quelles fonctions avez-vous reportées ?**

Inclus dans le MVP : un seul produit (surface d'acier laminé, dataset NEU-DET) ; 6 défauts ; détection et classification ; grille de gravité et moteur de décision à règles ; flux de production simulé à partir d'images ; base SQLite des résultats ; statistiques par lot et alerte de dérive ; dashboard Streamlit ; évaluation (mAP, rappel, matrice de confusion, latence, robustesse à l'éclairage).

Exclus ou reportés : caméra industrielle réelle et acquisition en ligne ; intégration automate / GPIO ; détection d'anomalies non supervisée (PatchCore / MVTec AD), maintenue en option bonus ; segmentation fine des défauts ; réentraînement automatique en production. Décision validée par le groupe : [à confirmer].

**3. Qu'aviez-vous prévu depuis le dernier point et qu'avez-vous réellement terminé ?**

| Fonction | Statut | Preuve |
| --- | --- | --- |
| Cahier des charges (produit, défauts, gravité, objectifs, contraintes) | Commencé / terminé [à confirmer] | `docs/cahier_des_charges.md` |
| Choix du dataset NEU-DET | Terminé | Section 5 de cette fiche |
| Environnement Python et dépôt Git | Terminé | Lien du dépôt, `requirements.txt` |
| Téléchargement NEU-DET | Terminé | Nombre de fichiers .jpg / .xml |
| Analyse exploratoire (`src/eda.py`) | Terminé | `data/annotations.csv`, `eda.png`, `exemples.png` |
| Split train/val/test et conversion YOLO (`src/prepare_yolo.py`) | Terminé | `data/yolo/`, `data.yaml`, `split_*.csv` |
| Vérification visuelle des labels YOLO | Prévu | Images avec boîtes dessinées |
| Baseline, entraînement YOLO, moteur de décision, base, dashboard | Prévu | Planning section 28 |

Bloqué : rien à ce jour. Pas d'accès à une caméra ni à un GPU local (voir question 10).

**4. Que peut-on exécuter aujourd'hui sans intervention manuelle cachée ?**

À ce jour, la chaîne de préparation des données : `python src/eda.py` puis `python src/prepare_yolo.py` à partir du dossier NEU-DET téléchargé, qui produit les statistiques, les graphiques et le dataset au format YOLO. Le scénario de bout en bout complet (image → détection → décision → base → dashboard) n'est pas encore exécutable : il est prévu aux jalons suivants. À présenter : la sortie du terminal de ces deux scripts.

**État général :** retard maîtrisable (le cadrage et les données sont en place ; l'entraînement et le pipeline de décision ne sont pas encore démontrés).

**Décision ou aide attendue de l'enseignant :** valider le choix de NEU-DET comme périmètre MVP et accepter une démonstration en flux simulé (sans caméra réelle), avec entraînement sur Google Colab / Kaggle et inférence sur CPU.

## Données et architecture

**5. Quel dataset ou corpus utilisez-vous exactement et comment y accède-t-on ?**

Dataset : NEU surface defect database (NEU-DET), université Northeastern (Chine), disponible sur Kaggle (recherche « NEU surface defect database », compte gratuit nécessaire). 1 800 images 200×200 px en niveaux de gris, 300 par classe, annotations de boîtes englobantes au format Pascal VOC (XML). Classes : crazing, inclusion, patches, pitted_surface, rolled-in_scale, scratches. Version / date de téléchargement : 15/11/2026. Licence : [Unknown ; usage académique]. Fichiers retenus : toutes les images et tous les XML ; stockés dans `data/raw/NEU-DET/`.

**6. Les données couvrent-elles réellement le problème posé ? Que simulez-vous ?**

Réel : images réelles de défauts sur acier laminé à chaud, avec labels de type et de position. Simulé : la ligne de production (on rejoue les images à cadence fixe avec identifiant de lot et horodatage), la caméra, et les variations d'éclairage (dégradation artificielle OpenCV : luminosité, ombres, flou). Limites : le dataset ne contient que des pièces défectueuses, donc pas de mesure directe des faux rejets sur pièces saines (piste : patchs sans défaut ou images saines de MVTec AD, sinon limite assumée) ; images petites et en niveaux de gris ; l'étiquette de gravité (critique / majeur / mineur) n'existe pas dans le dataset : elle est définie par notre grille métier, à justifier dans le rapport.

**7. Comment avez-vous nettoyé, annoté et séparé les données sans fuite ?**

Pipeline : `eda.py` lit tous les XML, associe chaque annotation à son image et construit `annotations.csv` (classe, coordonnées, aire relative) ; `prepare_yolo.py` convertit les boîtes au format YOLO (coordonnées normalisées) et crée `data/yolo/{images,labels}/{train,val,test}`. Annotations déjà fournies par le dataset : pas d'annotation manuelle, mais contrôle visuel d'un échantillon prévu. Split : 70 / 15 / 15, stratifié par classe, `random_state=42`, par image (une image n'est que dans un seul ensemble). Le jeu de test n'est utilisé qu'à l'évaluation finale. Limite à déclarer : des images peuvent provenir de plaques voisines, ce qui risque une légère fuite non détectable ; mesure prévue : contrôle des doublons exacts par hash d'image [à faire]. Exemples avant/après : [à ajouter : image + XML → image + boîte YOLO dessinée].

**8. Quelle insuffisance des données risque de fausser votre conclusion ?**

Principal risque : l'absence de pièces saines, qui rend les faux rejets non mesurables et peut surestimer la qualité réelle. Risques secondaires : biais de luminosité entre classes (le modèle pourrait apprendre l'éclairage plutôt que le défaut) et ressemblance visuelle entre classes (crazing / rolled-in_scale). Mesures : ajouter des images saines (MVTec AD ou patchs sans défaut) pour estimer le taux de faux rejets ; comparer la luminosité moyenne par classe dans l'EDA ; tester la robustesse avec des variations d'éclairage artificielles ; analyser la matrice de confusion.

**9. Quels composants fonctionnent et comment échangent-ils les données ?**

Architecture cible : Simulateur de ligne (dossier d'images) → Prétraitement (OpenCV) → Inférence (YOLO) → Moteur de décision (règles + seuils de confiance) → Base SQLite → Statistiques et alerte de dérive → Dashboard Streamlit. Modules : `acquisition`, `preprocessing`, `inference`, `decision`, `storage`, `analytics`, `dashboard`. Composants fonctionnels à ce jour : préparation des données (EDA, split, conversion YOLO). Les autres sont prévus. Échanges : appels de fonctions Python entre modules ; exemple de requête API (FastAPI) prévu pour l'inférence : `POST /predict` avec une image, réponse JSON `{decision, defauts:[{classe, gravite, confiance, bbox}], latence_ms}`.

**10. Pourquoi avez-vous choisi ces frameworks plutôt qu'une solution plus simple ?**

YOLO (Ultralytics) : détection + classification + localisation en un seul modèle, simple à entraîner, déclinaisons légères (n/s) compatibles avec une inférence CPU, export ONNX / OpenVINO. Une solution plus simple (seuillage OpenCV) sert de baseline mais ne sait pas classer six types de défauts. SQLite et Streamlit : mise en place rapide, sans serveur, suffisants pour le MVP. Ressources : pas de GPU local ni de caméra ; entraînement sur Google Colab / Kaggle, inférence sur CPU, ce qui sert aussi la contrainte de temps de traitement.

**11. Comment gérez-vous l'état, la mémoire, les erreurs et les reprises ?**

État : chaque pièce est une ligne en base (id, horodatage, lot, résultat, défauts, confiance, gravité, temps d'inférence, chemin d'image), ce qui sert de mémoire pour les statistiques et la dérive. Erreurs prévues : image illisible ou corrompue → pièce marquée CONTRÔLE MANUEL et erreur journalisée, sans arrêter la ligne ; modèle indisponible → mode dégradé en contrôle manuel ; reprise : le simulateur reprend à la dernière pièce enregistrée. État actuel : Prévu. Journal d'exécution et exemple d'échec traité : [à prévoir].

**Correction prioritaire sur les données ou la conception :** constituer ou identifier un jeu d'images saines pour mesurer les faux rejets, et contrôler les doublons entre train / val / test.

## Fonctionnement des agents et protocole

**12. Quelle décision l'agent prend-il et quels outils appelle-t-il ?**

Décision par pièce : ACCEPTER, REJETER ou CONTRÔLE MANUEL. Outils appelés : prétraitement OpenCV, modèle de vision YOLO, table de gravité (fichier de configuration), base SQLite, module de statistiques / alerte. Règles : aucun défaut → ACCEPTER ; défaut critique (crazing, inclusion) → REJETER ; défaut majeur (pitted_surface, rolled-in_scale) → CONTRÔLE MANUEL ; défaut mineur (scratches, patches) → ACCEPTER + signaler ; confiance entre 0,4 et 0,7 → CONTRÔLE MANUEL. Décision envisagée aussi selon la taille du défaut. Trace d'un scénario : Prévu.

**13. Quel résultat obtenez-vous avec des règles ou une chaîne sans agent ?**

La décision est déjà une chaîne de règles déterministes sur la sortie du modèle. La comparaison pertinente sera : (a) baseline OpenCV par seuillage, (b) classifieur simple, (c) YOLO, sur le même jeu de test et sur le même matériel CPU. Résultats : non mesurés à ce jour Prévu.

**14. Si plusieurs agents collaborent, quel rôle distinct remplit chacun ?**

Sans objet pour le MVP : le système est un pipeline à un seul agent de décision, sans LLM ni multi-agents. Un découpage en agents (inspection / décision / suivi statistique) n'apporterait pas de gain mesurable pour ce cas d'usage, et ajouterait de la latence. Option à discuter si le groupe veut une partie LLM : un agent d'explication des alertes de dérive.

**15. Comment vérifiez-vous une sortie du LLM avant de l'utiliser ?**

Pas de LLM dans le MVP, donc question sans objet pour un LLM. Équivalent pour la sortie du modèle de vision : validation du format (classes connues, boîtes dans l'image), seuil de confiance minimal, règle d'abstention (confiance faible → CONTRÔLE MANUEL), test métier sur des cas connus (rappel sur défauts critiques). Prévu.

**16. Quelles actions exigent une validation humaine et quelles limites imposez-vous ?**

Le REJET définitif d'un lot et toute modification des seuils ou de la grille de gravité demandent une validation humaine ; les cas ambigus (défauts majeurs, confiance faible) vont en contrôle manuel. Dans le MVP, l'agent n'agit sur aucun équipement réel : il trie dans des dossiers `accepte/`, `rejete/`, `manuel/` (simulation). Plafonds d'appels et de coût : non pertinents (modèle local, aucun appel payant).

**17. Quels tests prouvent que les fonctions annoncées marchent réellement ?**

À ce jour : aucun test automatisé [à confirmer]. Prévu : tests unitaires (pytest) sur la conversion de boîtes XML → YOLO, sur le moteur de décision (cas limites de confiance et de gravité), sur le stockage, et un test de bout en bout sur un petit lot simulé. Résultat daté et anomalies ouvertes : [à produire].

**18. Quels indicateurs avez-vous choisis et pourquoi conviennent-ils au projet ?**

| Indicateur | Pourquoi |
| --- | --- |
| Rappel sur défauts critiques | Un défaut critique laissé passer est le risque le plus grave |
| mAP@0.5, précision, rappel, F1 par classe | Qualité de la détection, sans masquer les classes rares |
| Matrice de confusion | Révèle les classes confondues |
| Taux de faux rejets | Coût des bonnes pièces rejetées |
| Latence moyenne et p95 (CPU) | Compatibilité avec la cadence de ligne |
| Perte de mAP sous variation d'éclairage | Robustesse industrielle |

Baseline : seuillage OpenCV. Protocole : jeu de test distinct jamais utilisé à l'entraînement, matériel CPU identique, mesures répétées pour la latence.

**Correction prioritaire sur l'agent ou les tests :** mettre en place la baseline et un premier entraînement YOLO mesuré, avec tests unitaires du moteur de décision.

## Résultats et déploiement

**19. Quels résultats chiffrés obtenez-vous sur un jeu de test distinct ?**

Aucun résultat de modèle à ce jour : l'entraînement est prévu au jalon 2. Taille de test prévue : environ 270 images (15 %). Les valeurs seront ajoutées dans le tableau « Résultats à comparer » ci-dessous.

**20. Quels sont vos trois échecs les plus importants et comment les expliquez-vous ?**

Sans objet à ce jour (pas encore de modèle). Échecs anticipés à surveiller : confusion crazing / rolled-in_scale, faible détection des rayures fines, dégradation sous variation d'éclairage. Entrées, sorties et causes : à documenter après la première évaluation.

**21. Quelles entrées difficiles ou hostiles avez-vous testées ?**

Pas encore testé. Prévu : image illisible ou de taille incorrecte, image sans défaut, image très sombre ou surexposée, plusieurs défauts sur une pièce, fichier modèle absent. Pas de prompt malveillant à tester (pas de LLM).

**22. Un autre groupe peut-il installer et lancer votre application ?**

Partiellement : les dépendances de préparation des données sont installables via pip. À faire : `requirements.txt` avec versions fixées, README avec commandes (`pip install -r requirements.txt`, `python src/eda.py`, `python src/prepare_yolo.py`), vérification sur une machine propre. [à confirmer]

**23. Quelle version est déployée et quel parcours avez-vous validé ?**

Aucun déploiement à ce jour. Version : commit [hash à indiquer]. Environnement : Python 3.10/3.11, Windows 11, CPU. Parcours validé : préparation des données Terminé. Parcours de bout en bout : prévu.

**24. Comment protégez-vous les secrets, les accès et les données ?**

Aucun secret dans le dépôt : `.gitignore` pour `venv/`, `data/` et les clés éventuelles (clé Kaggle `kaggle.json`, jamais commitée). Données publiques, sans donnée personnelle. Contrôle d'accès du dashboard : non nécessaire pour le MVP local ; à mentionner pour un déploiement réel. Journalisation : résultats et métadonnées de pièces uniquement.

### Résultats à comparer

| Indicateur | Baseline | Solution | Jeu ou scénario |
| --- | --- | --- | --- |
| Rappel défauts critiques | [non mesuré] | [non mesuré] | NEU-DET test (~270 images) |
| mAP@0.5 | [non mesuré] | [non mesuré] | NEU-DET test |
| Faux rejets | [non mesuré] | [non mesuré] | Images saines à constituer |
| Latence CPU p95 | [non mesuré] | [non mesuré] | NEU-DET test, CPU |
| Coût par scénario | 0 (local) | 0 (local) | Entraînement Colab gratuit |

Limites du passage au réel à expliquer : caméra et éclairage contrôlés, cadence réelle de la ligne, images plus grandes et en couleur, dérive des défauts dans le temps, nécessité de réentraîner et de valider avec des pièces saines.

## Contributions et corrections

**25. Quelle contribution chaque membre peut-il présenter et expliquer ?**

| Membre | Contribution | Choix technique à expliquer |
| --- | --- | --- |
| Omar TAZI | cahier des charges, grille de gravité, objectifs | justification des seuils et de la gravité |
| Meriam ERRAGRAGUI | EDA, analyse des données | découpage stratifié par classe |
| Wissal LAMHAL | conversion YOLO, vérification des labels | format YOLO et normalisation |

Preuve : commits Git par membre.

**26. Quel blocage menace le prochain jalon et de quelle aide avez-vous besoin ?**

Blocage potentiel : absence de GPU local pour entraîner ; solution : Google Colab / Kaggle, avec limites de session. Second point : absence d'images saines pour mesurer les faux rejets. Aide attendue : validation de l'utilisation d'images MVTec AD ou de patchs sans défaut comme pièces saines.

**27. Quelle affirmation ou fonctionnalité devez-vous corriger après cette revue ?**

À corriger : ne pas annoncer de résultat de détection tant qu'aucun modèle n'est évalué sur le test ; clarifier que la ligne et la caméra sont simulées ; préciser que la gravité est définie par notre grille et non fournie par le dataset ; compléter les placeholders de cette fiche après exécution des scripts.

**28. Quelles sont vos trois prochaines actions prioritaires ?**

voir « Plan de correction à valider » ci-dessous

**29. Faut-il réduire le périmètre ou revoir le choix des données ou des outils ?**

Pas de réduction du périmètre à ce stade : un produit, six défauts, flux simulé. Si l'entraînement prend du retard, on reporte en priorité le dashboard avancé et l'option anomalies non supervisée, en gardant la détection, la décision et les statistiques de base. Le choix de NEU-DET est maintenu.

**30. Quelle preuve présenterez-vous lors du prochain point d'avancement ?**

Une démonstration reproductible : lancer l'évaluation d'un modèle YOLO entraîné sur le jeu de test, afficher le tableau baseline / YOLO (mAP@0.5, rappel critique, latence CPU p95) et la matrice de confusion, puis faire passer 20 images du test dans le moteur de décision avec le résultat ACCEPTER / REJETER / MANUEL pour chacune.

### Plan de correction à valider

| Action prioritaire | Responsable | Échéance | Preuve de correction |
| --- | --- | --- | --- |
| 1. Exécuter `eda.py` et `prepare_yolo.py`, vérifier visuellement 10 labels YOLO, committer README + requirements.txt | [nom] | [date] | `annotations.csv`, `data.yaml`, 10 images avec boîtes dessinées, dépôt Git à jour |
| 2. Entraîner la baseline OpenCV et YOLOv8n sur Colab, évaluer sur val puis test | [nom] | [date] | Tableau mAP@0.5, rappel par classe, matrice de confusion, latence CPU |
| 3. Coder le moteur de décision avec tests pytest et le simulateur de ligne | [nom] | [date] | Tests au vert, journal d'exécution sur 50 images, dossiers accepte / rejete / manuel |

**Décision de la revue :** corriger avant le prochain jalon

**Commentaire de l'enseignant :** [à compléter]