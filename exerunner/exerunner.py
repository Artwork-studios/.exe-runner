import os
import tkinter as tk
from tkinter import messagebox

# ANSI escape codes for text colors
GREEN = "\033[32m"
ORANGE = "\033[33m"
RESET = "\033[0m"

class ExeRunnerApp:
    def __init__(self, master):
        self.master = master
        master.title("EXE RUNNER")
        master.geometry("800x600")  # Set initial window size

        # Color scheme
        self.bg_color = "#2E3B4E"
        self.button_color = "#5C7D99"
        self.text_color = "#FFFFFF"

        # Add a label at the top-middle
        self.middle_label = tk.Label(master, text=".EXE RUNNER", font=('Helvetica', 36),
                                     bg=self.bg_color, fg=self.text_color)
        self.middle_label.pack(side=tk.TOP, pady=20)  # Adjusted packing options

        # Main page buttons
        self.btn_downloads = tk.Button(master, text="Downloads", command=self.show_downloads,
                                       font=('Helvetica', 18), bg=self.button_color, fg=self.text_color)
        self.btn_downloads.pack(pady=20, expand=True, fill=tk.BOTH)
        self.btn_music = tk.Button(master, text="Music", command=self.show_music,
                                   font=('Helvetica', 18), bg=self.button_color, fg=self.text_color)
        self.btn_music.pack(pady=20, expand=True, fill=tk.BOTH)

        # Downloads page
        self.downloads_frame = tk.Frame(master, bg=self.bg_color)
        self.downloads_label = tk.Label(self.downloads_frame, text="Downloads Page", font=('Helvetica', 24),
                                        bg=self.bg_color, fg=self.text_color)
        self.downloads_label.pack(pady=10)

        # Listbox to display exe files
        self.listbox = tk.Listbox(self.downloads_frame, selectmode=tk.SINGLE, font=('Helvetica', 16),
                                  bg=self.bg_color, fg=self.text_color)
        self.listbox.pack(expand=True, fill=tk.BOTH)

        # Back button to return to the main page
        self.btn_back = tk.Button(self.downloads_frame, text="Back", command=self.show_main,
                                  font=('Helvetica', 18), bg=self.button_color, fg=self.text_color)
        self.btn_back.pack(pady=10, expand=True, fill=tk.BOTH)

        # Populate Downloads Listbox
        self.populate_listbox(os.path.join(os.path.dirname(__file__), "Downloads"))

    def show_main(self):
        self.downloads_frame.pack_forget()

    def show_downloads(self):
        self.downloads_frame.pack(fill=tk.BOTH, expand=True)
        self.show_exe_files(os.path.join(os.path.dirname(__file__), "Downloads"))

    def show_music(self):
        messagebox.showinfo("Music", "Music page coming soon!")

    def populate_listbox(self, folder):
        # Clear existing items
        self.listbox.delete(0, tk.END)

        # List all files in the folder
        files = os.listdir(folder)

        # Filter for .exe files
        exe_files = [file for file in files if file.endswith(".exe")]

        if not exe_files:
            self.listbox.insert(tk.END, "No .exe files here T-T")
        else:
            for exe_file in exe_files:
                self.listbox.insert(tk.END, exe_file)

    def show_exe_files(self, folder):
        # Clear the Listbox
        self.listbox.delete(0, tk.END)

        # Populate the Listbox with .exe files in the folder
        self.populate_listbox(folder)

        # Bind double-click event to run the selected .exe file
        self.listbox.bind("<Double-1>", self.run_selected_exe)

    def run_selected_exe(self, event):
        # Get the selected item in the Listbox
        selected_item_index = self.listbox.curselection()
        if selected_item_index:
            selected_item = self.listbox.get(selected_item_index)
            folder = os.path.join(os.path.dirname(__file__), "Downloads")
            exe_path = os.path.join(folder, selected_item)

            # Open the selected file with its associated program
            try:
                os.startfile(exe_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open {exe_path}: {e}")

def main():
    root = tk.Tk()
    app = ExeRunnerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
