# Database Migration: MySQL to Encrypted Local Storage

## Overview

This project has been successfully migrated from MySQL to an encrypted local file-based database system. This change provides:

- **No external dependencies**: No need to install MySQL
- **Data encryption**: All user data is encrypted using the Fernet encryption scheme
- **Portability**: Database files travel with your project
- **Security**: Encryption keys are stored separately and securely

## Changes Made

### 1. New Encrypted Database System (`encrypted_db.py`)

- **Encryption**: Uses the `cryptography` library with Fernet symmetric encryption
- **File-based storage**: Data is stored in encrypted `.enc` files in the `encrypted_data/` directory
- **Automatic key management**: Encryption keys are generated and stored securely

### 2. Updated Dependencies (`requirements.txt`)

Removed:
- `mysql-connector-python==8.2.0`

Added:
- `cryptography==41.0.7`

### 3. Modified Main Application (`main.py`)

All MySQL database operations have been replaced with encrypted database operations:

- `cursor.execute()` → `encrypted_db.get_user_by_email()`
- `cursor.fetchone()` → Direct dictionary access
- `database.commit()` → Automatic saving in encrypted format

### 4. Database Management Tool (`db_manager.py`)

A utility script to manage your encrypted database:

```bash
python db_manager.py
```

Features:
- View all users
- Create test users
- Delete users
- Database statistics
- Backup functionality
- View raw encrypted data (decrypted)

## File Structure

```
DigitalBulletinBoard/
├── encrypted_data/           # Encrypted database files
│   ├── users.enc            # Encrypted user data
│   └── ...
├── super_secret_stuff/
│   ├── supersecret.json     # App configuration
│   └── db_key.key          # Database encryption key (NEW)
├── encrypted_db.py          # Encrypted database module (NEW)
├── db_manager.py           # Database management tool (NEW)
├── main.py                 # Updated main application
└── requirements.txt        # Updated dependencies
```

## Security Features

### Data Encryption
- All user data is encrypted using Fernet (symmetric encryption)
- Encryption key is automatically generated and stored securely
- Each database table is stored as a separate encrypted file

### Key Management
- Encryption key is stored in `super_secret_stuff/db_key.key`
- **IMPORTANT**: Keep this key file secure and backed up
- Without this key, encrypted data cannot be recovered

## Usage

### Starting the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

The application will automatically:
1. Create the `encrypted_data/` directory
2. Generate an encryption key if it doesn't exist
3. Initialize the user database

### Managing the Database

Use the database management tool:

```bash
python db_manager.py
```

### Creating Your First User

You can create users through:
1. The web application signup process
2. The database management tool (`db_manager.py`)

## Migration Benefits

1. **No MySQL Installation Required**: The application now works out of the box
2. **Enhanced Security**: All data is encrypted at rest
3. **Simplified Deployment**: No database server setup required
4. **Backup Friendly**: Simply copy the `encrypted_data/` folder and key file
5. **Development Friendly**: Easy to reset/clear data during development

## Backup and Recovery

### Creating Backups

```bash
# Using the management tool
python db_manager.py
# Select option 5 (Backup database)

# Manual backup
cp -r encrypted_data/ backup_folder/
cp super_secret_stuff/db_key.key backup_folder/
```

### Restoring from Backup

```bash
# Restore encrypted data files
cp -r backup_folder/encrypted_data/ ./

# Restore encryption key
cp backup_folder/db_key.key super_secret_stuff/
```

## Security Considerations

1. **Protect the Encryption Key**: The file `super_secret_stuff/db_key.key` must be kept secure
2. **Regular Backups**: Back up both the data files and the encryption key
3. **Access Control**: Ensure the application directory has appropriate file permissions
4. **Key Rotation**: Consider periodically regenerating encryption keys for enhanced security

## API Compatibility

The application's API endpoints remain unchanged. All existing frontend code will continue to work without modifications.

## Troubleshooting

### Common Issues

1. **"No module named 'cryptography'"**
   - Run: `pip install -r requirements.txt`

2. **"Permission denied" errors**
   - Ensure the application has write permissions to create the `encrypted_data/` directory

3. **"Failed to create user account"**
   - Check if the user already exists
   - Use `db_manager.py` to view existing users

### Debug Information

The encrypted database system includes detailed error logging. Check the console output for debugging information.

## Performance Notes

- The encrypted database is designed for small to medium-scale applications
- For high-traffic applications, consider implementing caching mechanisms
- Database operations are performed in-memory and then written to disk

## Future Enhancements

Potential improvements for the encrypted database system:

1. **Indexing**: Add support for indexed searches
2. **Compression**: Compress data before encryption
3. **Sharding**: Split large tables across multiple files
4. **Audit Logging**: Track all database operations
5. **Automated Backups**: Schedule regular backups
