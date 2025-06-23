#!/usr/bin/env python3
"""
Database Management Script for Encrypted Local Database
This script provides utilities to manage your encrypted database.
"""

import os
import json
from encrypted_db import EncryptedDatabase
from datetime import datetime

def main():
    print("=== Encrypted Database Management Tool ===")
    
    # Initialize database
    db = EncryptedDatabase()
    
    while True:
        print("\nOptions:")
        print("1. View all users")
        print("2. Create test user")
        print("3. Delete user")
        print("4. Database statistics")
        print("5. Backup database")
        print("6. View raw encrypted file")
        print("7. Exit")
        
        choice = input("\nSelect an option (1-7): ").strip()
        
        if choice == "1":
            view_all_users(db)
        elif choice == "2":
            create_test_user(db)
        elif choice == "3":
            delete_user(db)
        elif choice == "4":
            show_database_stats(db)
        elif choice == "5":
            backup_database(db)
        elif choice == "6":
            view_raw_file(db)
        elif choice == "7":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")

def view_all_users(db):
    """Display all users in the database"""
    users = db.get_all_users()
    if not users:
        print("No users found in the database.")
        return
    
    print(f"\nFound {len(users)} users:")
    print("-" * 80)
    for user in users:
        print(f"ID: {user['id']}")
        print(f"Name: {user['full_name']}")
        print(f"Age: {user['age']}")
        print(f"Email: {user['email']}")
        print(f"Created: {user['created_at']}")
        print("-" * 80)

def create_test_user(db):
    """Create a test user"""
    print("\nCreating test user...")
    
    name = input("Full name: ").strip()
    if not name:
        name = "Test User"
    
    try:
        age = int(input("Age (default 25): ").strip() or "25")
    except ValueError:
        age = 25
    
    email = input("Email: ").strip()
    if not email:
        email = f"test{datetime.now().timestamp()}@example.com"
    
    password = input("Password (default 'password123'): ").strip()
    if not password:
        password = "password123"
    
    # Hash the password
    from encrypted_db import hash_password
    hashed_password = hash_password(password)
    
    success = db.create_user(name, age, email, hashed_password)
    
    if success:
        print(f"✅ User created successfully!")
        print(f"Email: {email}")
        print(f"Password: {password} (hashed in database)")
    else:
        print("❌ Failed to create user (email might already exist)")

def delete_user(db):
    """Delete a user"""
    email = input("Enter email of user to delete: ").strip()
    if not email:
        print("Email is required.")
        return
    
    # Check if user exists
    user = db.get_user_by_email(email)
    if not user:
        print("User not found.")
        return
    
    print(f"User found: {user['full_name']} ({user['email']})")
    confirm = input("Are you sure you want to delete this user? (yes/no): ").strip().lower()
    
    if confirm == "yes":
        success = db.delete_user(email)
        if success:
            print("✅ User deleted successfully!")
        else:
            print("❌ Failed to delete user.")
    else:
        print("User deletion cancelled.")

def show_database_stats(db):
    """Show database statistics"""
    stats = db.get_database_stats()
    print("\n=== Database Statistics ===")
    for table_name, table_stats in stats.items():
        print(f"{table_name.capitalize()} table:")
        print(f"  - Records: {table_stats['record_count']}")
        print(f"  - Next ID: {table_stats['auto_increment']}")
    
    # Show file sizes
    print("\n=== File Information ===")
    db_dir = "encrypted_data"
    if os.path.exists(db_dir):
        for filename in os.listdir(db_dir):
            if filename.endswith('.enc'):
                filepath = os.path.join(db_dir, filename)
                size = os.path.getsize(filepath)
                print(f"{filename}: {size} bytes")

def backup_database(db):
    """Create a backup of the database"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"database_backup_{timestamp}"
    
    db.backup_database(backup_path)
    print(f"✅ Database backed up to: {backup_path}")

def view_raw_file(db):
    """View the content of encrypted files (decrypted)"""
    print("\nAvailable tables:")
    db_dir = "encrypted_data"
    tables = []
    
    if os.path.exists(db_dir):
        for filename in os.listdir(db_dir):
            if filename.endswith('.enc'):
                table_name = filename[:-4]
                tables.append(table_name)
                print(f"  - {table_name}")
    
    if not tables:
        print("No tables found.")
        return
    
    table_name = input("Enter table name to view: ").strip()
    if table_name not in tables:
        print("Invalid table name.")
        return
    
    try:
        data = db._read_table(table_name)
        print(f"\n=== {table_name.upper()} TABLE CONTENT ===")
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"Error reading table: {e}")

if __name__ == "__main__":
    main()
