import os
import tkinter as tk
from tkinter import simpledialog, messagebox
import subprocess
import pefile
import hashlib
import logging

# ANSI escape codes for text colors
GREEN = "\033[32m"
ORANGE = "\033[33m"
RESET = "\033[0m"

class ExeRunnerApp:
    def __init__(self, master):
        self.master = master
        master.title("EXE RUNNER")
        master.geometry("800x600")  # Set initial window size

        # Set the icon for the app
        icon_path = os.path.join(os.path.dirname(__file__), "exe.ico")
        master.iconbitmap(icon_path)

        # Color scheme
        self.bg_color = "#2E3B4E"
        self.button_color = "#5C7D99"
        self.text_color = "#FFFFFF"

        # Configure logging
        self.configure_logging()

        # Add a label at the top-middle
        self.middle_label = tk.Label(master, text=".EXE RUNNER", font=('Helvetica', 36),
                                     bg=self.bg_color, fg=self.text_color)
        self.middle_label.pack(side=tk.TOP, pady=20)  # Adjusted packing options

        # Main page buttons with added padding
        self.btn_downloads = tk.Button(master, text="Downloads", command=self.show_downloads,
                                       font=('Helvetica', 18), bg=self.button_color, fg=self.text_color)
        self.btn_downloads.pack(pady=20, padx=10, expand=True, fill=tk.BOTH)
        self.btn_music = tk.Button(master, text="Music", command=self.show_music,
                                   font=('Helvetica', 18), bg=self.button_color, fg=self.text_color)
        self.btn_music.pack(pady=20, padx=10, expand=True, fill=tk.BOTH)

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
        self.btn_back.pack(pady=10, padx=10, expand=True, fill=tk.BOTH)

        # Password setup
        self.setup_password()

        # Populate Downloads Listbox
        self.populate_listbox(os.path.join(os.path.dirname(__file__), "Downloads"))

    def configure_logging(self):
        logging.basicConfig(filename='app_log.txt', level=logging.ERROR,
                            format='%(asctime)s [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    def log_error(self, error_message):
        # Log errors to a file
        logging.error(error_message)

    def setup_password(self):
        password_file_path = os.path.join(os.path.dirname(__file__), "password.txt")

        if not os.path.exists(password_file_path):
            # Set up a 4-digit password if it doesn't exist
            password = self.get_valid_password()
            with open(password_file_path, "w") as password_file:
                password_file.write(password)
            messagebox.showinfo("Password Set", "Password has been set successfully!")

        # Get the password from the file
        with open(password_file_path, "r") as password_file:
            self.password = password_file.read().strip()

    def get_valid_password(self):
        while True:
            password = simpledialog.askstring("Set Password", "Set a 4-digit password:")
            if password.isdigit() and len(password) == 4:
                return password
            messagebox.showerror("Invalid Password", "Invalid password. Please enter a 4-digit numeric password.")

    def authenticate_user(self):
        # Prompt user to log in using the stored password
        authenticated = False
        attempts = 3

        while not authenticated and attempts > 0:
            entered_password = simpledialog.askstring("Password", "Enter your 4-digit password:")

            if entered_password == self.password:
                authenticated = True
            else:
                attempts -= 1
                messagebox.showerror("Authentication Failed", f"Incorrect password. {attempts} attempts remaining.")

        if not authenticated:
            self.master.destroy()  # Close the application if authentication fails

    def show_main(self):
        self.downloads_frame.pack_forget()

    def show_downloads(self):
        # Authenticate the user before showing the Downloads page
        self.authenticate_user()
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
            self.listbox.insert(tk.END, "Nothing here T-T")
        else:
            for exe_file in exe_files:
                self.listbox.insert(tk.END, exe_file)

    def show_exe_files(self, folder):
        # Clear the Listbox
        self.listbox.delete(0, tk.END)

        # Populate the Listbox with .exe files in the folder and subfolders
        exe_files = self.populate_listbox_recursive(folder)

        if not exe_files:
            self.listbox.insert(tk.END, "Nothing here T-T")

        # Bind double-click event to run the selected .exe file
        self.listbox.bind("<Double-1>", self.run_selected_exe)

    def populate_listbox_recursive(self, folder):
        # Clear existing items
        self.listbox.delete(0, tk.END)

        exe_files = []

        for root, dirs, files in os.walk(folder):
            for exe_file in [file for file in files if file.endswith(".exe")]:
                full_path = os.path.join(root, exe_file)
                self.listbox.insert(tk.END, full_path)
                exe_files.append(full_path)

        return exe_files

    def run_selected_exe(self, event):
        # Get the selected item in the Listbox
        selected_item_index = self.listbox.curselection()
        if selected_item_index:
            selected_item = self.listbox.get(selected_item_index)

            # Check if the file is potentially malicious using pefile
            if self.is_malicious(selected_item):
                # If potentially malicious, show a warning popup
                warning_msg = (
                    f"The file may be malicious!\n\n"
                    f"Do you still want to run it?"
                )
                response = messagebox.askyesno("Potential Threat", warning_msg)
                if not response:
                    return  # User chose not to run the file

            # Open the selected file with its associated program using subprocess
            try:
                subprocess.Popen(selected_item, shell=True)
            except Exception as e:
                self.log_error(f"Failed to open {selected_item}: {e}")
                messagebox.showerror("Error", f"Failed to open {selected_item}: {e}")

    def is_malicious(self, file_path):
        try:
            pe = pefile.PE(file_path)
            # Add your custom logic for detecting potential threats here
            # Example: Check if the executable is flagged by antivirus
            if pe.FILE_HEADER.Characteristics & 0x0020:
                return True
            return False
        except Exception as e:
            self.log_error(f"Error checking for malicious app: {e}")
            return False


def main():
    root = tk.Tk()
    app = ExeRunnerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
