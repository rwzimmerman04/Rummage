# main.py
# Entry point for the CLI version of Rummage
# ===========================================================

import argparse
import os
import re
import pathlib
import whoosh.index

from indexer import index_documents
from searcher import search_index
from multiprocessing import freeze_support

# Define constants
BASE_DIR = pathlib.Path(__file__).parent.parent
INDEX_DIR = str(BASE_DIR / ".index")

def print_results(matches):
    """
    Cleanly prints search results to the terminal.
    Strips HTML tags from snippets for readable format.
    """
    
    # Check if we found matches
    if len(matches) == 0:
        print("No matches found!")
        return

    # Print confirmation: match count
    print(f"Found {len(matches)} results!")

    # Report the results
    for m in matches:
        clean = re.sub(r'<[^>]+>', '', m["snippet"])
        print(f" {m['filename']} | page {m['page']}")   
        print(f" {clean}")
        print()

def main():

    # Create the argumnet parser
    parser = argparse.ArgumentParser(
        prog = 'Rummage',
        description = 'Search files and folders for keywords and phrases.'
    )

    # Add arguments to the parser
    parser.add_argument('-d', '--dir',          help='Path to folder or file to search',            default=None)
    parser.add_argument('-q', '--query',        help='Keyword or phrase to search for',             default=None)
    parser.add_argument('-m', '--mode',         help='Search mode: recursive, folder, or file',     default='recursive')
    parser.add_argument('-r', '--reindex',      help='Force a rebuild of the index',                default=False,              action='store_true')

    # Retrieve the arguments
    args = parser.parse_args()

    # Index if --reindex flag is set or no index exists yet
    if args.reindex or not whoosh.index.exists_in(INDEX_DIR):
        if args.dir is None:
            print("Error: --dir is required to build the index.")
            return
        print("Indexing documents...")
        index_documents(args.dir, INDEX_DIR, args.mode)
        print("Indexing Complete!")

    # Search if a query was provided
    if args.query is not None:
        if not whoosh.index.exists_in(INDEX_DIR):
            print("Error: No index found. Run with --reindex first.")
            return
        matches = search_index(args.query, INDEX_DIR)
        print_results(matches)
    else:
        print("No query provided! Use -q option to search.")


if __name__ == "__main__":
    freeze_support()
    main()