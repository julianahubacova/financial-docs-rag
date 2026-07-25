"""
Étape 3 du pipeline RAG — Vectoriser les passages et les indexer dans Chroma.

Objectif : transformer chaque chunk de texte (sortie de step2_chunk.py) en
vecteur numérique (embedding), et le stocker dans une base vectorielle
persistante (Chroma) avec ses métadonnées (page, source), pour permettre
la recherche par similarité à l'étape 5.

Choix d'embeddings : modèle local (all-MiniLM-L6-v2, format ONNX, ~80 Mo),
via la fonction d'embedding par défaut de Chroma. Gratuit, tourne offline,
pas de clé API à gérer — adapté à un projet portfolio. Le modèle est
téléchargé automatiquement au premier lancement (une connexion internet
est nécessaire cette première fois seulement ; les lancements suivants
utilisent le modèle mis en cache localement).

Usage :
    python src/step3_index.py data/sample_memo.pdf
"""
import sys
import os

import chromadb
from chromadb.utils import embedding_functions

from step1_load import load_pdf_text
from step2_chunk import chunk_text

PERSIST_DIR = "chroma_db"       # dossier où Chroma persiste l'index sur disque
COLLECTION_NAME = "financial_docs"


def build_index(chunks: list[dict], source: str, persist_dir: str = PERSIST_DIR,
                 collection_name: str = COLLECTION_NAME, embedding_function=None):
    """Vectorise une liste de chunks et les indexe dans une collection Chroma.

    `embedding_function` est injectable : par défaut on utilise le modèle
    local de Chroma, mais on peut le remplacer (tests, ou une API
    d'embeddings différente plus tard) sans toucher au reste du code.

    `source` identifie le document d'origine (ex. nom du PDF) : il sert de
    préfixe aux IDs pour ne pas mélanger les chunks de plusieurs documents
    dans la même collection.
    """
    if embedding_function is None:
        embedding_function = embedding_functions.DefaultEmbeddingFunction()

    client = chromadb.PersistentClient(path=persist_dir)
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedding_function,
    )

    ids = [f"{source}::chunk{c['chunk_id']}" for c in chunks]
    documents = [c["text"] for c in chunks]
    metadatas = [
        {"source": source, "page": c["page"], "chunk_id": c["chunk_id"]}
        for c in chunks
    ]

    # upsert (pas add) : relancer le script sur le même document met à jour
    # les chunks existants au lieu d'échouer sur des IDs déjà présents.
    collection.upsert(ids=ids, documents=documents, metadatas=metadatas)

    return collection


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "data/sample_memo.pdf"

    text = load_pdf_text(path)
    chunks = chunk_text(text)
    collection = build_index(chunks, source=os.path.basename(path))

    print("=" * 60)
    print(f"Fichier         : {path}")
    print(f"Chunks indexés  : {len(chunks)}")
    print(f"Collection      : {COLLECTION_NAME} ({collection.count()} passages au total)")
    print(f"Dossier Chroma  : {PERSIST_DIR}/")
    print("=" * 60)
