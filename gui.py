'''
GUI Application (Tkinter)
-------------------------
Description:
This file contains the graphical user interface for the database system.
The GUI allows the user to interact with the backend classes (Record, Table,
Database, Query, StorageManager) using buttons, forms, and visual tables.

Purpose:
- Provide a user-friendly interface for the database system.
- Allow users to insert, delete, edit, query, sort, save, and load records.
- Display table data visually using Tkinter widgets.

Current Step:
STEP 11 — Final GUI polish and usability improvements.
'''

import tkinter as tk
from tkinter import ttk, messagebox
from classes import Database, StorageManager, Record

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Database Manager")

        # Backend
        self.storage = StorageManager("test_database.json")
        self.db = self.storage.load()

        # Main frame
        self.main_frame = ttk.Frame(root, padding=20)
        self.main_frame.pack(fill="both", expand=True)

        # Title
        title = ttk.Label(self.main_frame, text="Database Manager", font=("Arial", 20))
        title.pack(pady=10)

        # Buttons frame
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(pady=20)

        # Row 1
        ttk.Button(self.button_frame, text="Insert Record", width=20, command=self.open_insert_form).grid(row=0, column=0, padx=10, pady=10)
        ttk.Button(self.button_frame, text="View Table", width=20, command=self.open_table_viewer).grid(row=0, column=1, padx=10, pady=10)

        # Row 2
        ttk.Button(self.button_frame, text="Query Records", width=20, command=self.open_query_window).grid(row=1, column=0, padx=10, pady=10)
        ttk.Button(self.button_frame, text="Sort Records", width=20, command=self.open_sort_window).grid(row=1, column=1, padx=10, pady=10)

        # Row 3
        ttk.Button(self.button_frame, text="Save Database", width=20, command=self.save_database).grid(row=2, column=0, padx=10, pady=10)
        ttk.Button(self.button_frame, text="Load Database", width=20, command=self.load_database).grid(row=2, column=1, padx=10, pady=10)

        # Row 4
        ttk.Button(self.button_frame, text="Delete Record", width=20, command=self.open_delete_window).grid(row=3, column=0, padx=10, pady=10)
        ttk.Button(self.button_frame, text="Edit Record", width=20, command=self.open_edit_window).grid(row=3, column=1, padx=10, pady=10)

    # Center popup windows (UPDATED)
    def center_window(self, window):
        window.update_idletasks()
        w = window.winfo_width()
        h = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (w // 2)
        y = (window.winfo_screenheight() // 2) - (h // 2)
        window.geometry(f"+{x}+{y}")
        window.resizable(False, False)

    def open_table_viewer(self):
        if hasattr(self, "viewer") and self.viewer.winfo_exists():
            self.viewer.lift()
            return

        self.viewer = tk.Toplevel(self.root)
        self.viewer.title("Table Viewer")
        self.center_window(self.viewer)

        self.tree = ttk.Treeview(self.viewer, columns=("id", "name", "age"), show="headings")
        self.tree.pack(fill="both", expand=True, padx=20, pady=20)

        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("age", text="Age")

        self.tree.column("id", width=50)
        self.tree.column("name", width=150)
        self.tree.column("age", width=80)

        self.refresh_table_view()

    def refresh_table_view(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        table = self.db.get_table("students")
        if table:
            for record in table.records:
                self.tree.insert("", "end", values=(record.id, record.fields.get("name", ""), record.fields.get("age", "")))

    def open_insert_form(self):
        form = tk.Toplevel(self.root)
        form.title("Insert Record")
        self.center_window(form)

        ttk.Label(form, text="ID:").grid(row=0, column=0, padx=10, pady=5)
        id_entry = ttk.Entry(form)
        id_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(form, text="Name:").grid(row=1, column=0, padx=10, pady=5)
        name_entry = ttk.Entry(form)
        name_entry.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(form, text="Age:").grid(row=2, column=0, padx=10, pady=5)
        age_entry = ttk.Entry(form)
        age_entry.grid(row=2, column=1, padx=10, pady=5)

        def submit_record():
            try:
                record_id = int(id_entry.get())
                name = name_entry.get()
                age = int(age_entry.get())

                table = self.db.get_table("students")
                if not table:
                    messagebox.showerror("Error", "Students table not found.")
                    return

                # Duplicate detection
                if table.record_exists(record_id):
                    messagebox.showerror("Error", "A record with this ID already exists.")
                    return

                new_record = Record(record_id, {"name": name, "age": age})
                table.insert(new_record)

                messagebox.showinfo("Success", "Record inserted successfully!")

                if hasattr(self, "tree"):
                    self.refresh_table_view()

                form.destroy()

            except ValueError:
                messagebox.showerror("Error", "Invalid input. ID and Age must be numbers.")

        ttk.Button(form, text="Submit", command=submit_record).grid(row=3, column=0, columnspan=2, pady=10)

    def save_database(self):
        self.storage.save(self.db)
        self.storage.backup()
        messagebox.showinfo("Success", "Database saved and backup created!")

    def load_database(self):
        self.db = self.storage.load()
        messagebox.showinfo("Success", "Database loaded successfully!")

        if hasattr(self, "tree"):
            self.refresh_table_view()

    def open_edit_window(self):
        edit_win = tk.Toplevel(self.root)
        edit_win.title("Edit Record")
        self.center_window(edit_win)

        ttk.Label(edit_win, text="Enter ID:").grid(row=0, column=0, padx=10, pady=5)
        id_entry = ttk.Entry(edit_win)
        id_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(edit_win, text="Name:").grid(row=1, column=0, padx=10, pady=5)
        name_entry = ttk.Entry(edit_win)
        name_entry.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(edit_win, text="Age:").grid(row=2, column=0, padx=10, pady=5)
        age_entry = ttk.Entry(edit_win)
        age_entry.grid(row=2, column=1, padx=10, pady=5)

        def load_record():
            try:
                record_id = int(id_entry.get())
                table = self.db.get_table("students")

                for r in table.records:
                    if r.id == record_id:
                        name_entry.delete(0, tk.END)
                        age_entry.delete(0, tk.END)
                        name_entry.insert(0, r.fields.get("name", ""))
                        age_entry.insert(0, r.fields.get("age", ""))
                        return

                messagebox.showerror("Error", "Record not found.")

            except ValueError:
                messagebox.showerror("Error", "ID must be a number.")

        def save_changes():
            try:
                record_id = int(id_entry.get())
                new_name = name_entry.get()
                new_age = int(age_entry.get())

                table = self.db.get_table("students")
                updated = table.update_record(record_id, {"name": new_name, "age": new_age})

                if updated:
                    messagebox.showinfo("Success", "Record updated successfully!")
                    if hasattr(self, "tree"):
                        self.refresh_table_view()
                    edit_win.destroy()
                else:
                    messagebox.showerror("Error", "Record not found.")

            except ValueError:
                messagebox.showerror("Error", "Age must be a number.")

        ttk.Button(edit_win, text="Load", command=load_record).grid(row=3, column=0, pady=10)
        ttk.Button(edit_win, text="Save", command=save_changes).grid(row=3, column=1, pady=10)

    def open_query_window(self):
        query_win = tk.Toplevel(self.root)
        query_win.title("Query Records")
        self.center_window(query_win)

        ttk.Label(query_win, text="ID:").grid(row=0, column=0, padx=10, pady=5)
        id_entry = ttk.Entry(query_win)
        id_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(query_win, text="Name:").grid(row=1, column=0, padx=10, pady=5)
        name_entry = ttk.Entry(query_win)
        name_entry.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(query_win, text="Age:").grid(row=2, column=0, padx=10, pady=5)
        age_entry = ttk.Entry(query_win)
        age_entry.grid(row=2, column=1, padx=10, pady=5)

        results = ttk.Treeview(query_win, columns=("id", "name", "age"), show="headings")
        results.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        results.heading("id", text="ID")
        results.heading("name", text="Name")
        results.heading("age", text="Age")

        def run_query():
            for row in results.get_children():
                results.delete(row)

            table = self.db.get_table("students")
            if not table:
                messagebox.showerror("Error", "Students table not found.")
                return

            id_val = id_entry.get().strip()
            name_val = name_entry.get().strip().lower()
            age_val = age_entry.get().strip()

            for record in table.records:
                match = True
                if id_val and str(record.id) != id_val:
                    match = False
                if name_val and name_val not in record.fields.get("name", "").lower():
                    match = False
                if age_val and str(record.fields.get("age", "")) != age_val:
                    match = False

                if match:
                    results.insert("", "end", values=(record.id, record.fields.get("name", ""), record.fields.get("age", "")))

        ttk.Button(query_win, text="Search", command=run_query).grid(row=3, column=0, columnspan=2, pady=10)

    def open_sort_window(self):
        sort_win = tk.Toplevel(self.root)
        sort_win.title("Sort Records")
        self.center_window(sort_win)

        ttk.Label(sort_win, text="Sort by:").grid(row=0, column=0, padx=10, pady=5)
        field_var = tk.StringVar()
        field_dropdown = ttk.Combobox(sort_win, textvariable=field_var, values=["ID", "Name", "Age"], state="readonly")
        field_dropdown.grid(row=0, column=1, padx=10, pady=5)
        field_dropdown.current(0)

        ttk.Label(sort_win, text="Order:").grid(row=1, column=0, padx=10, pady=5)
        order_var = tk.StringVar()
        order_dropdown = ttk.Combobox(sort_win, textvariable=order_var, values=["Ascending", "Descending"], state="readonly")
        order_dropdown.grid(row=1, column=1, padx=10, pady=5)
        order_dropdown.current(0)

        results = ttk.Treeview(sort_win, columns=("id", "name", "age"), show="headings")
        results.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        results.heading("id", text="ID")
        results.heading("name", text="Name")
        results.heading("age", text="Age")

        def run_sort():
            for row in results.get_children():
                results.delete(row)

            table = self.db.get_table("students")
            if not table:
                messagebox.showerror("Error", "Students table not found.")
                return

            field = field_var.get()
            order = order_var.get()

            if field == "ID":
                key_func = lambda r: r.id
            elif field == "Name":
                key_func = lambda r: r.fields.get("name", "").lower()
            else:
                key_func = lambda r: r.fields.get("age", 0)

            reverse = (order == "Descending")

            sorted_records = sorted(table.records, key=key_func, reverse=reverse)

            for record in sorted_records:
                results.insert("", "end", values=(record.id, record.fields.get("name", ""), record.fields.get("age", "")))

        ttk.Button(sort_win, text="Sort", command=run_sort).grid(row=2, column=0, columnspan=2, pady=10)

    def open_delete_window(self):
        delete_win = tk.Toplevel(self.root)
        delete_win.title("Delete Record")
        self.center_window(delete_win)

        ttk.Label(delete_win, text="Enter ID to delete:").grid(row=0, column=0, padx=10, pady=5)
        id_entry = ttk.Entry(delete_win)
        id_entry.grid(row=0, column=1, padx=10, pady=5)

        def delete_record():
            try:
                record_id = int(id_entry.get())
                table = self.db.get_table("students")

                if not table:
                    messagebox.showerror("Error", "Students table not found.")
                    return

                exists = any(r.id == record_id for r in table.records)
                if not exists:
                    messagebox.showerror("Error", "Record not found.")
                    return

                confirm = messagebox.askyesno("Confirm Delete", f"Delete record with ID {record_id}?")
                if not confirm:
                    return

                table.records = [r for r in table.records if r.id != record_id]
                messagebox.showinfo("Success", "Record deleted successfully!")

                if hasattr(self, "tree"):
                    self.refresh_table_view()

                delete_win.destroy()

            except ValueError:
                messagebox.showerror("Error", "ID must be a number.")

        ttk.Button(delete_win, text="Delete", command=delete_record).grid(row=1, column=0, columnspan=2, pady=10)


# Run the GUI
root = tk.Tk()
app = App(root)
root.mainloop()
