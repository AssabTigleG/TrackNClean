import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime


class FolderMonitor:
    def __init__(self):
        self.snapshot_file = "folder_snapshot.json"
        self.root = tk.Tk()
        self.root.title("Multi-Directory Monitor")
        self.root.geometry("1500x720")  # Made window bigger for better visibility
        # self.root.attributes('-fullscreen', True)
        self.root.state('zoomed')
        self.directories = []
        self.setup_gui()
        self.load_existing_snapshots()
        self.exclusions_file = "exclusions.json"
        self.exclusions = self.load_exclusions()

    def setup_gui(self):
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Top frame for directory list
        top_frame = tk.Frame(main_frame)
        top_frame.pack(fill=tk.BOTH, expand=True)

        # Left side - Directory list
        left_frame = tk.Frame(top_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(left_frame, text="Monitored Directories:").pack(anchor='w')

        self.tree = ttk.Treeview(left_frame, columns=('Path', 'Last Snapshot'), show='headings')
        self.tree.heading('Path', text='Directory Path')
        self.tree.heading('Last Snapshot', text='Last Snapshot')
        self.tree.column('Path', width=400)
        self.tree.column('Last Snapshot', width=200)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=(5, 10))

        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Right side - Changes list
        right_frame = tk.Frame(top_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(20, 0))

        tk.Label(right_frame, text="Detected Changes:").pack(anchor='w')

        self.changes_tree = ttk.Treeview(right_frame, columns=('Path', 'Type'), show='headings')
        self.changes_tree.heading('Path', text='Path')
        self.changes_tree.heading('Type', text='Type')
        self.changes_tree.column('Path', width=300)
        self.changes_tree.column('Type', width=100)
        self.changes_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=(5, 10))

        changes_scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.changes_tree.yview)
        changes_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.changes_tree.configure(yscrollcommand=changes_scrollbar.set)

        # Buttons frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        tk.Button(button_frame, text="Add Directory", command=self.add_directory).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Remove Selected", command=self.remove_directory).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Take Snapshots", command=self.take_snapshots).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Check Changes", command=self.check_changes).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Clean All Changes", command=self.check_and_clean_all).pack(side=tk.LEFT, padx=5)

        excl_buttons = tk.Frame(button_frame)
        excl_buttons.pack(side=tk.LEFT, padx=20)
        tk.Button(excl_buttons, text="Add to Exclusions", command=self.add_to_exclusions).pack(side=tk.LEFT, padx=5)
        tk.Button(excl_buttons, text="Remove from Exclusions", command=self.remove_from_exclusions).pack(side=tk.LEFT,
                                                                                                         padx=5)

        # Status area
        tk.Label(main_frame, text="Status:").pack(anchor='w', pady=(20, 5))
        self.status_text = tk.Text(main_frame, height=8, width=70)
        self.status_text.pack(fill=tk.BOTH, expand=True)

        # Right side - Exclusions list
        right_frame = tk.Frame(top_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(20, 0))

        tk.Label(right_frame, text="Exclusions:").pack(anchor='w')

        self.exclusions_tree = ttk.Treeview(right_frame, columns=('Path', 'Type'), show='headings')
        self.exclusions_tree.heading('Path', text='Path')
        self.exclusions_tree.heading('Type', text='Type')
        self.exclusions_tree.column('Path', width=250)
        self.exclusions_tree.column('Type', width=80)
        self.exclusions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=(5, 10))

        exclusions_scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.exclusions_tree.yview)
        exclusions_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.exclusions_tree.configure(yscrollcommand=exclusions_scrollbar.set)

    def check_changes(self):
        """Check for changes without deleting anything."""
        if not self.directories:
            messagebox.showwarning("Warning", "No directories are being monitored!")
            return

        # Clear previous changes
        for item in self.changes_tree.get_children():
            self.changes_tree.delete(item)

        total_changes = 0
        for dir_info in self.directories:
            if not dir_info.get('contents'):
                self.update_status(f"No snapshot taken for {dir_info['directory']}. Skipping...")
                continue

            directory = dir_info['directory']
            if not os.path.exists(directory):
                self.update_status(f"Directory no longer exists: {directory}")
                continue

            original_contents = set(dir_info['contents'])
            current_contents = set(self.get_directory_contents(directory))

            # Check for new items
            new_items = current_contents - original_contents
            # Check for deleted items
            deleted_items = original_contents - current_contents

            # Add new items to changes tree
            for item in new_items:
                full_path = os.path.join(directory, item)
                if not self.is_excluded(full_path):  # Only show if not excluded
                    item_type = "Folder" if os.path.isdir(full_path) else "File"
                    self.changes_tree.insert('', tk.END, values=(full_path, f"New {item_type}"))
                    total_changes += 1

            # Add deleted items to changes tree
            for item in deleted_items:
                full_path = os.path.join(directory, item)
                self.changes_tree.insert('', tk.END, values=(full_path, "Deleted"))
                total_changes += 1

        if total_changes == 0:
            self.update_status("No changes detected in any monitored directories.")
        else:
            self.update_status(f"Detected {total_changes} changes across all monitored directories.")

    def get_directory_contents(self, directory):
        """Get all files and folders in a directory."""
        contents = []
        try:
            for item in os.listdir(directory):
                contents.append(item)
        except Exception as e:
            self.update_status(f"Error reading directory {directory}: {str(e)}")
        return contents

    def add_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            existing_dirs = [d['directory'] for d in self.directories]
            if directory not in existing_dirs:
                dir_info = {
                    'directory': directory,
                    'contents': [],
                    'timestamp': 'No snapshot taken'
                }
                self.directories.append(dir_info)
                self.tree.insert('', tk.END, values=(directory, 'No snapshot taken'))
                self.save_snapshots()
                self.update_status(f"Added directory: {directory}")
            else:
                messagebox.showwarning("Warning", "This directory is already being monitored!")

    def remove_directory(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a directory to remove!")
            return

        directory = self.tree.item(selected_item[0])['values'][0]
        self.directories = [d for d in self.directories if d['directory'] != directory]
        self.tree.delete(selected_item)
        self.save_snapshots()
        self.update_status(f"Removed directory: {directory}")

    def take_snapshots(self):
        updated_count = 0
        # Clear changes tree when taking new snapshots
        for item in self.changes_tree.get_children():
            self.changes_tree.delete(item)

        for dir_info in self.directories:
            directory = dir_info['directory']
            if not os.path.exists(directory):
                self.update_status(f"Error: Directory no longer exists: {directory}")
                continue

            contents = self.get_directory_contents(directory)
            dir_info['contents'] = contents
            dir_info['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for item in self.tree.get_children():
                if self.tree.item(item)['values'][0] == directory:
                    self.tree.item(item, values=(directory, dir_info['timestamp']))

            updated_count += 1

        self.save_snapshots()
        self.update_status(f"Snapshots taken for {updated_count} directories")

    def load_existing_snapshots(self):
        try:
            if os.path.exists(self.snapshot_file):
                with open(self.snapshot_file, 'r') as f:
                    self.directories = json.load(f)
                    for dir_info in self.directories:
                        self.tree.insert('', tk.END, values=(
                            dir_info['directory'],
                            dir_info.get('timestamp', 'No snapshot taken')
                        ))
                self.update_status("Loaded existing snapshots successfully")
        except Exception as e:
            self.update_status(f"Error loading existing snapshots: {str(e)}")
            self.directories = []

    def save_snapshots(self):
        try:
            with open(self.snapshot_file, 'w') as f:
                json.dump(self.directories, f, indent=4)
            self.update_status("Snapshots saved successfully")
        except Exception as e:
            self.update_status(f"Error saving snapshots: {str(e)}")

    def check_and_clean_all(self):
        if not self.directories:
            messagebox.showwarning("Warning", "No directories are being monitored!")
            return

        # First check for changes
        self.check_changes()

        # If there are changes in the tree, proceed with cleaning
        if not self.changes_tree.get_children():
            return

        # Build confirmation message from changes tree
        confirm_msg = "The following items will be deleted:\n\n"
        for item in self.changes_tree.get_children():
            values = self.changes_tree.item(item)['values']
            if values[1].startswith("New"):  # Only delete new items
                confirm_msg += f"{values[0]} ({values[1]})\n"

        if messagebox.askyesno("Confirm Deletion", confirm_msg):
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            auto_excluded = []

            for item in self.changes_tree.get_children():
                values = self.changes_tree.item(item)['values']
                if values[1].startswith("New"):  # Only delete new items
                    path = values[0]
                    if not self.is_excluded(path):  # Skip excluded items
                        try:
                            if os.path.isdir(path):
                                self._remove_directory(path)
                            else:
                                os.remove(path)
                            self.update_status(f"Deleted: {path}")
                        except PermissionError as e:
                            # Add to exclusions if it's a permission error
                            item_type = "Folder" if os.path.isdir(path) else "File"
                            self.exclusions.append({
                                'path': path,
                                'type': item_type,
                                'timestamp': current_time,
                                'auto_excluded': True  # Mark as automatically excluded
                            })
                            auto_excluded.append(path)
                            self.update_status(f"Auto-excluded system file: {path}")
                        except Exception as e:
                            self.update_status(f"Error deleting {path}: {str(e)}")

            # If any files were auto-excluded, save and refresh
            if auto_excluded:
                self.save_exclusions()
                self.refresh_exclusions_tree()
                messagebox.showinfo("Auto-Exclusions Added",
                                    f"Some system files could not be deleted and were automatically added to exclusions:\n\n" +
                                    "\n".join(auto_excluded))

            # Refresh changes view
            self.check_changes()

    def _remove_directory(self, directory):
        """Recursively remove a directory and its contents."""
        for root, dirs, files in os.walk(directory, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(directory)

    def update_status(self, message):
        """Update the status text area with a new message."""
        self.status_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')}: {message}\n")
        self.status_text.see(tk.END)

    def run(self):
        self.root.mainloop()

    # EXCLUSION LIST
    def load_exclusions(self):
        """Load saved exclusions from file."""
        try:
            if os.path.exists(self.exclusions_file):
                with open(self.exclusions_file, 'r') as f:
                    exclusions = json.load(f)
                    # Initialize the exclusions tree with saved data
                    self.refresh_exclusions_tree(exclusions)
                    return exclusions
        except Exception as e:
            self.update_status(f"Error loading exclusions: {str(e)}")
        return []

    def save_exclusions(self):
        """Save current exclusions to file."""
        try:
            with open(self.exclusions_file, 'w') as f:
                json.dump(self.exclusions, f, indent=4)
            self.update_status("Exclusions saved successfully")
        except Exception as e:
            self.update_status(f"Error saving exclusions: {str(e)}")

    def refresh_exclusions_tree(self, exclusions=None):
        """Refresh the exclusions treeview."""
        # Clear existing items
        for item in self.exclusions_tree.get_children():
            self.exclusions_tree.delete(item)

        # Use provided exclusions or instance exclusions
        exclusions_to_show = exclusions if exclusions is not None else self.exclusions

        # Update the tree view columns if not already set up
        if len(self.exclusions_tree['columns']) == 2:  # If old column setup
            self.exclusions_tree['columns'] = ('Path', 'Type', 'Added', 'Source')
            self.exclusions_tree.heading('Added', text='Added')
            self.exclusions_tree.heading('Source', text='Source')
            self.exclusions_tree.column('Added', width=150)
            self.exclusions_tree.column('Source', width=80)

        for excl in exclusions_to_show:
            # Format the timestamp if it exists, otherwise use "Prior to tracking"
            timestamp = excl.get('timestamp', 'Prior to tracking')
            # Add source information (Auto/Manual)
            source = "Auto" if excl.get('auto_excluded', False) else "Manual"
            self.exclusions_tree.insert('', tk.END, values=(excl['path'], excl['type'], timestamp, source))

    def add_to_exclusions(self):
        """Add selected changes to exclusions list."""
        selected_items = self.changes_tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select items from the changes list to exclude!")
            return

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for item in selected_items:
            values = self.changes_tree.item(item)['values']
            path = values[0]
            item_type = values[1].split()[-1]  # Extract "File" or "Folder" from "New File"/"New Folder"

            # Check if already excluded
            if not any(e['path'] == path for e in self.exclusions):
                self.exclusions.append({
                    'path': path,
                    'type': item_type,
                    'timestamp': current_time
                })
                self.update_status(f"Added to exclusions: {path}")

        self.save_exclusions()
        self.refresh_exclusions_tree()
        self.check_changes()  # Refresh changes list

    def remove_from_exclusions(self):
        """Remove selected items from exclusions list."""
        selected_items = self.exclusions_tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select items to remove from exclusions!")
            return

        for item in selected_items:
            values = self.exclusions_tree.item(item)['values']
            path = values[0]
            self.exclusions = [e for e in self.exclusions if e['path'] != path]
            self.update_status(f"Removed from exclusions: {path}")

        self.save_exclusions()
        self.refresh_exclusions_tree()
        self.check_changes()

    def is_excluded(self, path):
        """Check if a path is in the exclusions list."""
        return any(e['path'] == path for e in self.exclusions)

if __name__ == "__main__":
    app = FolderMonitor()
    app.run()
















# import os
# import json
# import shutil
# from tkinter import Tk, Button, Label, filedialog, messagebox
#
# # Path to save snapshot data (ensure it's in the script's directory)
# SNAPSHOT_FILE = os.path.join(os.path.dirname(__file__), "snapshot.json")
#
# def take_snapshot(folder_paths):
#     """Creates a snapshot of all files and folders in specified folder paths."""
#     snapshot = {}
#     for path in folder_paths:
#         if os.path.exists(path):
#             # Capture files and folders, exclude the snapshot file itself
#             snapshot[path] = [item for item in os.listdir(path)
#                               if os.path.join(path, item) != SNAPSHOT_FILE]
#     with open(SNAPSHOT_FILE, "w") as f:
#         json.dump(snapshot, f)
#     messagebox.showinfo("Snapshot", "Snapshot taken and saved.")
#     print("Snapshot saved to:", SNAPSHOT_FILE)  # Debug print
#
# def load_snapshot():
#     """Loads the saved snapshot if it exists."""
#     if os.path.exists(SNAPSHOT_FILE):
#         with open(SNAPSHOT_FILE, "r") as f:
#             try:
#                 return json.load(f)
#             except json.JSONDecodeError:
#                 messagebox.showerror("Error", "Snapshot file corrupted.")
#                 return {}
#     messagebox.showinfo("Info", "No snapshot found, please take a snapshot first.")
#     return {}
#
# def delete_new_items(snapshot):
#     """Deletes any new files or folders not in the snapshot."""
#     for path, original_items in snapshot.items():
#         if os.path.exists(path):
#             current_items = [item for item in os.listdir(path)
#                              if os.path.join(path, item) != SNAPSHOT_FILE]
#             new_items = set(current_items) - set(original_items)
#
#             for item in new_items:
#                 full_path = os.path.join(path, item)
#                 if os.path.isdir(full_path):
#                     shutil.rmtree(full_path)
#                 else:
#                     os.remove(full_path)
#                 print(f"Deleted: {full_path}")
#     messagebox.showinfo("Cleanup", "Deleted all new files and folders not in the snapshot.")
#
# def add_folder():
#     """Open folder selection dialog and add folder to monitored list."""
#     folder = filedialog.askdirectory()
#     if folder:
#         folder_paths.append(folder)
#         folders_label["text"] = "\n".join(folder_paths)
#
# def create_snapshot():
#     """Create a snapshot of the specified folders."""
#     take_snapshot(folder_paths)
#
# def delete_all_new():
#     """Delete all new items not in the snapshot for the specified folders."""
#     snapshot = load_snapshot()
#     if snapshot:
#         delete_new_items(snapshot)
#     else:
#         messagebox.showerror("Error", "No snapshot found. Please take a snapshot first.")
#
# # Initialize folder paths list
# folder_paths = []
#
# # GUI setup
# root = Tk()
# root.title("File and Folder Monitor and Cleaner")
# root.geometry("400x300")
#
# # Labels and buttons
# Label(root, text="Monitored Folders:").pack()
# folders_label = Label(root, text="")
# folders_label.pack()
#
# Button(root, text="Add Folder", command=add_folder).pack(pady=5)
# Button(root, text="Take Snapshot", command=create_snapshot).pack(pady=5)
# Button(root, text="Delete New Files and Folders", command=delete_all_new).pack(pady=5)
#
# root.mainloop()
#










# import os
# import json
# import shutil
# from tkinter import Tk, Button, Label, filedialog, messagebox
#
# # Path to save snapshot data
# SNAPSHOT_FILE = "snapshot.json"
#
# def take_snapshot(folder_paths):
#     """Creates a snapshot of subfolders in the specified folder paths."""
#     snapshot = {}
#     for path in folder_paths:
#         if os.path.exists(path):
#             snapshot[path] = [sub for sub in os.listdir(path) if os.path.isdir(os.path.join(path, sub))]
#     with open(SNAPSHOT_FILE, "w") as f:
#         json.dump(snapshot, f)
#     messagebox.showinfo("Snapshot", "Snapshot taken and saved.")
#
# def load_snapshot():
#     """Loads the saved snapshot if it exists."""
#     if os.path.exists(SNAPSHOT_FILE):
#         with open(SNAPSHOT_FILE, "r") as f:
#             return json.load(f)
#     return {}
#
# def delete_new_folders(snapshot):
#     """Deletes new folders not in the snapshot."""
#     for path, original_folders in snapshot.items():
#         if os.path.exists(path):
#             current_folders = [sub for sub in os.listdir(path) if os.path.isdir(os.path.join(path, sub))]
#             new_folders = set(current_folders) - set(original_folders)
#
#             for folder in new_folders:
#                 full_path = os.path.join(path, folder)
#                 shutil.rmtree(full_path)
#                 print(f"Deleted folder: {full_path}")
#     messagebox.showinfo("Cleanup", "Deleted all new subfolders not in the snapshot.")
#
# def add_folder():
#     """Open folder selection dialog and add folder to monitored list."""
#     folder = filedialog.askdirectory()
#     if folder:
#         folder_paths.append(folder)
#         folders_label["text"] = "\n".join(folder_paths)
#
# def create_snapshot():
#     """Create a snapshot of the specified folders."""
#     take_snapshot(folder_paths)
#
# def delete_all_new():
#     """Delete all new folders not in the snapshot for the specified folders."""
#     snapshot = load_snapshot()
#     if snapshot:
#         delete_new_folders(snapshot)
#     else:
#         messagebox.showerror("Error", "No snapshot found. Please take a snapshot first.")
#
# # Initialize folder paths list
# folder_paths = []
#
# # GUI setup
# root = Tk()
# root.title("Folder Monitor and Cleaner")
# root.geometry("400x300")
#
# # Labels and buttons
# Label(root, text="Monitored Folders:").pack()
# folders_label = Label(root, text="")
# folders_label.pack()
#
# Button(root, text="Add Folder", command=add_folder).pack(pady=5)
# Button(root, text="Take Snapshot", command=create_snapshot).pack(pady=5)
# Button(root, text="Delete New Subfolders", command=delete_all_new).pack(pady=5)
#
# root.mainloop()
