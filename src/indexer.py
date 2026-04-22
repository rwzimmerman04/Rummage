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


def index_documents(folder_path, index_dir):
    idx = create_or_open_index(index_dir)

    # Fetch the writer
    writer = idx.writer()

    for path in pathlib.Path(folder_path).rglob("*.pdf"):
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text is not None:
                    writer.add_document(
                        path=str(path),
                        filename=path.name,
                        page=page.page_number,
                        content=text
                    )

    writer.commit()     # Run at the end to persist the index


index_documents("../tests/", "../.index")
print("Done!")

