#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AGAMART Database Management Desktop Application
تطبيق سطح المكتب لإدارة قاعدة البيانات
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv
from datetime import datetime
import os

class DatabaseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AGAMART Database Management")
        self.root.geometry("1200x700")
        self.root.configure(bg='#1a1a2e')
        
        # Database path
        self.db_path = 'store.db'
        
        # Check if database exists
        if not os.path.exists(self.db_path):
            messagebox.showerror("Error", "Database file not found: {}".format(self.db_path))
            self.root.destroy()
            return
        
        self.setup_ui()
        self.load_tables()
        
    def setup_ui(self):
        # Main container
        main_frame = tk.Frame(self.root, bg='#1a1a2e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='#16213e', relief=tk.RAISED, bd=2)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(
            header_frame,
            text="🏪 AGAMART Database Management",
            font=('Arial', 16, 'bold'),
            bg='#16213e',
            fg='#0f3460'
        )
        title_label.pack(pady=15)
        
        # Top frame with controls
        control_frame = tk.Frame(main_frame, bg='#1a1a2e')
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Search box
        search_label = tk.Label(
            control_frame,
            text="Search:",
            font=('Arial', 10),
            bg='#1a1a2e',
            fg='white'
        )
        search_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search)
        search_entry = tk.Entry(
            control_frame,
            textvariable=self.search_var,
            font=('Arial', 10),
            width=30,
            bg='#16213e',
            fg='white',
            insertbackground='white'
        )
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Export button
        export_btn = tk.Button(
            control_frame,
            text="📥 Export to CSV",
            command=self.export_to_csv,
            font=('Arial', 10, 'bold'),
            bg='#27ae60',
            fg='white',
            relief=tk.RAISED,
            bd=3,
            padx=10,
            pady=5
        )
        export_btn.pack(side=tk.LEFT, padx=10)
        
        # Refresh button
        refresh_btn = tk.Button(
            control_frame,
            text="🔄 Refresh",
            command=self.refresh_data,
            font=('Arial', 10, 'bold'),
            bg='#3498db',
            fg='white',
            relief=tk.RAISED,
            bd=3,
            padx=10,
            pady=5
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Statistics frame
        stats_frame = tk.Frame(main_frame, bg='#16213e', relief=tk.RAISED, bd=2)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        stats_label = tk.Label(
            stats_frame,
            text="Statistics",
            font=('Arial', 12, 'bold'),
            bg='#16213e',
            fg='#0f3460'
        )
        stats_label.pack(pady=5)
        
        self.stats_frame_inner = tk.Frame(stats_frame, bg='#16213e')
        self.stats_frame_inner.pack(fill=tk.X, padx=10, pady=5)
        
        # Main content frame
        content_frame = tk.Frame(main_frame, bg='#1a1a2e')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Table list
        left_panel = tk.Frame(content_frame, bg='#16213e', relief=tk.RAISED, bd=2, width=200)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        table_label = tk.Label(
            left_panel,
            text="Tables",
            font=('Arial', 12, 'bold'),
            bg='#16213e',
            fg='#0f3460'
        )
        table_label.pack(pady=10)
        
        # Scrollbar for table list
        table_scroll = tk.Scrollbar(left_panel)
        table_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.table_listbox = tk.Listbox(
            left_panel,
            yscrollcommand=table_scroll.set,
            font=('Arial', 10),
            bg='#1a1a2e',
            fg='white',
            selectbackground='#3498db',
            selectforeground='white',
            relief=tk.FLAT,
            bd=0
        )
        self.table_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.table_listbox.bind('<<ListboxSelect>>', self.on_table_select)
        table_scroll.config(command=self.table_listbox.yview)
        
        # Right panel - Data display
        right_panel = tk.Frame(content_frame, bg='#1a1a2e')
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Treeview for data
        tree_frame = tk.Frame(right_panel, bg='#1a1a2e')
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.tree = ttk.Treeview(
            tree_frame,
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set,
            style='Custom.Treeview'
        )
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        v_scrollbar.config(command=self.tree.yview)
        h_scrollbar.config(command=self.tree.xview)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Custom.Treeview',
                        background='#1a1a2e',
                        foreground='white',
                        fieldbackground='#1a1a2e',
                        rowheight=25)
        style.configure('Custom.Treeview.Heading',
                        background='#16213e',
                        foreground='#0f3460',
                        font=('Arial', 10, 'bold'))
        style.map('Custom.Treeview',
                 background=[('selected', '#3498db')])
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = tk.Label(
            main_frame,
            textvariable=self.status_var,
            font=('Arial', 9),
            bg='#16213e',
            fg='white',
            anchor=tk.W,
            relief=tk.SUNKEN,
            bd=1
        )
        status_bar.pack(fill=tk.X, pady=(10, 0))
        
    def load_tables(self):
        """Load all tables from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = cursor.fetchall()
            
            self.table_listbox.delete(0, tk.END)
            self.tables_data = {}
            
            for table in tables:
                table_name = table[0]
                self.table_listbox.insert(tk.END, table_name)
                
                # Load table data
                try:
                    cursor.execute("SELECT * FROM {} LIMIT 1000".format(table_name))
                    columns = [description[0] for description in cursor.description]
                    rows = cursor.fetchall()
                    
                    self.tables_data[table_name] = {
                        'columns': columns,
                        'rows': rows
                    }
                except Exception as e:
                    print("Error loading table {}: {}".format(table_name, e))
                    self.tables_data[table_name] = {
                        'columns': [],
                        'rows': []
                    }
            
            conn.close()
            
            # Load statistics
            self.load_statistics()
            
            # Select first table
            if tables:
                self.table_listbox.selection_set(0)
                self.on_table_select(None)
                
        except Exception as e:
            messagebox.showerror("Error", "Error loading database: {}".format(str(e)))
    
    def load_statistics(self):
        """Load and display statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Clear existing stats
            for widget in self.stats_frame_inner.winfo_children():
                widget.destroy()
            
            # Get statistics for main tables
            stats_tables = {
                'Users': 'user',
                'Products': 'product',
                'Sales': 'sale',
                'Invoices': 'invoice',
                'Customers': 'customer',
                'Stores': 'store',
                'Purchase Orders': 'purchase_order',
                'Deliveries': 'delivery'
            }
            
            row = 0
            col = 0
            for label, table in stats_tables.items():
                try:
                    cursor.execute("SELECT COUNT(*) FROM {}".format(table))
                    count = cursor.fetchone()[0]
                    
                    stat_label = tk.Label(
                        self.stats_frame_inner,
                        text="{}: {}".format(label, count),
                        font=('Arial', 10, 'bold'),
                        bg='#16213e',
                        fg='#3498db',
                        padx=15,
                        pady=5
                    )
                    stat_label.grid(row=row, column=col, padx=5, pady=2, sticky='w')
                    
                    col += 1
                    if col > 3:
                        col = 0
                        row += 1
                except:
                    pass
            
            conn.close()
            
        except Exception as e:
            print("Error loading statistics: {}".format(str(e)))
    
    def on_table_select(self, event):
        """Handle table selection"""
        selection = self.table_listbox.curselection()
        if not selection:
            return
        
        table_name = self.table_listbox.get(selection[0])
        self.display_table(table_name)
    
    def display_table(self, table_name):
        """Display table data in treeview"""
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if table_name not in self.tables_data:
            return
        
        data = self.tables_data[table_name]
        columns = data['columns']
        rows = data['rows']
        
        # Configure tree columns
        self.tree['columns'] = columns
        self.tree['show'] = 'headings'
        
        # Set column headings and widths
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor=tk.W)
        
        # Insert data
        for row in rows:
            # Convert None to empty string and truncate long values
            display_row = []
            for val in row:
                if val is None:
                    display_row.append('')
                elif isinstance(val, str) and len(val) > 50:
                    display_row.append(val[:50] + '...')
                else:
                    display_row.append(str(val))
            
            self.tree.insert('', tk.END, values=display_row)
        
        # Update status
        self.status_var.set("Table: {} | Records: {}".format(table_name, len(rows)))
    
    def on_search(self, *args):
        """Handle search"""
        search_term = self.search_var.get().lower()
        
        if not search_term:
            # Reset to current table
            selection = self.table_listbox.curselection()
            if selection:
                table_name = self.table_listbox.get(selection[0])
                self.display_table(table_name)
            return
        
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Search in all tables
        found_count = 0
        for table_name, data in self.tables_data.items():
            columns = data['columns']
            rows = data['rows']
            
            for row in rows:
                # Check if search term is in any field
                row_str = ' '.join([str(val) if val else '' for val in row]).lower()
                if search_term in row_str:
                    # Find matching columns
                    matching_cols = []
                    matching_vals = []
                    for i, val in enumerate(row):
                        if val and search_term in str(val).lower():
                            matching_cols.append(columns[i])
                            matching_vals.append(str(val)[:50])
                    
                    if matching_cols:
                        # Create a display row
                        display_row = [''] * len(columns)
                        for i, col in enumerate(columns):
                            if col in matching_cols:
                                idx = matching_cols.index(col)
                                display_row[i] = matching_vals[idx]
                            elif row[i]:
                                display_row[i] = str(row[i])[:50]
                        
                        self.tree.insert('', tk.END, values=display_row)
                        found_count += 1
        
        self.status_var.set("Search results: {} matches".format(found_count))
    
    def export_to_csv(self):
        """Export current table to CSV"""
        selection = self.table_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a table to export")
            return
        
        table_name = self.table_listbox.get(selection[0])
        data = self.tables_data[table_name]
        
        # Ask for save location
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="{}_export.csv".format(table_name)
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write headers
                writer.writerow(data['columns'])
                
                # Write data
                for row in data['rows']:
                    writer.writerow([str(val) if val is not None else '' for val in row])
            
            messagebox.showinfo("Success", "Data exported to {}".format(filename))
            self.status_var.set("Exported {} to {}".format(table_name, filename))
            
        except Exception as e:
            messagebox.showerror("Error", "Error exporting data: {}".format(str(e)))
    
    def refresh_data(self):
        """Refresh database data"""
        self.status_var.set("Refreshing...")
        self.load_tables()
        self.status_var.set("Data refreshed")

def main():
    root = tk.Tk()
    app = DatabaseApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

