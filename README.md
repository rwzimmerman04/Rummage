# Rummage
Fast keyword and phrase search across large collections of documents. Built with Python, Whoosh, and tkinter.

**Author:** Robert Zimmerman  
**Started:** April 2026

---

## What is Rummage?

Rummage lets you search through hundreds of documents at once without opening a single file manually. Type a keyword or phrase, and Rummage will tell you exactly which files, page number, and sentence it appears in.

## Motivation

I have a large collection of tabletop game rulebooks. When I need to look something up, my only options were to guess which book it might be in, or open each one and use Ctrl+F. Rummage solves this by allowing me to search my entire collection from a single interface - no files need to be opened until I find exactly what I'm looking for. So, next time I want to play an unholy paladin sworn by blood to a storm god, I don't have to manually search through a dozen books of templates and character rules for the one entry that has exactly what I need at the time.

---

## Features

- Keyword and phrase search across a large collection of documents
- Inverted index means searches are near-instant after the first index build
- Recursive folder search, single folder, and single file modes
- Supports PDF (more formats on the way!)
- Simple GUI - no need to enter commands in the CLI, great for non-technical users :)

---

## Installation

...

---

## Usage

...

---

## How it works

Rummage builds an **Inverted Index** -> A map of every word in every document to the exact file and page it appears on. Once built, searching is near-instant regardless of collection size because Rummage looks up words in the index rather than scanning every file for each query - unlike a certain previous Java implementation that shall not be named. \**looks side to side*\*

Phrase seaches like `"holy knight"` work using positional indexing where Whoosh records positions of every word, so it can verify that "holy" and "knight" are indeed next to one another, or at least in the same sentence (it returns the results by priority, FYI), not just anywhere on the page.

---

## Why Whoosh?

Whoosh is a Python search library that handles all the hard work of building and querying an inverted index. Rather than scanning every doc on every query, *cough cough*, Whoosh builds a map of every meaningful word to exact file and page it appears on- making searches near-instant. Now, what do I mean *meaningful*? More on that later.

### What does Whoosh handle exactly?

- **Inverted Index:** Maps a word to it's locations so lookups 
  are O(1) instead of O(everything).
- **Positional Indexing:** Records where each word appears within 
  a page, enabling phrase search like `"holy knight"` to find those 
  two words together, not just anywhere on the page.
- **Stop Words:** Common words like "the", "a", "is" that get dropped 
  from the index by default since nobody searches specifically for them, 
  saving space and improving index build  performance.
- **Case Insensitive:** "Holy", "holy", and "HOLY" all match up to the
  same entry.
- **Delta Encoding:** Word positions are stored as compressed 
  differences rather than raw numbers, keeping the index much smaller
  than the original media.

### Why not just Ctrl+F this?

Well, as I said earlier in the motivation, Ctrl+F is completely fine, if you only have a few books or know which book to look in, and Ctrl+F is still useful once this tool has identified the books you query appears in. However, if you have a **large** collection of books, you may not feel like spending you precious time click open and closing each book, jumping from one occurrence to the next. This way, you can spend that time reading about the topic instead.

### Why not a lightweight relational databse like SQLite?

A database could work, but you would quickly run into some of it's limitations for an application like this. To support the **phrase search** you would need extra columns to store positional information for every word in every document - and since the same word appears a thousand times across hundred of pages or even files, that positional data would balloon into massive amounts of duplicate information.

Phrase searches make it even worse. Finding "holy knight" requires a self join on a hypothetical *Positions* table - checking that "holy" and "knight" appear on the same page at consecutive palces. A three word search would require another join. Guess what, four words means another, and so on. So, we start to observe scaling issues.

Finally, the table would be enormously bloated with words nobody would care about - "the", "a", "is", "in" - eating up space and slowing down every query. That happens to be another thing Whoosh handles for us, enter *stop words*.

### Wait! Won't we just have a bloated index with filler words?

**NO!** Whoosh defaults to dropping common words - called **stop words** - from the index entirely. Words like "the", "a", "an", "is", "are", "on" and many more are never stored because they aren't typically searched for. This keeps a slim index and improves build time.

An exmaple would be if I searched for `"the holy knight"`, this would automatically become a search for `"holy knight"` - notice the meaningful words are all that remains - the "the" has been ignored. This means we will recieve results where holy and knight appear in the sentence.

**A heads up for rulebook users:** Some game terms may include stop words, like "to hit" or "at will". Whoosh will drop "to" and "at" by default, and only search for "hit" and "will". In many cases you will probably still find what you are looking for, but be warned that you may get some weird results from time to time on short phrase searches.

However! I plan to include a **Include stop words** option specifically for these edge cases - please refer to the roadmap down below for it's current status.

---

## Project Structure 

```
Rummage/
├── .index/                 # Emphemeral folder for index storage
├── src/
│   ├── indexer.py          # Builds and populates the whoosh index
│   ├── searcher.py         # Queries the index
│   ├── main.py             # CLI entry point
│   └── gui.py              # tkinter GUI (IN PROGRESS)
├── tests/
│   └── Rummage_test.pdf    # Simple PDF file for sanity checks after logic adjustments
├── requirements.txt        # Dependencies to import for build
└── README.md               # The document you are reading, lol
```

---

## Development Roadmap

- [X] PDF Support
- [X] Phrase Search
- [X] CLI interface and argument parser
- [X] Stop words toggle (--stopwords)
- [X] Result limit (--limit)
- [X] Search mode selection: exact, all, any (--searchmode)
- [ ] "Include stop words" toggle in GUI
- [ ] Search mode selector in GUI
- [ ] tkinter GUI
- [ ] Windows executable with PyInstaller
- [ ] DOCX Support
- [ ] TXT Support
- [ ] Incremental indexing (only re-index changed files)
- [ ] Stemming toggle (--stemming) for root word matching e.g. "knights" → "knight"
*...something I should add?*

---

## License

MIT