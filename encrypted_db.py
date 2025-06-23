import json
import os
from cryptography.fernet import Fernet
from datetime import datetime
from typing import Dict, List, Any, Optional
import hashlib

class EncryptedDatabase:
    def __init__(self, db_directory: str = "encrypted_data", encryption_key_file: str = "super_secret_stuff/db_key.key"):
        self.db_directory = db_directory
        self.encryption_key_file = encryption_key_file
        
        # Create directories if they don't exist
        os.makedirs(db_directory, exist_ok=True)
        os.makedirs(os.path.dirname(encryption_key_file), exist_ok=True)
        
        # Initialize encryption
        self.cipher = self._get_or_create_cipher()
        
        # Initialize database files
        self._initialize_database()
    
    def _get_or_create_cipher(self) -> Fernet:
        """Get existing encryption key or create a new one"""
        if os.path.exists(self.encryption_key_file):
            with open(self.encryption_key_file, 'rb') as key_file:
                key = key_file.read()
        else:
            key = Fernet.generate_key()
            with open(self.encryption_key_file, 'wb') as key_file:
                key_file.write(key)
        
        return Fernet(key)
    
    def _get_db_file_path(self, table_name: str) -> str:
        """Get the file path for a table"""
        return os.path.join(self.db_directory, f"{table_name}.enc")
    
    def _encrypt_data(self, data: Dict) -> bytes:
        """Encrypt data to bytes"""
        json_data = json.dumps(data, indent=2)
        return self.cipher.encrypt(json_data.encode())
    
    def _decrypt_data(self, encrypted_data: bytes) -> Dict:
        """Decrypt bytes to data"""
        decrypted_data = self.cipher.decrypt(encrypted_data)
        return json.loads(decrypted_data.decode())
    
    def _read_table(self, table_name: str) -> Dict:
        """Read and decrypt a table file"""
        file_path = self._get_db_file_path(table_name)
        if not os.path.exists(file_path):
            return {"records": [], "auto_increment": 1}
        
        with open(file_path, 'rb') as file:
            encrypted_data = file.read()
            return self._decrypt_data(encrypted_data)
    
    def _write_table(self, table_name: str, data: Dict):
        """Encrypt and write a table file"""
        file_path = self._get_db_file_path(table_name)
        encrypted_data = self._encrypt_data(data)
        
        with open(file_path, 'wb') as file:
            file.write(encrypted_data)
    
    def _initialize_database(self):
        """Initialize database tables if they don't exist"""
        # Initialize users table
        users_data = self._read_table("users")
        if not users_data.get("records"):
            users_data = {
                "records": [],
                "auto_increment": 1,
                "schema": {
                    "id": "integer",
                    "full_name": "string",
                    "age": "integer", 
                    "email": "string",
                    "password": "string",
                    "created_at": "datetime"
                }
            }
            self._write_table("users", users_data)
    
    # User management methods
    def create_user(self, full_name: str, age: int, email: str, password: str) -> bool:
        """Create a new user"""
        try:
            users_data = self._read_table("users")
            
            # Check if email already exists
            for user in users_data["records"]:
                if user["email"] == email:
                    return False
            
            # Create new user
            user_id = users_data["auto_increment"]
            new_user = {
                "id": user_id,
                "full_name": full_name,
                "age": age,
                "email": email,
                "password": password,  # Should already be hashed
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            users_data["records"].append(new_user)
            users_data["auto_increment"] += 1
            
            self._write_table("users", users_data)
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        try:
            users_data = self._read_table("users")
            for user in users_data["records"]:
                if user["email"] == email:
                    return user
            return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def update_user_password(self, email: str, new_password: str) -> bool:
        """Update user password"""
        try:
            users_data = self._read_table("users")
            for user in users_data["records"]:
                if user["email"] == email:
                    user["password"] = new_password  # Should already be hashed
                    user["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self._write_table("users", users_data)
                    return True
            return False
        except Exception as e:
            print(f"Error updating password: {e}")
            return False
    
    def get_all_users(self) -> List[Dict]:
        """Get all users"""
        try:
            users_data = self._read_table("users")
            return users_data["records"]
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []
    
    def delete_user(self, email: str) -> bool:
        """Delete user by email"""
        try:
            users_data = self._read_table("users")
            users_data["records"] = [user for user in users_data["records"] if user["email"] != email]
            self._write_table("users", users_data)
            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
    
    # Utility methods
    def backup_database(self, backup_path: str):
        """Create a backup of the entire database"""
        try:
            os.makedirs(backup_path, exist_ok=True)
            
            # Copy all encrypted files
            for filename in os.listdir(self.db_directory):
                if filename.endswith('.enc'):
                    src = os.path.join(self.db_directory, filename)
                    dst = os.path.join(backup_path, filename)
                    with open(src, 'rb') as src_file, open(dst, 'wb') as dst_file:
                        dst_file.write(src_file.read())
            
            # Also backup the encryption key (be careful with this!)
            if os.path.exists(self.encryption_key_file):
                key_backup = os.path.join(backup_path, "db_key.key")
                with open(self.encryption_key_file, 'rb') as src, open(key_backup, 'wb') as dst:
                    dst.write(src.read())
            
            print(f"Database backed up to {backup_path}")
        except Exception as e:
            print(f"Error backing up database: {e}")
    
    def get_database_stats(self) -> Dict:
        """Get statistics about the database"""
        try:
            stats = {}
            for filename in os.listdir(self.db_directory):
                if filename.endswith('.enc'):
                    table_name = filename[:-4]  # Remove .enc extension
                    table_data = self._read_table(table_name)
                    stats[table_name] = {
                        "record_count": len(table_data.get("records", [])),
                        "auto_increment": table_data.get("auto_increment", 1)
                    }
            return stats
        except Exception as e:
            print(f"Error getting database stats: {e}")
            return {}

# Helper functions to maintain compatibility with existing code
def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()
