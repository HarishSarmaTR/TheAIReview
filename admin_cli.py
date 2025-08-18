#!/usr/bin/env python3
"""
Command-line admin management tool for AI Review Tool
Quick way to add/remove admins from command line
"""

import json
import os
import sys
import argparse
from datetime import datetime

class AdminCLI:
    def __init__(self):
        self.config_file = "access_control.json"
        if not os.path.exists(self.config_file):
            self.config_file = os.path.join("AIReview", "access_control.json")
        
        if not os.path.exists(self.config_file):
            print(f"❌ Error: {self.config_file} not found!")
            print("Please run this script from the AI Review Tool directory.")
            sys.exit(1)
    
    def load_config(self):
        """Load current configuration"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            sys.exit(1)
    
    def save_config(self, config):
        """Save configuration with backup"""
        try:
            # Create backup
            backup_file = f"{self.config_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with open(backup_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Save new configuration
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"✅ Configuration saved successfully!")
            print(f"📁 Backup created: {backup_file}")
            return True
        except Exception as e:
            print(f"❌ Error saving config: {e}")
            return False
    
    def list_admins(self):
        """List current admin users"""
        config = self.load_config()
        admin_users = config.get("admin_users", [])
        
        print("\n👑 Current Admin Users:")
        print("=" * 50)
        if admin_users:
            for i, admin in enumerate(admin_users, 1):
                print(f"{i:2d}. {admin}")
        else:
            print("No admin users configured.")
        print(f"\nTotal: {len(admin_users)} admin users")
    
    def add_admin(self, admin_identifier):
        """Add a new admin user"""
        config = self.load_config()
        admin_users = config.get("admin_users", [])
        
        if admin_identifier in admin_users:
            print(f"⚠️  Admin already exists: {admin_identifier}")
            return False
        
        admin_users.append(admin_identifier)
        
        if self.save_config(config):
            print(f"✅ Added admin: {admin_identifier}")
            return True
        return False
    
    def remove_admin(self, admin_identifier):
        """Remove an admin user"""
        config = self.load_config()
        admin_users = config.get("admin_users", [])
        
        if admin_identifier not in admin_users:
            print(f"❌ Admin not found: {admin_identifier}")
            return False
        
        admin_users.remove(admin_identifier)
        
        if self.save_config(config):
            print(f"✅ Removed admin: {admin_identifier}")
            return True
        return False
    
    def bulk_add(self, filename):
        """Add multiple admins from a file"""
        try:
            with open(filename, 'r') as f:
                new_admins = [line.strip() for line in f if line.strip()]
            
            config = self.load_config()
            admin_users = config.get("admin_users", [])
            
            added_count = 0
            skipped_count = 0
            
            for admin in new_admins:
                if admin not in admin_users:
                    admin_users.append(admin)
                    print(f"✅ Added: {admin}")
                    added_count += 1
                else:
                    print(f"⚠️  Skipped (already exists): {admin}")
                    skipped_count += 1
            
            if added_count > 0:
                self.save_config(config)
            
            print(f"\n📊 Summary: {added_count} added, {skipped_count} skipped")
            return True
            
        except Exception as e:
            print(f"❌ Error reading file {filename}: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(
        description="AI Review Tool - Admin Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python admin_cli.py list
  python admin_cli.py add "john.doe@company.com"
  python admin_cli.py add "johndoe"
  python admin_cli.py remove "old.admin@company.com"
  python admin_cli.py bulk-add admins.txt

Admin Types Supported:
  • System Username (e.g., "6126175")
  • Network Username (e.g., "harish.sarma")
  • Email Address (e.g., "user@thomsonreuters.com")
  • Display Name (e.g., "John Smith")
""")
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    subparsers.add_parser('list', help='List current admin users')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new admin user')
    add_parser.add_argument('admin', help='Admin identifier (username, email, etc.)')
    
    # Remove command
    remove_parser = subparsers.add_parser('remove', help='Remove an admin user')
    remove_parser.add_argument('admin', help='Admin identifier to remove')
    
    # Bulk add command
    bulk_parser = subparsers.add_parser('bulk-add', help='Add multiple admins from file')
    bulk_parser.add_argument('file', help='Text file with one admin per line')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = AdminCLI()
    
    if args.command == 'list':
        cli.list_admins()
    elif args.command == 'add':
        cli.add_admin(args.admin)
    elif args.command == 'remove':
        cli.remove_admin(args.admin)
    elif args.command == 'bulk-add':
        cli.bulk_add(args.file)

if __name__ == "__main__":
    main()
