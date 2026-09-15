import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import csv
import json
from datetime import datetime
import glob

class AttendanceViewer:
    def __init__(self, master):
        self.master = master
        self.master.title("Attendance Records Viewer")
        self.master.geometry("1100x650")
        self.master.resizable(True, True)
        
        # Store the attendance directory path
        self.attendance_dir = "attendance"
        self.selected_date = None  # No date selected initially
        self.current_file_mode = "all"  # Track whether we're showing all files or a specific file
        
        # Load label map for name mapping
        self.label_map = self.load_label_map()
        
        # Configure styles
        self.style = ttk.Style()
        self.style.configure('Treeview', font=('Arial', 10), rowheight=25)
        self.style.configure('Treeview.Heading', font=('Arial', 11, 'bold'))
        self.style.map('Treeview', background=[('selected', '#347083')])
        
        # Main container
        self.main_container = ttk.Frame(self.master)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create widgets
        self.create_widgets()
        
        # Load initial data (show all records)
        self.load_data()
    
    def load_label_map(self):
        """Load the label map from JSON file"""
        try:
            if os.path.exists("label_map.json"):
                with open("label_map.json", "r") as f:
                    data = json.load(f)
                return {int(v): k for k, v in data.items()}
            return {}
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load label map: {str(e)}")
            return {}
    
    def create_widgets(self):
        # Filter frame
        filter_frame = ttk.Frame(self.main_container)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Date filter section
        date_filter_frame = ttk.Frame(filter_frame)
        date_filter_frame.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Selected date display
        self.selected_date_var = tk.StringVar()
        self.selected_date_var.set("Showing all records")
        ttk.Label(date_filter_frame, textvariable=self.selected_date_var).pack(side=tk.LEFT, padx=10)
        
        # Show All button
        ttk.Button(date_filter_frame, text="Show All Files", 
                  command=self.show_all_files).pack(side=tk.LEFT, padx=5)
        
        # File selection
        file_frame = ttk.Frame(filter_frame)
        file_frame.pack(side=tk.LEFT, padx=20)
        
        ttk.Label(file_frame, text="File with Date:").pack(side=tk.LEFT)
        self.file_var = tk.StringVar()
        file_dropdown = ttk.Combobox(file_frame, textvariable=self.file_var, width=20, state="readonly")
        file_dropdown.pack(side=tk.LEFT, padx=5)
        file_dropdown.bind('<<ComboboxSelected>>', self.file_selected)
        self.file_dropdown = file_dropdown
        
        # Search section
        search_frame = ttk.Frame(filter_frame)
        search_frame.pack(side=tk.RIGHT, padx=5, fill=tk.X, expand=True)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.search_entry.bind('<Return>', lambda e: self.search_records())
        
        ttk.Button(search_frame, text="Search", command=self.search_records).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Clear", command=self.clear_search).pack(side=tk.LEFT, padx=5)
        
        # Treeview frame
        tree_frame = ttk.Frame(self.main_container)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create Treeview with scrollbars
        self.tree = ttk.Treeview(tree_frame, columns=("Date", "Time", "Enrollment", "Name"), show="headings")
        
        # Define headings
        columns = {
            "Date": {"text": "Date", "width": 120, "anchor": tk.CENTER},
            "Time": {"text": "Time", "width": 100, "anchor": tk.CENTER},
            "Enrollment": {"text": "Enrollment", "width": 150, "anchor": tk.CENTER},
            "Name": {"text": "Name", "width": 200, "anchor": tk.CENTER}
        }
        
        for col, settings in columns.items():
            self.tree.heading(col, text=settings["text"])
            self.tree.column(col, width=settings["width"], anchor=settings["anchor"])
        
        # Add scrollbars
        y_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        x_scroll = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscroll=y_scroll.set, xscroll=x_scroll.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        
        # Configure grid weights
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Button frame
        btn_frame = ttk.Frame(self.main_container)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="Refresh", command=self.refresh_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Export to CSV", command=self.export_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Close", command=self.master.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.main_container, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, pady=(5, 0))
    
    def refresh_data(self):
        """Refresh the file list and data"""
        self.update_file_list()
        if self.current_file_mode == "all":
            self.load_data()
        else:
            self.file_selected()
    
    def update_file_list(self):
        """Update the dropdown with available attendance files"""
        files = glob.glob(os.path.join(self.attendance_dir, "attendance_*.csv"))
        files.sort(reverse=True)  # Most recent first
        
        file_names = [os.path.basename(f) for f in files]
        self.file_dropdown['values'] = file_names
        
        if file_names and self.current_file_mode != "all":
            self.file_var.set(file_names[0])
    
    def show_all_files(self):
        """Show data from all files in the attendance directory"""
        self.current_file_mode = "all"
        self.selected_date_var.set("Showing all files")
        self.file_var.set("")  # Clear file selection
        self.load_data()
    
    def file_selected(self, event=None):
        """Handle file selection from dropdown"""
        selected_file = self.file_var.get()
        if selected_file:
            self.current_file_mode = "single"
            file_path = os.path.join(self.attendance_dir, selected_file)
            self.load_data(file_path)
    
    def open_date_picker(self):
        """Open calendar popup for date selection"""
        top = tk.Toplevel(self.master)
        top.title("Select Date")
        top.geometry("300x250")
        top.grab_set()  # Make the dialog modal
        
        cal = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        def set_date():
            selected_date = cal.get_date()
            self.selected_date = selected_date
            self.filter_by_date(selected_date)
            top.destroy()
        
        ttk.Button(top, text="OK", command=set_date).pack(pady=5)
    
    def filter_by_date(self, selected_date):
        """Filter records based on selected date"""
        # Parse selected date
        try:
            selected_dt = datetime.strptime(selected_date, "%Y-%m-%d")
            formatted_selected_date = selected_dt.strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD format.")
            return
        
        # Clear previous selection
        for item in self.tree.selection():
            self.tree.selection_remove(item)
        
        # Show only records matching the selected date
        found_items = []
        for item in self.tree.get_children():
            date_str = self.tree.item(item, "values")[0]
            if date_str == formatted_selected_date:
                self.tree.item(item, tags=('visible',))
                found_items.append(item)
            else:
                self.tree.item(item, tags=('hidden',))
        
        # Hide non-matching items
        self.tree.tag_configure('visible', background='white')
        self.tree.tag_configure('hidden', background='light gray')
        
        if found_items:
            self.selected_date_var.set(f"Showing records for: {formatted_selected_date}")
            self.status_var.set(f"Found {len(found_items)} records for {formatted_selected_date}")
            
            # Select and scroll to first matching item
            if found_items:
                self.tree.selection_add(found_items[0])
                self.tree.see(found_items[0])
        else:
            messagebox.showinfo("Date Filter", "No records found for selected date")
            self.status_var.set(f"No records found for {formatted_selected_date}")
    
    def show_all_records(self):
        """Show all records without any date filter"""
        self.selected_date = None
        self.selected_date_var.set("Showing all records")
        
        # Make all items visible
        for item in self.tree.get_children():
            self.tree.item(item, tags=('visible',))
        
        # Clear any selection
        for item in self.tree.selection():
            self.tree.selection_remove(item)
            
        self.status_var.set("Showing all records")
    
    def load_data(self, file_path=None):
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Update file list
        self.update_file_list()
        
        # If no specific file provided, load all files
        if file_path is None:
            files = glob.glob(os.path.join(self.attendance_dir, "attendance_*.csv"))
            file_count = len(files)
        else:
            files = [file_path]
            file_count = 1
        
        record_count = 0
        last_loaded_file = None
        
        for f in files:
            try:
                if not os.path.exists(f):
                    continue
                
                last_loaded_file = f
                
                with open(f, mode='r', newline='') as csvfile:
                    reader = csv.DictReader(csvfile)
                    
                    for row in reader:
                        # Get values with defaults
                        date = row.get('Date', 'Unknown')
                        time = row.get('Time', 'Unknown')
                        enrollment = row.get('Enrollment', 'Unknown')
                        name = row.get('Name', 'Unknown')
                        
                        # If name is missing, try to get it from label_map
                        if name == 'Unknown' and enrollment != 'Unknown':
                            for label_id, label_name in self.label_map.items():
                                if enrollment in label_name:
                                    name = label_name.split('_', 1)[1] if '_' in label_name else label_name
                                    break
                        
                        self.tree.insert("", tk.END, values=(date, time, enrollment, name))
                        record_count += 1
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load data from {f}: {str(e)}")
        
        # Sort by date (newest first)
        self.tree.heading("Date", command=lambda: self.sort_by_date(False))
        self.sort_by_date(True)
        
        if self.current_file_mode == "all":
            self.status_var.set(f"Loaded {record_count} records from {file_count} file(s)")
            self.selected_date_var.set("Showing all files")
        else:
            display_name = os.path.basename(last_loaded_file) if last_loaded_file else "unknown"
            self.status_var.set(f"Loaded {record_count} records from {display_name}")
            self.selected_date_var.set(f"Showing file: {display_name}")
    
    def sort_by_date(self, descending=True):
        """Sort tree by date column"""
        data = [(self.tree.set(child, 'Date'), child) for child in self.tree.get_children('')]
        
        # Try to sort as dates
        try:
            data.sort(key=lambda x: datetime.strptime(x[0], "%Y-%m-%d"), reverse=descending)
        except:
            data.sort(reverse=descending)
        
        for index, (val, child) in enumerate(data):
            self.tree.move(child, '', index)
        
        # Reverse sort order for next click
        self.tree.heading("Date", command=lambda: self.sort_by_date(not descending))
    
    def export_data(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save attendance records"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', newline='') as file:
                writer = csv.writer(file)
                # Write header
                writer.writerow(["Date", "Time", "Enrollment", "Name"])
                
                # Write data
                for item in self.tree.get_children():
                    values = self.tree.item(item)['values']
                    writer.writerow(values)
            
            self.status_var.set(f"Data exported to {os.path.basename(file_path)}")
            messagebox.showinfo("Success", f"Data exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")
            self.status_var.set(f"Export error: {str(e)}")
    
    def search_records(self):
        query = self.search_entry.get().strip().lower()
        if not query:
            self.clear_search()
            return
        
        # Clear previous highlights
        for item in self.tree.selection():
            self.tree.selection_remove(item)
        
        # Search through all items
        found_items = []
        for item in self.tree.get_children():
            values = [str(v).lower() for v in self.tree.item(item)['values']]
            if any(query in value for value in values):
                found_items.append(item)
                self.tree.selection_add(item)
                self.tree.see(item)
        
        if found_items:
            self.status_var.set(f"Found {len(found_items)} matching records")
        else:
            messagebox.showinfo("Search", "No matching records found")
            self.status_var.set("No matching records found")
    
    def clear_search(self):
        self.search_entry.delete(0, tk.END)
        for item in self.tree.selection():
            self.tree.selection_remove(item)
        self.status_var.set("Search cleared")

def main():
    root = tk.Tk()
    
    app = AttendanceViewer(root)
    
    # Center the window
    window_width = 1100
    window_height = 650
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()