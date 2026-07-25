# Financial Docs RAG

Un système RAG (*Retrieval-Augmented Generation*) simple pour poser des
questions en langage naturel à des documents financiers, et obtenir des
réponses ancrées dans le texte source.

*A simple RAG system to ask natural-language questions about financial
documents and get answers grounded in the source text.*

## Le pipeline / The pipeline

| # | Étape | Statut |
|---|-------|--------|
| 1 | Charger le document, extraire le texte | ✅ fait |
| 2 | Découper en passages (chunking) | ✅ fait |
| 3 | Vectoriser les passages (embeddings) + indexer | ✅ fait |
| 4 | Vectoriser la question | ⬜ à venir |
| 5 | Recherche des passages pertinents (retrieval) | ⬜ à venir |
| 6 | Génération de la réponse ancrée | ⬜ à venir |
| 7 | Affichage avec la source | ⬜ à venir |

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation (état actuel)

```bash
# 1. Générer un PDF de test (mémo d'investissement fictif)
python data/make_sample_pdf.py

# 2. Extraire le texte du PDF
python src/step1_load.py data/sample_memo.pdf

# 3. Découper le texte en passages (chunking)
python src/step2_chunk.py data/sample_memo.pdf

# 4. Vectoriser les passages et les indexer dans Chroma
python src/step3_index.py data/sample_memo.pdf
```

Remplace `data/sample_memo.pdf` par tes propres documents financiers
quand tu veux — le code fonctionne avec n'importe quel PDF texte.

### Chunking (étape 2)

Le texte est découpé en passages de **500 caractères** avec un
**chevauchement de 100 caractères** (20%) entre passages consécutifs.
Compromis retenu : assez court pour que chaque passage porte une seule
idée (précision de la recherche), assez long pour garder un chiffre
avec son contexte ; l'overlap évite qu'une idée à cheval sur la
frontière entre deux passages devienne invisible à la recherche.
Chaque chunk garde le numéro de la page dont il provient, pour citer
la source plus tard.

*The text is split into 500-character passages with a 100-character
(20%) overlap. Trade-off: short enough that each passage carries one
idea (search precision), long enough to keep a figure with its
context; the overlap prevents an idea straddling two passages from
becoming invisible to search. Each chunk keeps its source page number
for later citation.*

### Embeddings + indexation (étape 3)

Les chunks sont vectorisés avec le modèle local **all-MiniLM-L6-v2**
(format ONNX, fonction d'embedding par défaut de Chroma) : gratuit,
tourne offline, pas de clé API à gérer. Le modèle (~80 Mo) est
téléchargé automatiquement au premier lancement — une connexion
internet est nécessaire cette première fois seulement. L'index est
persisté sur disque dans `chroma_db/` (créé automatiquement, ignoré par
Git) ; relancer le script sur le même document met à jour les chunks
existants (upsert) au lieu de les dupliquer.

*Chunks are embedded with the local **all-MiniLM-L6-v2** model (ONNX
format, Chroma's default embedding function): free, runs offline, no
API key needed. The model (~80 MB) is downloaded automatically on
first run — internet access is only needed that first time. The index
is persisted to disk under `chroma_db/` (auto-created, git-ignored);
re-running the script on the same document upserts existing chunks
instead of duplicating them.*

## Structure

```
financial-docs-rag/
├── data/
│   ├── make_sample_pdf.py   # génère un document de test
│   └── sample_memo.pdf      # mémo d'investissement fictif
├── src/
│   ├── step1_load.py        # étape 1 : chargement + extraction
│   ├── step2_chunk.py       # étape 2 : découpage en passages (chunking)
│   └── step3_index.py       # étape 3 : embeddings + indexation Chroma
├── requirements.txt
└── README.md
```
