# indexer.py
# Handles extracting text from filesand buidling Whoosh index
# =======================================================================

import os
import pathlib
import pdfplumber
from whoosh.fields import Schema, ID, TEXT, NUMERIC
from whoosh.analysis import RegexTokenizer, LowercaseFilter
import whoosh.index

# Create analyzer: No stop filter (keep stopwords)
analyzer_no_stop = RegexTokenizer() | LowercaseFilter()

# List supported extensions
SUPPORTED_EXTENSIONS = [".pdf"]


def create_schema():
    """
    Builds and returns the Whoosh schema with the appropriate analyzer,
    """

    return Schema(
        path=ID(stored=True),                                   # Full file path, stored as-is
        filename=TEXT(stored=True),                             # Name of the specific file (For display)
        page=NUMERIC(stored=True),                              # Page number for display
        content=TEXT(analyzer=analyzer_no_stop, stored=True)    # Full page text, this is what the query searches
    )


def create_or_open_index(index_dir):
    """
    Creates the index directory if it doesn't already exist.
    Opens and returns the the existing index or creates a fresh one.
    """
    if not os.path.isdir(index_dir):
        os.makedirs(index_dir)
    
    # Always create  a fresh index, otherwise we get DUPLICATES!
    return whoosh.index.create_in(index_dir, create_schema(use_stopwords))


def index_documents(path, index_dir, mode="recursive"):
    """
    Retrieves files based on the selected mode, extracts text, 
    and writes each page as document into the Whoosh index
    """

    # Validate the mode, ensure the file is valid
    if mode == "file" and not pathlib.Path(path).is_file():
        raise ValueError(f"Mode is 'file' but the path is not a file!: {path}")

    # Retrieve the index
    idx = create_or_open_index(index_dir, use_stopwords)

    # Fetch the writer
    writer = idx.writer()

    # Create iterable list for searched files/folders
    files = []

    # Retrieve file(s)
    if mode == "recursive":
        files = pathlib.Path(path).rglob("*")
    elif mode == "folder":
        files = pathlib.Path(path).glob("*")
    elif mode == "file":
        files = [pathlib.Path(path)]    # Place the single item in a list, keeps the indexing logic clean

    # Iterate through list, indexing each file
    for _file in files:
        # Verify a valid extension has been selected
        if _file.suffix.lower() in SUPPORTED_EXTENSIONS:
            for page_num, text in extract_text_from_file(_file):
                # Skip the pages that have no extractable text
                if text is not None:
                    writer.add_document(
                        path=str(_file),
                        filename=_file.name,
                        page=page_num,
                        content=text
                    )

    writer.commit()     # Run at the end to persist data to index file


def extract_text_from_file(path):
    """
    Extract text from a file and return a list of (page_number, text) tuples
    """

    # Add page tuples here, if extension is invalid, this remains empty
    pages = []

    # Retrieve the extension
    ext = path.suffix.lower()
    if ext == ".pdf":
        # Handle PDF files here!
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text is not None:
                    pages.append((page.page_number, text))
    elif ext == ".txt":
        # Handle TXT files here!
        pass # To come later...
    elif ext == ".docx":
        # Handle DOCX files here!
        pass # To come later...
    return pages

# TEMP - Test the functionality of index_documents() and create_or_open_index()
# index_documents("../tests/", "../.index")
# print("Done!")