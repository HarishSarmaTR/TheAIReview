#!/usr/bin/env python3
"""
Admin Management Tool for AI Review Tool
Provides a GUI interface to manage admin users safely
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import getpass
from datetime import datetime

class AdminManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI Review Tool - Admin Management")
        self.root.geometry("800x600")
        
        # Configuration file path
        self.config_file = "access_control.json"
        if not os.path.exists(self.config_file):
            self.config_file = os.path.join("AIReview", "access_control.json")
        
        self.current_config = self.load_config()
        self.setup_ui()
        
    def load_config(self):
        """Load current admin configuration"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load configuration: {e}")
            return {"admin_users": [], "allowed_users": []}
    
    def save_config(self):
        """Save configuration with backup"""
        try:
            # Create backup
            backup_file = f"{self.config_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with open(backup_file, 'w') as f:
                json.dump(self.current_config, f, indent=2)
            
            # Save new configuration
            with open(self.config_file, 'w') as f:
                json.dump(self.current_config, f, indent=2)
            
            messagebox.showinfo("Success", f"Configuration saved successfully!\nBackup created: {backup_file}")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Could not save configuration: {e}")
            return False
    
    def setup_ui(self):
        """Setup the admin management interface"""
        # Title
        title_label = tk.Label(self.root, text="AI Review Tool - Admin Management", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Current admin info
        info_frame = tk.Frame(self.root)
        info_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Label(info_frame, text=f"Current User: {getpass.getuser()}", 
                font=("Arial", 10)).pack(anchor="w")
        tk.Label(info_frame, text=f"Config File: {self.config_file}", 
                font=("Arial", 10)).pack(anchor="w")
        
        # Admin list frame
        list_frame = tk.LabelFrame(self.root, text="Current Admin Users", font=("Arial", 12, "bold"))
        list_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Admin listbox with scrollbar
        list_container = tk.Frame(list_frame)
        list_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(list_container)
        scrollbar.pack(side="right", fill="y")
        
        self.admin_listbox = tk.Listbox(list_container, yscrollcommand=scrollbar.set, 
                                       font=("Consolas", 10))
        self.admin_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.admin_listbox.yview)
        
        # Buttons frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10, padx=20, fill="x")
        
        # Add admin button
        tk.Button(button_frame, text="Add Admin", command=self.add_admin,
                 bg="green", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        
        # Remove admin button
        tk.Button(button_frame, text="Remove Admin", command=self.remove_admin,
                 bg="red", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        
        # Refresh button
        tk.Button(button_frame, text="Refresh", command=self.refresh_list,
                 bg="blue", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        
        # Save button
        tk.Button(button_frame, text="Save Changes", command=self.save_config,
                 bg="orange", fg="white", font=("Arial", 10, "bold")).pack(side="right", padx=5)
        
        # Instructions
        instructions = tk.Text(self.root, height=4, wrap="word", font=("Arial", 9))
        instructions.pack(pady=10, padx=20, fill="x")
        instructions.insert("1.0", 
            "Instructions:\n"
            "• Add admins using system username, network username, or email address\n"
            "• Multiple identifiers per person are supported for redundancy\n"
            "• Changes are saved to access_control.json with automatic backup\n"
            "• Restart the AI Review Tool for changes to take effect")
        instructions.config(state="disabled")
        
        self.refresh_list()
    
    def refresh_list(self):
        """Refresh the admin list display"""
        self.current_config = self.load_config()
        self.admin_listbox.delete(0, tk.END)
        
        admin_users = self.current_config.get("admin_users", [])
        for i, admin in enumerate(admin_users, 1):
            self.admin_listbox.insert(tk.END, f"{i:2d}. {admin}")
    
    def add_admin(self):
        """Add a new admin user"""
        dialog = AddAdminDialog(self.root)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            admin_identifier = dialog.result.strip()
            if admin_identifier:
                if admin_identifier not in self.current_config["admin_users"]:
                    self.current_config["admin_users"].append(admin_identifier)
                    self.refresh_list()
                    messagebox.showinfo("Success", f"Admin added: {admin_identifier}")
                else:
                    messagebox.showwarning("Duplicate", f"Admin already exists: {admin_identifier}")
    
    def remove_admin(self):
        """Remove selected admin user"""
        selection = self.admin_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selection", "Please select an admin to remove")
            return
        
        index = selection[0]
        admin_users = self.current_config.get("admin_users", [])
        
        if index < len(admin_users):
            admin_to_remove = admin_users[index]
            
            # Confirm removal
            if messagebox.askyesno("Confirm Removal", 
                                  f"Are you sure you want to remove admin:\n{admin_to_remove}"):
                admin_users.pop(index)
                self.refresh_list()
                messagebox.showinfo("Success", f"Admin removed: {admin_to_remove}")
    
    def run(self):
        """Start the admin management interface"""
        self.root.mainloop()

class AddAdminDialog:
    def __init__(self, parent):
        self.result = None
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add New Admin")
        self.dialog.geometry("500x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 150, parent.winfo_rooty() + 100))
        
        self.setup_dialog()
    
    def setup_dialog(self):
        """Setup the add admin dialog"""
        # Title
        tk.Label(self.dialog, text="Add New Admin User", 
                font=("Arial", 14, "bold")).pack(pady=10)
        
        # Instructions
        instructions = tk.Text(self.dialog, height=6, wrap="word", font=("Arial", 9))
        instructions.pack(pady=10, padx=20, fill="x")
        instructions.insert("1.0", 
            "Enter one of the following for the new admin:\n\n"
            "• System Username: e.g., '6126175'\n"
            "• Network Username: e.g., 'harish.sarma'\n"
            "• Email Address: e.g., 'user@thomsonreuters.com'\n"
            "• Display Name: e.g., 'John Smith'\n\n"
            "You can add multiple entries for the same person for redundancy.")
        instructions.config(state="disabled")
        
        # Entry frame
        entry_frame = tk.Frame(self.dialog)
        entry_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Label(entry_frame, text="Admin Identifier:", font=("Arial", 10, "bold")).pack(anchor="w")
        self.entry = tk.Entry(entry_frame, font=("Arial", 11), width=50)
        self.entry.pack(fill="x", pady=5)
        self.entry.focus()
        
        # Buttons
        button_frame = tk.Frame(self.dialog)
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Add", command=self.ok_clicked,
                 bg="green", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=10)
        tk.Button(button_frame, text="Cancel", command=self.cancel_clicked,
                 bg="gray", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=10)
        
        # Bind Enter key
        self.dialog.bind('<Return>', lambda e: self.ok_clicked())
        self.dialog.bind('<Escape>', lambda e: self.cancel_clicked())
    
    def ok_clicked(self):
        """Handle OK button click"""
        self.result = self.entry.get()
        self.dialog.destroy()
    
    def cancel_clicked(self):
        """Handle Cancel button click"""
        self.result = None
        self.dialog.destroy()

if __name__ == "__main__":
    # Check if running from correct directory
    if not os.path.exists("access_control.json") and not os.path.exists("AIReview/access_control.json"):
        print("Error: access_control.json not found!")
        print("Please run this script from the AI Review Tool directory.")
        input("Press Enter to exit...")
        exit(1)
    
    # Start admin manager
    manager = AdminManager()
    manager.run()
