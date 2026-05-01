# gui.py
# customtkinter GUI entry point for Rummage
# ===========================================================

import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import re
import os
import threading
import webbrowser
import whoosh.index
import pathlib

from indexer import index_documents
from searcher import search_index

# Set the appearance of the application
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Constants
GITHUB_URL  = "https://github.com/rwzimmerman04/Rummage"
BASE_DIR    = pathlib.Path(__file__).parent.parent
INDEX_DIR   = str(BASE_DIR / ".index")
APP_VERSION = "0.1"


class RummageApp:
    def __init__(self, window):
        # Store reference to the main window
        self.window = window
        self.window.title("Rummage")
        self.window.minsize(700, 650)

        # StringVars are tkinter variables that automatically update
        # any widget that is bound to them when their value changes
        self.folder_path = tk.StringVar(value="No folder selected...")
        self.status_text = tk.StringVar(value="Ready.")
        self.needs_reindex = False
        self.last_folder = None

        # Build each section of the UI in order
        self._build_menu()
        self._build_folder_section()
        self._build_search_bar()
        self._build_warning_banner()
        self._build_results_panel()
        self._build_status_bar()


    # ===========================================================
    # Menu Bar
    # ===========================================================

    def _build_menu(self):
        """
        Builds the top menu bar with File and About menus.
        tk.Menu is used here because customtkinter has no menu widget.
        """
        menubar = tk.Menu(self.window, tearoff=0)

        # File menu: folder and app management
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open Folder",      command=self.browse_folder)
        file_menu.add_command(label="Save Results",     command=self.save_results)
        file_menu.add_command(label="Reindex",          command=self.force_reindex)
        file_menu.add_separator()
        file_menu.add_command(label="Exit",             command=self.window.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # About menu: app info and help
        about_menu = tk.Menu(menubar, tearoff=0)
        about_menu.add_command(label="About Rummage",   command=self.show_about)
        about_menu.add_command(label="View on GitHub",  command=lambda:self.open_link(GITHUB_URL))
        about_menu.add_separator()
        about_menu.add_command(label="Help",            command=self.show_help)
        menubar.add_cascade(label="About", menu=about_menu)

        # Attach the menu bar to the window
        self.window.config(menu=menubar)


    # ===========================================================
    # Folder Section
    # ===========================================================

    def _build_folder_section(self):
        """
        Builds the document folder section.
        Contains the folder path display, browse button, and mode selector.
        """
        # Outer container frame
        frame = ctk.CTkFrame(self.window)
        frame.pack(fill="x", padx=12, pady=(12, 4))

        # Section label
        ctk.CTkLabel(frame, text="DOCUMENT FOLDER",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="gray")\
            .pack(anchor="w", padx=10, pady=(8, 2))

        # Row: folder path entry + browse button
        path_frame = ctk.CTkFrame(frame, fg_color="transparent")
        path_frame.pack(fill="x", padx=10, pady=(0, 6))

        # Read-only entry displays the selected folder path
        # textvariable binds it to self.folder_path so it updates automatically
        ctk.CTkEntry(path_frame, textvariable=self.folder_path, state="readonly")\
            .pack(side="left", fill="x", expand=True, padx=(0, 6))

        # Create the browse button
        ctk.CTkButton(path_frame, text="Browse", width=80, command=self.browse_folder)\
            .pack(side="left")

        # All three radio buttons share the same variable this way only one can be selected at a time
        self.mode = tk.StringVar(value="recursive")
        mode_frame = ctk.CTkFrame(frame, fg_color="transparent")
        mode_frame.pack(anchor="w", padx=10, pady=(0, 10))

        ctk.CTkLabel(mode_frame, text="Mode:", text_color="gray")\
            .pack(side="left", padx=(0, 8))

        # tk.Radiobutton used here — customtkinter's radio button
        # lacks good styling options for dark mode
        for text, value in [("Recursive", "recursive"),
                             ("Folder only", "folder"),
                             ("Single file", "file")]:
            tk.Radiobutton(mode_frame, text=text, variable=self.mode, value=value,
                            command=self._on_mode_change,
                            bg="#2b2b2b", fg="white", selectcolor="#2b2b2b",
                            activebackground="#2b2b2b", activeforeground="white")\
                .pack(side="left", padx=(0, 12))


    # ===========================================================
    # Search Bar
    # ===========================================================

    def _build_search_bar(self):
        """
        Builds the search bar with query entry and search button.
        """
        frame = ctk.CTkFrame(self.window, fg_color="transparent")
        frame.pack(fill="x", padx=12, pady=4)

        # Create the query entry box
        self.query_entry = ctk.CTkEntry(
            frame,
            placeholder_text='Search keyword or "phrase"...',
            font=ctk.CTkFont(size=13)
        )
        self.query_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))

        # Create the search button
        self.search_button = ctk.CTkButton(frame, text="Search", width=90, command=self.run_search)
        self.search_button.pack(side="left")

        # Create the hint label below the search bar
        ctk.CTkLabel(self.window,
                     text='Tip: use "quotes" for exact phrases',
                     font=ctk.CTkFont(size=10),
                     text_color="gray")\
            .pack(anchor="w", padx=14)


    # ===========================================================
    # Warning Banner
    # ===========================================================

    def _build_warning_banner(self):
        """
        Builds the warning banner that appears when reindexing is needed.
        Hidden by default -> shown and hidden dynamically with show_warning/hide_warning.
        """
        # Dark yellow background frame
        self.warning_frame = ctk.CTkFrame(self.window, fg_color="#3d3000")

        # Warning message label
        self.warning_label = ctk.CTkLabel(
            self.warning_frame,
            text="",
            text_color="#ffc107",
            wraplength=640,
            justify="left"
        )
        self.warning_label.pack(padx=12, pady=6)

    
    def show_warning(self, warning):
        """
        Show the warning label and display a warning message
        """
        self.warning_label.configure(text=warning)
        self.warning_frame.pack(fill="x", padx=12, pady=(2, 0))


    def hide_warning(self):
        """
        Hide the warning label
        """
        self.warning_frame.pack_forget()

    # ===========================================================
    # Results Panel
    # ===========================================================

    def _build_results_panel(self):
        """
        Builds the results panel with two sections.
        - SUMMARY: Scrollabel list of buttons, one per book, showing matched page numbers
        - CONTEXT: Scrollable text area showing snippets grouped by book then page
        """
        
        # SUMMARY SECTION

        ctk.CTkLabel(self.window, text="SUMMARY",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="gray")\
            .pack(anchor="w", padx=14, pady=(8, 2))

        self.summary_frame = ctk.CTkScrollableFrame(self.window, height=120)
        self.summary_frame.pack(fill="x", padx=12, pady=(0, 4))

        # CONTEXT SECTION

        ctk.CTkLabel(self.window, text="CONTEXT",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="gray")\
            .pack(anchor="w", padx=14, pady=(4, 2))

        # Container frame for text widget and scrollbar
        frame = ctk.CTkFrame(self.window)
        frame.pack(fill="both", expand=True, padx=12, pady=(0, 4))

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        # Build the results area
        self.results_text = tk.Text(
            frame,
            state="disabled",
            yscrollcommand=scrollbar.set,
            wrap="word",
            font=("Helvetica", 10),
            bg="#2b2b2b",
            fg="#ffffff",
            padx=10,
            pady=8,
            cursor="arrow",
            relief="flat",
            insertbackground="white"
        )
        self.results_text.pack(fill="both", expand=True)
        scrollbar.config(command=self.results_text.yview)

        # Define tags for stlying the results area
        self.results_text.tag_config("book",     font=("Helvetica", 11, "bold"), foreground="#4fc3f7")
        self.results_text.tag_config("page",     font=("Helvetica", 10, "bold"), foreground="#888888")
        self.results_text.tag_config("snippet",  font=("Helvetica", 10),         foreground="#dddddd")
        self.results_text.tag_config("match",    font=("Helvetica", 10, "bold"), foreground="#ffc107")
        self.results_text.tag_config("divider",  foreground="#444444")


    def display_results(self, matches):
        """
        Renders match list into the results text widget. 
        Parses <b> tags from Whoosh snippets to bolden matched words.
        """
        
        # # Enableediting temoprarily for result updating
        # self.results_text.config(state="normal")
        # self.results_text.delete("1.0", "end")

        # if not matches:
        #     self.results_text.insert("end", "No matches found.")
        #     self.results_text.config(state="disabled")
        #     return

        # for m in matches:
        #     # Filename and page number on one line
        #     self.results_text.insert("end", m["filename"], "filename")
        #     self.results_text.insert("end", f" - page {m['page']}\n", "page")

        #     # Empty line after the header - makes it less corwded :)
        #     self.results_text.insert("end", "\n")

        #     # Split fragments with "..." as Whoosh seperator
        #     # Each fragment is one matching sentence
        #     snippet = m["snippet"].strip()
        #     if not snippet:
        #         self.results_text.insert("end", "... (match found - open file to view context)\n", "page")
        #     else:
        #         fragments = m["snippet"].split("...")
        #     for fragment in fragments:
        #         fragment = fragment.strip()     # Clean the fragment
        #         if not fragment:
        #             continue
            
        #         # leading ellipses to show this is a snippet, not the full page
        #         self.results_text.insert("end", "... ", "page")

        #         # Remove nextline chars
        #         fragment = fragment.replace("\n", " ").replace("  ", " ").strip()

        #         # Parse <b> tags - bold yellow for matched words, normal for all other words
        #         while "<b" in fragment:
        #             pre, remaining = fragment.split("<b", 1)
        #             _, remaining = remaining.split(">", 1)
        #             word, remaining = remaining.split("</b>", 1)
        #             self.results_text.insert("end", pre, "snippet")
        #             self.results_text.insert("end", word, "match")
        #             fragment = remaining
    
        #         # Insert remaing text after the last found match
        #         self.results_text.insert("end", fragment + "\n", "snippet")

        #     # Empty line then divider then empty line between results
        #     self.results_text.insert("end", "\n")
        #     self.results_text.insert("end", "-" * 60 + "\n", "divider")
        #     self.results_text.insert("end", "\n")

        # # Lock the text window for the results after making changes
        # self.results_text.config(state="disabled")


    # ===========================================================
    # Status Bar
    # ===========================================================

    def _build_status_bar(self):
        """
        Builds the status bar at the bottom of the window.
        """
        frame = ctk.CTkFrame(self.window, height=28, corner_radius=0)
        frame.pack(fill="x", side="bottom")

        ctk.CTkLabel(frame,
                     textvariable=self.status_text,
                     font=ctk.CTkFont(size=10),
                     text_color="gray")\
            .pack(side="left", padx=8)

    # ===========================================================
    # Helper functions
    # ===========================================================

    def browse_folder(self):
        """
        Open folder picker and detect if reindex is needed.
        """
        if self.mode.get() == "file":
            path = filedialog.askopenfilename(
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
            )
        else:
            path = filedialog.askdirectory()

        if path:
            self.folder_path.set(path)
            # Flag reindex if folder changed
            if path != self.last_folder:
                self.needs_reindex = True
                if whoosh.index.exists_in(INDEX_DIR):
                    self.show_warning("Folder changed: Index will be rebuilt on next search.")
                else:
                    self.show_warning("No index found: Index will be built on first search.")
            self.status_text.set(f"Folder: {path}")


    def run_search(self):
        """
        Reindex if neededon a background thread, then run the search.
        """
        query = self.query_entry.get().strip()
        folder = self.folder_path.get()

        if folder == "No folder selected...":
            messagebox.showwarning("No folder", "Please select a folder first.")
            return
        if not query:
            messagebox.showwarning("No query", "Please enter a search term.")
            return

        if self.needs_reindex:
            # Disable the search button while indexing
            self._set_ui_enabled(False)
            self.status_text.set("Indexing... please wait.")
            # Spawn a thread for the indexing process
            thread = threading.Thread(
                target=self._run_index,
                args=(folder, query),
                daemon=True
            )
            thread.start()  # Start the indexing thread
        else:
            self._do_search(query)


    def force_reindex(self):
        """Force a full reindex from the menu on a background thread."""
        folder = self.folder_path.get()

        # Validation
        if folder == "No folder selected...":
            messagebox.showwarning("No folder", "Please select a folder first.")
            return

        self._set_ui_enabled(False)
        self.status_text.set("Reindexing... please wait.")
        # Spawn a thread for the indexing process
        thread = threading.Thread(
            target=self._run_index,
            args=(folder,),
            daemon=True
        )
        thread.start()      # Start the indexing thread


    def _run_index(self, folder, query=None):
        """
        Background thread worker: Indexes then optionally searches.
        query=None means just reindex, no search after.
        """
        index_documents(folder, INDEX_DIR, self.mode.get(), 
                        progress_callback=self._on_progress)
        self.last_folder = folder
        self.needs_reindex = False
        self.window.after(0, self.hide_warning)
        self.window.after(0, lambda: self._set_ui_enabled(True))

        if query:
            self.window.after(0, lambda: self._do_search(query))
        else:
            self.window.after(0, lambda: self.status_text.set("Reindex complete!"))


    def _on_progress(self, current, total, writing=False):
        """
        Called by indexer after each file: Updates the status bar safely.
        writing=True means extract is done and we are writing to disk/index.
        """
        if writing:
            self.window.after(0, lambda: self.status_text.set(
                "Writing index to disk..."
            ))
        else:
            self.window.after(0, lambda: self.status_text.set(
                f"Indexing... ({current} of {total} files.)"
            ))
        

    def _do_search(self, query):
        """
        Runs the search and displays results: always on the main thread.
        """
        matches = search_index(query, INDEX_DIR)
        self.display_results(matches)
        self.status_text.set(f"Found {len(matches)} results for: {query}")


    def _set_ui_enabled(self, enabled):
        """
        Enables or disables interactive widgets during the indexing.
        """
        state = "normal" if enabled else "disabled"
        self.query_entry.configure(state=state)


    def open_link(self, url_in):
        """
        Open the github page for Rummage, direct the user to the page
        """
        webbrowser.open(url_in)


    def show_about(self):
        """
        Defines a message box to display info about the Rummage app to the user
        """
        messagebox.showinfo("About Rummage", 
            f"Rummage v{APP_VERSION}\n\nFast keyword and phrase search across large document collections.\n\nBuilt by Robert Zimmerman")


    def show_help(self):
        """
        Defines a message box for tips and helpful info for the user.
        """
        messagebox.showinfo("Help",
            "Search syntax:\n\n"
            "  holy knight     — pages containing both words\n"
            '  "holy knight"   — exact phrase only\n\n'
            "Indexing:\n\n"
            "  Select a folder and click Search.\n"
            "  The index is built automatically on first search.\n"
            "  Use File > Reindex to force a rebuild.")

    
    def _on_mode_change(self):
        """
        Called when the user switches mode.
        Resets the folder path only when switching between file and folder modes
        since they require different path types.
        """
        current_mode = self.mode.get()
        current_path = self.folder_path.get()

        # Only reset if switching between incompatible path types
        if current_mode == "file" and pathlib.Path(current_path).is_dir():
            self._reset_path()
        elif current_mode in ("recursive", "folder") and pathlib.Path(current_path).is_file():
            self._reset_path()


    def _reset_path(self):
        """
        Clears the selected path and resets related state.
        """
        self.folder_path.set("No folder selected...")
        self.last_folder   = None
        self.needs_reindex = False
        self.hide_warning()
        self.status_text.set("Ready.")


    def save_results(self):
        pass    # TO-DO: Save results to file




# ===========================================================
# Entry Point
# ===========================================================

def main():
    # Create the main window and pass it to RummageApp
    window = ctk.CTk()
    app = RummageApp(window)

    # Start the event loop
    window.mainloop()


if __name__ == "__main__":
    main()