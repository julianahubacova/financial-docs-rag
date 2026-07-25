"""
Étape 2 du pipeline RAG — Découper le texte en passages (chunking).

Objectif : transformer le texte brut (avec marqueurs [page N]) produit par
step1_load.py en une liste de petits passages, chacun assez précis pour être
retrouvé individuellement par la recherche, et assez court pour donner un
embedding net.

Compromis taille / overlap :
- Chunk trop grand → l'embedding mélange plusieurs idées, la recherche
  devient floue, la citation de page perd de sa précision.
- Chunk trop petit → une idée (ex. un chiffre + son contexte) est coupée
  en deux, l'embedding ne capture rien d'utile.
- L'overlap (chevauchement) sert uniquement à éviter qu'une idée à cheval
  sur la frontière entre deux chunks soit invisible aux deux.

Valeurs par défaut retenues : 500 caractères par chunk, 100 de chevauchement
(soit 20%). Ajustables en paramètres si le retrieval donne de mauvais
résultats plus tard.

Usage :
    python src/step2_chunk.py data/sample_memo.pdf
"""
import sys
import re

# Import relatif simple : step1_load.py est dans le même dossier src/.
from step1_load import load_pdf_text

CHUNK_SIZE = 500     # caractères par chunk
CHUNK_OVERLAP = 100  # caractères de chevauchement entre deux chunks consécutifs


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE,
               overlap: int = CHUNK_OVERLAP) -> list[dict]:
    """Découpe le texte extrait en chunks, en conservant leur page d'origine.

    Le texte d'entrée contient des marqueurs "[page N]" insérés par
    load_pdf_text(). On les repère d'abord pour savoir, à chaque position
    du texte, sur quelle page on se trouve — puis on découpe le texte
    (marqueurs retirés) en fenêtres glissantes de `chunk_size` caractères
    avec un `overlap` entre chaque fenêtre.

    Retourne une liste de dicts : {"text": str, "page": int, "chunk_id": int}
    """
    page_starts = _find_page_boundaries(text)
    clean_text = re.sub(r"\[page \d+\]\n?", "", text)

    # On reconstruit la correspondance position-dans-clean_text → page,
    # car retirer les marqueurs décale les indices.
    offsets = _map_offsets_to_pages(text, page_starts)

    chunks = []
    start = 0
    chunk_id = 0
    step = chunk_size - overlap

    while start < len(clean_text):
        end = start + chunk_size
        window = clean_text[start:end]

        # On évite de couper au milieu d'un mot : si on n'est pas à la fin
        # du texte, on recule jusqu'au dernier espace du fragment.
        if end < len(clean_text):
            last_space = window.rfind(" ")
            if last_space > 0:
                end = start + last_space
                window = clean_text[start:end]

        window = window.strip()
        if window:
            chunks.append({
                "chunk_id": chunk_id,
                "text": window,
                "page": _page_for_position(start, offsets),
            })
            chunk_id += 1

        start += step

    return chunks


def _find_page_boundaries(text: str) -> list[tuple[int, int]]:
    """Retourne [(position_dans_text, numero_page), ...] pour chaque marqueur."""
    return [(m.start(), int(m.group(1)))
            for m in re.finditer(r"\[page (\d+)\]", text)]


def _map_offsets_to_pages(text: str, page_starts: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Convertit les positions des marqueurs dans `text` vers des positions
    équivalentes dans le texte nettoyé (marqueurs retirés).

    Retourne [(position_dans_clean_text, numero_page), ...].
    """
    offsets = []
    removed_so_far = 0
    for pos, page_num in page_starts:
        marker = f"[page {page_num}]\n"
        clean_pos = pos - removed_so_far
        offsets.append((clean_pos, page_num))
        removed_so_far += len(marker)
    return offsets


def _page_for_position(pos: int, offsets: list[tuple[int, int]]) -> int:
    """Trouve le numéro de page correspondant à une position dans le texte nettoyé."""
    page = offsets[0][1] if offsets else 1
    for clean_pos, page_num in offsets:
        if clean_pos <= pos:
            page = page_num
        else:
            break
    return page


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "data/sample_memo.pdf"

    text = load_pdf_text(path)
    chunks = chunk_text(text)

    print("=" * 60)
    print(f"Fichier          : {path}")
    print(f"Chunks générés   : {len(chunks)}")
    print(f"Taille / overlap : {CHUNK_SIZE} / {CHUNK_OVERLAP} caractères")
    print("=" * 60)

    for c in chunks:
        print(f"\n--- Chunk {c['chunk_id']} (page {c['page']}, "
              f"{len(c['text'])} car.) ---")
        print(c["text"])
