# searcher.py 
# Handles querying the Whoosh index and returning results
# ===========================================================

import whoosh.index
from whoosh.highlight import SentenceFragmenter
from whoosh.qparser import QueryParser

def search_index(query_string, index_dir, limit=30):
    """
    Search the index for a keyword or phrase.
    Returns a list of dicts with filename, page, and snippet.
    """
    idx = whoosh.index.open_dir(index_dir)

    # If the index is empty, nothing to search
    if idx.doc_count() == 0:
        return []

    with idx.searcher() as searcher:
        # Build the query
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