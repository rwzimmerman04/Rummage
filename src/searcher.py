import whoosh.index
from whoosh.qparser import QueryParser

def search_index(query_string, index_dir):
    idx = whoosh.index.open_dir(index_dir)

    # Check if any documents were created
    if idx.doc_count() == 0:
        return []
    
    # Search the index documents for matching query_string
    with idx.searcher() as searcher:
        query = QueryParser("content", idx.schema).parse(query_string)
        results = searcher.search(query)

        matches = []
        for r in results:
            matches.append({
                "filename": r["filename"],
                "page": r["page"],
                "snippet": r.highlights("content")
            })
        return matches


