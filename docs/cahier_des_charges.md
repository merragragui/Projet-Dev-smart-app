# Cahier des charges : Agent de contrôle qualité visuel

## 1. Contexte
Contrôle qualité en sortie de ligne de laminage d'acier. Objectif : détecter,
classer et trier automatiquement les pièces selon les défauts de surface.

## 2. Périmètre
- Produit : surface d'acier laminé à chaud (dataset NEU-DET)
- 6 défauts : crazing, inclusion, patches, pitted_surface, rolled-in_scale, scratches
- Hors périmètre : caméra réelle (flux simulé), intégration automate

## 3. Grille de gravité et décision
| Défaut | Gravité | Décision |
|---|---|---|
| crazing | Critique | REJETER |
| inclusion | Critique | REJETER |
| pitted_surface | Majeur | CONTRÔLE MANUEL |
| rolled-in_scale | Majeur | CONTRÔLE MANUEL |
| scratches | Mineur | ACCEPTER + signaler |
| patches | Mineur | ACCEPTER + signaler |
Règle complémentaire : confiance faible (0,4 à 0,7) → CONTRÔLE MANUEL.

## 4. Objectifs chiffrés
- Rappel défauts critiques ≥ 95 %
- mAP@0.5 ≥ 70 %
- Faux rejets ≤ 5 %
- Latence CPU < 100 ms/image (p95)
- Cadence simulée ≥ 5 pièces/s
- Perte de mAP < 10 points à ±30 % de luminosité

## 5. Contraintes
CPU uniquement en local ; entraînement sur Colab/Kaggle ; pas de caméra
(flux simulé à partir d'images).

## 6. Stack
Python, OpenCV, PyTorch, Ultralytics YOLO, SQLite, Streamlit, MLflow.
