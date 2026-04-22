# test_index.py
# Quick test check for the indexer and searcher
# ===================================================

from indexer import index_documents
from searcher import search_index

INDEX_PATH = "../.index"
FOLDER_PATH = "../tests"
QUERY = "holy knight"

# Build the index
idx = index_documents(FOLDER_PATH, INDEX_PATH)
print("Completed Indexing")

# Search the index
matches = search_index("holy knight", "../.index")
print(f"Found {len(matches)} results:")

# Report the results
for m in matches:
    print(m["filename"], m["page"], m["snippet"])
