# Imports
import os
import pathlib
import pdfplumber
from whoosh.fields import Schema, ID, TEXT, NUMERIC
import whoosh.index

# Define a whoosh schema for the index
schema = Schema(path=ID(stored=True),
                filename=TEXT(stored=True),
                page=NUMERIC(stored=True),
                content=TEXT(stored=True))

# Create the .index folder if does not exist for saving indexes.
def create_or_open_index(index_dir):
    # If does not exist, create the index directory
    if not os.path.isdir(index_dir):
        os.makedirs(index_dir)
    
    # Create a fresh index or open the existing one
    if whoosh.index.exists_in(index_dir):
        return whoosh.index.open_dir(index_dir)
    else:
        return whoosh.index.create_in(index_dir, schema)





idx = create_or_open_index(".index")
print("Index ready:", idx)

