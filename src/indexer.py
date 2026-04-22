# indexer.py
# Handles extracting text from filesand buidling Whoosh index
# =======================================================================

import os
import pathlib
import pdfplumber
from whoosh.fields import Schema, ID, TEXT, NUMERIC
import whoosh.index

# Schema defines the structure of each indexed document
# One document = one page of one file
schema = Schema(path=ID(stored=True),           # Full file path, stored as-is
                filename=TEXT(stored=True),     # Name of the specific file (For display)
                page=NUMERIC(stored=True),      # Page number for display
                content=TEXT(stored=True))      # Full page text, this is what the query searches

# Create the .index folder if does not exist for saving indexes.
def create_or_open_index(index_dir):
    """
    Creates the index directory if it doesn't already exist.
    Opens and returns the the existing index or creates a fresh one.
    """
    if not os.path.isdir(index_dir):
        os.makedirs(index_dir)
    
    # Create a fresh index or open the existing one
    if whoosh.index.exists_in(index_dir):
        return whoosh.index.open_dir(index_dir)
    else:
        return whoosh.index.create_in(index_dir, schema)


def index_documents(folder_path, index_dir):
    """
    Walks the folder path recursively, extracts text from every PDF page,
    then writes each page as a document into the Whoosh index
    """
    idx = create_or_open_index(index_dir)

    # Fetch the writer
    writer = idx.writer()

    for path in pathlib.Path(folder_path).rglob("*.pdf"):
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                # Skip the pages that have no extractable text
                if text is not None:
                    writer.add_document(
                        path=str(path),
                        filename=path.name,
                        page=page.page_number,
                        content=text
                    )

    writer.commit()     # Run at the end to persist the index


# TEMP - Test the functionality of index_documents() and create_or_open_index()
# index_documents("../tests/", "../.index")
# print("Done!")

