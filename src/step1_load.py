"""
Étape 1 du pipeline RAG — Charger un document et en extraire le texte.

Objectif : transformer un PDF en texte brut propre, prêt à être découpé
à l'étape 2 (chunking). On ne fait RIEN d'intelligent ici : on lit, on
nettoie un peu, on rend une chaîne de caractères.

On utilise pdfplumber plutôt que pypdf parce qu'il préserve mieux la
mise en page (l'ordre des mots, les espaces) sur des documents texte.

Usage :
    python src/step1_load.py data/sample_memo.pdf
"""
import sys
import re
import pdfplumber


def load_pdf_text(pdf_path: str) -> str:
    """Ouvre un PDF et retourne tout son texte, nettoyé.

    Retourne une seule chaîne (tout le document). On ajoute un séparateur
    entre les pages pour garder une trace des frontières de page — utile
    plus tard si on veut citer « page X » dans les réponses.
    """
    pages_text = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            # extract_text() rend None si la page est vide (ex. page scannée
            # sans texte). On protège contre ça avec "or ''".
            raw = page.extract_text() or ""
            cleaned = _clean(raw)
            if cleaned:
                pages_text.append(f"[page {page_number}]\n{cleaned}")

    return "\n\n".join(pages_text)


def _clean(text: str) -> str:
    """Nettoyage léger : espaces multiples, sauts de ligne en trop.

    On reste minimal exprès. Un sur-nettoyage (ex. tout mettre sur une
    ligne) détruirait des repères utiles. On enlève juste le bruit.
    """
    # Remplace toute suite d'espaces/tabs par un seul espace
    text = re.sub(r"[ \t]+", " ", text)
    # Réduit 3 sauts de ligne ou plus à 2 (garde les paragraphes)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Enlève les espaces en début/fin de chaque ligne
    text = "\n".join(line.strip() for line in text.splitlines())
    return text.strip()


if __name__ == "__main__":
    # Chemin du PDF : donné en argument, sinon le mémo exemple par défaut.
    path = sys.argv[1] if len(sys.argv) > 1 else "data/sample_memo.pdf"

    text = load_pdf_text(path)

    # Petit rapport pour vérifier que l'extraction a marché.
    print("=" * 60)
    print(f"Fichier         : {path}")
    print(f"Caractères      : {len(text):,}")
    print(f"Mots (approx.)  : {len(text.split()):,}")
    print("=" * 60)
    print("\n--- Aperçu (500 premiers caractères) ---\n")
    print(text[:500])
    print("\n--- Fin de l'aperçu ---")
