# searcher.py 
# Handles querying the Whoosh index and returning results
# ===========================================================

import whoosh.index
from whoosh.highlight import SentenceFragmenter
from whoosh.analysis import RegexTokenizer, LowercaseFilter
from whoosh.qparser import QueryParser, OrGroup

def search_index(query_string, index_dir, limit=30, use_stopwords=False, search_mode="all"):
    """
    Search the index for a keyword or phrase.
    Returns a list of dicts with filename, page, and snippet.

    search_mode options:
        "all"    — all words must appear on the page (default)
        "exact"  — words must appear together as an exact phrase
        "any"    — any of the words may appear, ranked by how many match
    """
    idx = whoosh.index.open_dir(index_dir)

    # If the index is empty, nothing to search
    if idx.doc_count() == 0:
        return []

    with idx.searcher() as searcher:

        # Build the query based on the selected search mode
        if search_mode == "exact":
            # Wrap in quotes to enforce exact phrase matching
            query = QueryParser("content", idx.schema).parse(f'"{query_string}"')

        elif search_mode == "any":
            # Use OrGroup so pages matching any word are returned
            # Results are still ranked by how many terms match (BM25F)
            parser = QueryParser("content", idx.schema, group=OrGroup)
            query = parser.parse(query_string)

        else:
            # Default "all" mode — all terms must appear on the page (AND)
            query = QueryParser("content", idx.schema).parse(query_string)

        # Execute the search with optional result cap
        results = searcher.search(query, limit=limit)

        # Use sentence boundaries for cleaner snippets
        results.fragmenter = SentenceFragmenter()

        # Build a clean list of match dictionaries
        matches = []
        for r in results:
            matches.append({
                "filename": r["filename"],
                "page": r["page"],
                "snippet": r.highlights("content", top=1)  # <b> tags kept for GUI rendering
            })
        return matches