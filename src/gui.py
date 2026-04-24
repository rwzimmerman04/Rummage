# gui.py
# tkinter GUI entry point for Rummage
# ===========================================================

import tkinter as tk
from tkinter import filedialog, messagebox
import whoosh.index

from indexer import index_documents
from searcher import search_index

# Constants
GITHUB_URL  = "https://github.com/rwzimmerman04/Rummage"
INDEX_DIR   = "../.index"
APP_VERSION = "0.1"


class RummageApp:
    def __init__(self, window):
        # Create the window
        self.window         = window
        self.folder_path    = tk.StringVar(value="No folder selected...")
        self.status_text    = tk.StringVar(value="No folder selected.")
        self.needs_reindex  = False
        self.last_folder    = None

        # Set name and min size
        self.window.title("Rummage")
        self.window.minsize(700, 600)

        # Add the applications components to the window
        self._build_menu()
        self._build_folder_section()
        self._build_search_bar()
        self._build_results_panel()


    # ===========================================================
    # Menu Bar
    # ===========================================================

    def _build_menu(self):
        menubar = tk.Menu(self.window, tearoff=0)

        # Create the 'File' menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)

        # Create the 'About' menu
        about_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="About", menu=about_menu)

        self.window.config(menu=menubar)


    # ===========================================================
    # Folder Section
    # ===========================================================

    def _build_folder_section(self):
        # Add a label
        frame = tk.LabelFrame(self.window, text="Document Folder", padx=8, pady=8)
        frame.pack(fill="x", padx=12, pady=(12, 4))

        # Folder path display and browse button
        path_frame = tk.Frame(frame)
        path_frame.pack(fill="x")

        tk.Entry(path_frame, textvariable=self.folder_path, state="readonly")\
            .pack(side="left", fill="x", expand=True, padx=(0, 6))
        tk.Button(path_frame, text="Browse")\
            .pack(side="left")

        # Add a Mode to the radio buttons (acts as a group where only one can be selected)
        self.mode = tk.StringVar(value="recursive")
        mode_frame = tk.Frame(frame)
        mode_frame.pack(anchor="w", pady=(6, 0))

        # Add the buttons, the default mode has been set to recursive already in the mode
        tk.Radiobutton(mode_frame, text="Recursive",    variable=self.mode, value="recursive").pack(side="left", padx=(0, 12))
        tk.Radiobutton(mode_frame, text="Folder only",  variable=self.mode, value="folder").pack(side="left", padx=(0, 12))
        tk.Radiobutton(mode_frame, text="Single file",  variable=self.mode, value="file").pack(side="left")

        # Create the Limit option
        limit_frame = tk.Frame(frame)
        limit_frame.pack(anchor="w", pady=(6, 0))


    # ===========================================================
    # Search Bar
    # ===========================================================

    def _build_search_bar(self):
        frame = tk.Frame(self.window)
        frame.pack(fill="x", padx=12, pady=4)

        # Create the entry box for searching
        self.query_entry = tk.Entry(frame, font=("Helvetica", 12))
        self.query_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))

        # SSearch button
        tk.Button(frame, text="Search")\
            .pack(side="left")

        # Search syntax helpful tip
        tk.Label(self.window, text='Tip: use "quotes" for exact phrases', 
                 font=("Helvetica", 9), fg="gray")\
            .pack(anchor="w", padx=14)



    # ===========================================================
    # Results Panel
    # ===========================================================

    def _build_results_panel(self):
        frame = tk.LabelFrame(self.window, text="Results", padx=6, pady=6)
        frame.pack(fill="both", expand=True, padx=12, pady=(4, 4))

        # Scrollable text widget for results
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        self.results_text = tk.Text(
            frame,
            state="disabled",
            yscrollcommand=scrollbar.set,
            wrap="word",
            font=("Helvetica", 10),
            padx=6,
            pady=6,
            cursor="arrow"
        )
        self.results_text.pack(fill="both", expand=True)
        scrollbar.config(command=self.results_text.yview)

        # Text tags for styling
        self.results_text.tag_config("filename",    font=("Helvetica", 10, "bold"))
        self.results_text.tag_config("page",        foreground="gray")
        self.results_text.tag_config("snippet",     font=("Helvetica", 10))
        self.results_text.tag_config("match",       font=("Helvetica", 10, "bold"))
        self.results_text.tag_config("divider",     foreground="#cccccc")



    # ===========================================================
    # Actions
    # ===========================================================

    # ...TO-DO...


# ===========================================================
# Entry Point
# ===========================================================

def main():
    window = tk.Tk()
    app = RummageApp(window)
    window.mainloop()

if __name__ == "__main__":
    main()