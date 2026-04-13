# ATS Simulator

Simulateur d'ATS orienté recruteur pour évaluer la correspondance d'un CV avec une offre d'emploi.

## Ce que fait le simulateur

- **Adaptation automatique à l'offre**: extraction du titre, des compétences clés, des exigences (ex: années d'expérience, langue).
- **Évaluation multi-critères** inspirée des screenings ATS:
  - parsing & structure,
  - matching mots-clés offre/CV,
  - qualité du contenu,
  - impact/résultats mesurables.
- **Rapport détaillé**:
  - score global,
  - forces,
  - failles,
  - mots-clés trouvés/manquants.
- **Deux options clés**:
  - suggestions d'amélioration,
  - réécriture directe d'une version plus alignée du CV.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Lancement en 1 double-clic (Windows)

Un script `start.bat` est fourni pour tout faire automatiquement:
- création du venv,
- installation des dépendances,
- lancement de l'app Streamlit.

Double-cliquez simplement sur `start.bat`.

Note:
- Le premier lancement installe les dépendances (téléchargements normaux).
- Les lancements suivants réutilisent l'environnement et ne retéléchargent pas massivement.
- Pour forcer une mise à jour: `start.bat --update`.

## Tester via interface web (lien)

Lancez l'application:

```bash
streamlit run app.py
```

Puis ouvrez ce lien dans votre navigateur:

- http://localhost:8501

## Utilisation CLI

Préparer:
- un fichier texte d'offre (ex: `offer.txt`),
- un fichier texte de CV (ex: `cv.txt`).

Lancer l'analyse:

```bash
ats-sim --offer offer.txt --cv cv.txt
```

Sortie JSON:

```bash
ats-sim --offer offer.txt --cv cv.txt --json
```

Réécriture du CV + suggestions:

```bash
ats-sim --offer offer.txt --cv cv.txt --rewrite
```

Désactiver les suggestions:

```bash
ats-sim --offer offer.txt --cv cv.txt --no-suggestions
```

## Tests

```bash
python -m pytest
```

## Améliorations possibles

- Support natif PDF/DOCX avec extraction de texte robuste.
- Pondération par métier (Sales, Data, Product, etc.).
- Module de scoring configurable par entreprise.
- Interface web + historique d'analyses.
- Option de conformité (biais, neutralité, anonymisation).
