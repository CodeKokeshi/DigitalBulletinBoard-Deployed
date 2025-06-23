import json
import os
from cryptography.fernet import Fernet
from typing import Dict, Any

class SecureConfig:
    def __init__(self, config_dir: str = "super_secret_stuff"):
        self.config_dir = config_dir
        self.config_file = os.path.join(config_dir, "supersecret.enc")
        self.key_file = os.path.join(config_dir, "config_key.key")
        
        # Create directory if it doesn't exist
        os.makedirs(config_dir, exist_ok=True)
        
        # Initialize encryption
        self.cipher = self._get_or_create_cipher()
        
        # Load or create config
        self._config_data = self._load_or_create_config()
    
    def _get_or_create_cipher(self) -> Fernet:
        """Get existing config encryption key or create a new one"""
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as key_file:
                key = key_file.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as key_file:
                key_file.write(key)
            print(f"🔐 Created new config encryption key: {self.key_file}")
        
        return Fernet(key)
    
    def _encrypt_data(self, data: Dict) -> bytes:
        """Encrypt configuration data"""
        json_data = json.dumps(data, indent=2)
        return self.cipher.encrypt(json_data.encode())
    
    def _decrypt_data(self, encrypted_data: bytes) -> Dict:
        """Decrypt configuration data"""
        decrypted_data = self.cipher.decrypt(encrypted_data)
        return json.loads(decrypted_data.decode())
    
    def _load_or_create_config(self) -> Dict:
        """Load encrypted config or migrate from plain text"""
        # Check if encrypted config exists
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'rb') as file:
                    encrypted_data = file.read()
                    return self._decrypt_data(encrypted_data)
            except Exception as e:
                print(f"❌ Error loading encrypted config: {e}")
                return {}
        
        # Check if plain text config exists (for migration)
        plain_config_file = os.path.join(self.config_dir, "supersecret.json")
        if os.path.exists(plain_config_file):
            print("🔄 Migrating plain text config to encrypted format...")
            try:
                with open(plain_config_file, 'r') as file:
                    data = json.load(file)
                
                # Save as encrypted
                self._save_config(data)
                
                # Backup and remove plain text file
                backup_file = os.path.join(self.config_dir, "supersecret.json.backup")
                os.rename(plain_config_file, backup_file)
                print(f"✅ Config migrated! Plain text backed up to: {backup_file}")
                print("🔥 IMPORTANT: Delete the backup file after confirming everything works!")
                
                return data
            except Exception as e:
                print(f"❌ Error migrating config: {e}")
                return {}
        
        # Create default config if none exists
        print("📝 Creating default encrypted config...")
        default_config = {
            "verification": [
                {
                    "email_sender": "your_email@gmail.com",
                    "password": "your_app_password"
                }
            ],
            "SuperSecret": [
                {
                    "SuperSecretKey": f"user_key_{Fernet.generate_key().decode()[:16]}",
                    "SuperSecretKeyAdmin": f"admin_key_{Fernet.generate_key().decode()[:16]}"
                }
            ],
            "Database_Stuff": [
                {
                    "note": "This section is no longer used - we now use encrypted local database"
                }
            ]
        }
        self._save_config(default_config)
        return default_config
    
    def _save_config(self, data: Dict):
        """Save configuration data in encrypted format"""
        encrypted_data = self._encrypt_data(data)
        with open(self.config_file, 'wb') as file:
            file.write(encrypted_data)
    
    def get(self, section: str, key: str = None, index: int = 0) -> Any:
        """Get configuration value"""
        try:
            if section not in self._config_data:
                return None
            
            section_data = self._config_data[section]
            if isinstance(section_data, list) and len(section_data) > index:
                item = section_data[index]
                if key:
                    return item.get(key)
                return item
            elif isinstance(section_data, dict) and key:
                return section_data.get(key)
            
            return section_data
        except Exception as e:
            print(f"Error getting config value: {e}")
            return None
    
    def set(self, section: str, key: str, value: Any, index: int = 0):
        """Set configuration value"""
        try:
            if section not in self._config_data:
                self._config_data[section] = [{}]
            
            if isinstance(self._config_data[section], list):
                while len(self._config_data[section]) <= index:
                    self._config_data[section].append({})
                self._config_data[section][index][key] = value
            else:
                self._config_data[section][key] = value
            
            self._save_config(self._config_data)
            print(f"✅ Updated config: {section}.{key}")
        except Exception as e:
            print(f"Error setting config value: {e}")
    
    def get_email_config(self) -> Dict:
        """Get email configuration"""
        return {
            "email_sender": self.get("verification", "email_sender"),
            "password": self.get("verification", "password")
        }
    
    def get_secret_keys(self) -> Dict:
        """Get secret keys"""
        return {
            "user_key": self.get("SuperSecret", "SuperSecretKey"),
            "admin_key": self.get("SuperSecret", "SuperSecretKeyAdmin")
        }
    
    def update_email_config(self, email: str, password: str):
        """Update email configuration"""
        self.set("verification", "email_sender", email)
        self.set("verification", "password", password)
    
    def regenerate_secret_keys(self):
        """Generate new secret keys"""
        new_user_key = f"user_key_{Fernet.generate_key().decode()[:16]}"
        new_admin_key = f"admin_key_{Fernet.generate_key().decode()[:16]}"
        
        self.set("SuperSecret", "SuperSecretKey", new_user_key)
        self.set("SuperSecret", "SuperSecretKeyAdmin", new_admin_key)
        
        print("🔑 Generated new secret keys!")
        return {
            "user_key": new_user_key,
            "admin_key": new_admin_key
        }
    
    def export_decrypted(self, output_file: str = None):
        """Export decrypted config for debugging (USE WITH CAUTION!)"""
        if not output_file:
            output_file = os.path.join(self.config_dir, "supersecret_decrypted_TEMP.json")
        
        with open(output_file, 'w') as file:
            json.dump(self._config_data, file, indent=2)
        
        print(f"⚠️  SECURITY WARNING: Decrypted config exported to {output_file}")
        print("🔥 DELETE THIS FILE IMMEDIATELY AFTER USE!")
        return output_file
    
    def backup_encrypted_config(self, backup_dir: str = None):
        """Create a backup of encrypted configuration"""
        if not backup_dir:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = f"config_backup_{timestamp}"
        
        os.makedirs(backup_dir, exist_ok=True)
        
        # Copy encrypted config
        if os.path.exists(self.config_file):
            backup_config = os.path.join(backup_dir, "supersecret.enc")
            with open(self.config_file, 'rb') as src, open(backup_config, 'wb') as dst:
                dst.write(src.read())
        
        # Copy encryption key
        if os.path.exists(self.key_file):
            backup_key = os.path.join(backup_dir, "config_key.key")
            with open(self.key_file, 'rb') as src, open(backup_key, 'wb') as dst:
                dst.write(src.read())
        
        print(f"✅ Encrypted config backed up to: {backup_dir}")
        return backup_dir

# Global instance for easy access
secure_config = SecureConfig()
