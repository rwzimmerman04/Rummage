# indexer.py
# Handles extracting text from filesand buidling Whoosh index
# =======================================================================

import os
import pathlib
import fitz
from whoosh.fields import Schema, ID, TEXT, NUMERIC
from whoosh.analysis import RegexTokenizer, LowercaseFilter
from multiprocessing import Pool, cpu_count, freeze_support
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
    return whoosh.index.create_in(index_dir, create_schema())


def _extract_worker(path):
    """
    Worker function for parallel extraction.
    Called by each process in the pool.
    Returns a list of (path, filename, page_num, text) tuples.
    """
    results = []
    for page_num, text in extract_text_from_file(path):
        results.append((str(path), path.name, page_num, text))
    return results


def index_documents(path, index_dir, mode="recursive", progress_callback=None):
    """
    Retrieves files based on the selected mode, extracts text, 
    and writes each page as document into the Whoosh index
    """
    freeze_support()

    # Validate the mode, ensure the file is valid
    if mode == "file" and not pathlib.Path(path).is_file():
        raise ValueError(f"Mode is 'file' but the path is not a file!: {path}")

    # Retrieve the index
    idx = create_or_open_index(index_dir)
    # Fetch the writer
    writer = idx.writer()

    # Build file list
    if mode == "recursive":
        files = [f for f in pathlib.Path(path).rglob("*") 
                 if f.suffix.lower() in SUPPORTED_EXTENSIONS]
    elif mode == "folder":
        files = [f for f in pathlib.Path(path).glob("*") 
                 if f.suffix.lower() in SUPPORTED_EXTENSIONS]
    elif mode == "file":
        files = [pathlib.Path(path)]

    total = len(files)

    # Extract text in parallel
    with Pool(processes=cpu_count()) as pool:
        results = pool.map(_extract_worker, files)

    # Write to index single-threaded, report progress after each file
    for i, file_results in enumerate(results):
        for _path, filename, page_num, text in file_results:
            writer.add_document(
                path=_path,
                filename=filename,
                page=page_num,
                content=text
            )
        if progress_callback:
            progress_callback(i + 1, total)

    # Notify that we are now writing the index
    if progress_callback:
        progress_callback(total, total, writing=True)

    writer.commit()


def extract_text_from_file(path):
    """
    Extract text from a file and return a list of (page_number, text) tuples
    """

    # Add page tuples here, if extension is invalid, this remains empty
    pages = []

    # Retrieve the extension
    ext = path.suffix.lower()
    if ext == ".pdf":
        with fitz.open(path) as pdf:
            for page in pdf:
                text = page.get_text()
                if text.strip():
                    pages.append((page.number + 1, text))
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