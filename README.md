# Rummage
Fast keyword and phrase search across large collections of documents. Built with Python, Whoosh, and customtkinter.

**Author:** Robert Zimmerman  
**Started:** April 2026

---

## What is Rummage?

Rummage lets you search through hundreds of documents at once without opening a single file manually. Type a keyword or phrase, and Rummage will tell you exactly which files and pages it appears in.

## Motivation

I have a large collection of tabletop game rulebooks. When I need to look something up, my only options were to guess which book it might be in, or open each one and use Ctrl+F. Rummage solves this by allowing me to search my entire collection from a single interface - no files need to be opened until I find exactly what I'm looking for. So, next time I want to play an unholy paladin sworn by blood to a storm god, I don't have to manually search through a dozen books of templates and character rules for the one entry that has exactly what I need at the time.

---

## Features

- Keyword and phrase search across large collection of documents
- Inverted index means searches are near-instant after the index is built
- Recursive folder search, single folder, and single file modes
- Fast parallel PDF extraction via pymupdf
- Background threading means GUI stays responsive during indexing
- Supports PDF (more formats on the way!)
- Simple GUI — no need to enter commands in the CLI, great for non-technical users :)

---

## Installation

...

---

## Usage

- `holy knight`     — finds pages containing both words anywhere on the page
- `"holy knight"`   — finds exact phrase only

---

## How it works

Rummage builds an **Inverted Index** -> A map of every word in every document to the exact file and page it appears on. Once built, searching is near-instant regardless of collection size because Rummage looks up words in the index rather than scanning every file for each query - unlike a certain previous Java implementation that shall not be named. \**looks side to side*\*

Phrase seaches like `"holy knight"` work using positional indexing where Whoosh records positions of every word, so it can verify that "holy" and "knight" are indeed next to one another.

When indexing a folder, Rummage extracts text from all files in parallel using Python's multiprocessing pool and pymupdf, which is a C-based PDF library and significantly faster than pure Python alternatives. Once extraction is complete, pages are written to the Whoosh index single-threaded, this is because Whoosh's writer is not process-safe. In the GUI, indexing runs on a background thread so the interface stays responsive and shows live progress while your collection is being indexed to verify nothing has frozen up on you.

---

## Why Whoosh?

Whoosh is a Python search library that handles all the hard work of building and querying an inverted index. Rather than scanning every doc on every query, *cough cough*, Whoosh builds a map of every meaningful word to exact file and page it appears on- making searches near-instant. Now, what do I mean *meaningful*? More on that later.

### What does Whoosh handle exactly?

- **Inverted Index:** Maps a word to it's locations so lookups 
  are O(1) instead of O(everything).
- **Positional Indexing:** Records where each word appears within 
  a page, enabling phrase search like `"holy knight"` to find those 
  two words together, not just anywhere on the page.
- **Case Insensitive:** "Holy", "holy", and "HOLY" all match up to the
  same entry.
- **Delta Encoding:** Word positions are stored as compressed 
  differences rather than raw numbers, keeping the index much smaller
  than the original media.

### Why not just Ctrl+F this?

Well, as I said earlier in the motivation, Ctrl+F is completely fine, if you only have a few books or know which book to look in, and Ctrl+F is still useful once this tool has identified the books you query appears in. However, if you have a **large** collection of books, you may not feel like spending you precious time click open and closing each book, jumping from one occurrence to the next. This way, you can spend that time reading about the topic instead.

### Wait! Won't we just have a bloated index with filler words?

**Yes — and this is intentional.** Whoosh is perfectly capable of dropping filler words like "the", "a", "is" from the index, in fact it does this be default, it keeps the index slim and improves build time. However, Rummage deliberately keeps them, why?

The reason comes down to a real world use case. Tabletop rulebooks and many other documents have lots of game terms that contain filler words — "to hit", "at will", "is prone", "a critical". If these filler words, or stop words as Whoosh calls them, were filtered, searching for `"to hit"` would silently become a search for just `"hit"`, returning every page that mentions hit anywhere in any context at all rather than the specific mechanic you were looking for.

Instead, Rummage keeps all words in the index and lets you control precision through searching the syntax:

- `holy knight` — finds pages where both words appear anywhere
- `to hit`      — finds pages where "hit" appears
- `"to hit"`    — finds the exact phrase, "to" and all

---

## Project Structure 

```
Rummage/
├── .index/                 # Ephemeral folder for index storage
├── src/
│   ├── indexer.py          # Builds and populates the whoosh index
│   ├── searcher.py         # Queries the index
│   ├── main.py             # CLI entry point
│   └── gui.py              # customtkinter GUI (IN PROGRESS)
├── tests/
│   └── Rummage_test.pdf    # Simple PDF file for sanity checks after logic adjustments
├── requirements.txt        # Dependencies to import for build
└── README.md               # The document you are reading, lol
```

---

## Development Roadmap

- [X] PDF support
- [X] Phrase search via positional indexing
- [X] Recursive, folder, and single file modes
- [X] CLI interface and argument parser
- [X] Parallel extraction with pymupdf
- [X] customtkinter GUI
- [X] Background threading — UI stays responsive during indexing
- [X] Live indexing progress in status bar
- [X] Summary and context results panels
- [X] Implement results save function
- [ ] Windows executable via PyInstaller
- [ ] DOCX support
- [ ] TXT support
- [ ] EPUB support
- [ ] Incremental indexing — only re-index changed files
- [ ] Stemming toggle for root word matching e.g. "knights" → "knight"
- [ ] Open PDF to exact page from results (maybe)
- [ ] Remember last used folder between sessions

---

## License

MIT