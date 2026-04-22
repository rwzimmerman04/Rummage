# test_index.py
# Quick test check for the indexer and searcher
# ===================================================

from indexer import index_documents
from searcher import search_index

INDEX_PATH = "../.index"
# FILE_PATH = "../tests/Rummage_test.pdf"         # Use for testing single file search
FILE_PATH = "../tests"                        # Use for testing folder search and also errored file search
# MODE = "file"                                   # Use for testing single file search
MODE = "recursive"                            # Use for testing folder search and also errored file search
QUERY = "holy knight"

# Build the index
idx = index_documents(FILE_PATH, INDEX_PATH, MODE)
print("Completed Indexing")

# Search the index
matches = search_index(QUERY, INDEX_PATH)
print(f"Found {len(matches)} results:")

# Report the results
for m in matches:
    print(m["filename"], m["page"], m["snippet"])
