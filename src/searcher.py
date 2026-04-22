# searcher.py 
# Handles querying the Whoosh index and returning results
# ===========================================================

import whoosh.index
from whoosh.qparser import QueryParser

def search_index(query_string, index_dir):
    idx = whoosh.index.open_dir(index_dir)

    # If index is empty, return an emty array
    if idx.doc_count() == 0:
        return []
    
    # Search the index documents for matching query_string
    with idx.searcher() as searcher:
        # Build the query against the content field
        query = QueryParser("content", idx.schema).parse(query_string)
        results = searcher.search(query)

        # Create an array of match dictionaries
        matches = []
        for r in results:
            matches.append({
                "filename": r["filename"],
                "page": r["page"],
                "snippet": r.highlights("content") # Snippet with matched words wrapped in <b>, leave <b> in for the GUI :)
            })
        return matches


