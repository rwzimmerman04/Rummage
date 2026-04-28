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
        file_menu.add_command(label="Open Folder")
        file_menu.add_command(label="Save Results")
        file_menu.add_command(label="Reindex")
        file_menu.add_separator()
        file_menu.add_command(label="Exit")
        menubar.add_cascade(label="File", menu=file_menu)

        # About menu: app info and help
        about_menu = tk.Menu(menubar, tearoff=0)
        about_menu.add_command(label="About Rummage", command=self.show_about)
        about_menu.add_command(label="View on GitHub", command=lambda:self.open_link(GITHUB_URL))
        about_menu.add_separator()
        about_menu.add_command(label="Help", command=self.show_help)
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
        self.search_button = ctk.CTkButton(frame, text="Search", width=90)
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
        self.warning_label.pack_forget()

    # ===========================================================
    # Results Panel
    # ===========================================================

    def _build_results_panel(self):
        """
        Builds the results panel.
        """
        # Create results section label
        ctk.CTkLabel(self.window, text="RESULTS",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="gray")\
            .pack(anchor="w", padx=14, pady=(8, 2))

        # Container frame for text widget and scrollbar
        frame = ctk.CTkFrame(self.window)
        frame.pack(fill="both", expand=True, padx=12, pady=(0, 4))

        # Build the results area
        self.results_text = tk.Text(
            frame,
            state="disabled",
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

        # Define tags for stlying the results area
        self.results_text.tag_config("filename",    font=("Helvetica", 10, "bold"), foreground="#4fc3f7")
        self.results_text.tag_config("page",        foreground="#888888")
        self.results_text.tag_config("snippet",     font=("Helvetica", 10), foreground="#dddddd")
        self.results_text.tag_config("match",       font=("Helvetica", 10, "bold"), foreground="#ffc107")
        self.results_text.tag_config("divider",     foreground="#444444")


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