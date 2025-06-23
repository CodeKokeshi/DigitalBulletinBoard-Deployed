#!/usr/bin/env python3
"""
Secure Configuration Management Tool
This tool helps you manage your encrypted configuration securely.
"""

import os
import getpass
from secure_config import SecureConfig

def main():
    print("🔐 === Secure Configuration Manager ===")
    
    # Initialize secure config
    config = SecureConfig()
    
    while True:
        print("\nOptions:")
        print("1. View current configuration (masked)")
        print("2. Update email configuration")
        print("3. Regenerate secret keys")
        print("4. Create configuration backup")
        print("5. Test email configuration")
        print("6. Security audit")
        print("7. Emergency decrypt (USE WITH CAUTION)")
        print("8. Exit")
        
        choice = input("\nSelect an option (1-8): ").strip()
        
        if choice == "1":
            view_masked_config(config)
        elif choice == "2":
            update_email_config(config)
        elif choice == "3":
            regenerate_keys(config)
        elif choice == "4":
            backup_config(config)
        elif choice == "5":
            test_email_config(config)
        elif choice == "6":
            security_audit(config)
        elif choice == "7":
            emergency_decrypt(config)
        elif choice == "8":
            print("🔒 Configuration secured. Goodbye!")
            break
        else:
            print("❌ Invalid option. Please try again.")

def view_masked_config(config):
    """Display configuration with sensitive data masked"""
    print("\n🔍 === Current Configuration (Masked) ===")
    
    email_config = config.get_email_config()
    secret_keys = config.get_secret_keys()
    
    print(f"📧 Email Sender: {mask_email(email_config.get('email_sender', 'Not set'))}")
    print(f"🔑 Email Password: {'*' * 12 if email_config.get('password') else 'Not set'}")
    print(f"🗝️  User Secret Key: {mask_key(secret_keys.get('user_key', 'Not set'))}")
    print(f"👑 Admin Secret Key: {mask_key(secret_keys.get('admin_key', 'Not set'))}")

def mask_email(email):
    """Mask email address for display"""
    if not email or '@' not in email:
        return email
    
    username, domain = email.split('@', 1)
    if len(username) <= 2:
        masked_username = '*' * len(username)
    else:
        masked_username = username[0] + '*' * (len(username) - 2) + username[-1]
    
    return f"{masked_username}@{domain}"

def mask_key(key):
    """Mask secret key for display"""
    if not key:
        return key
    
    if len(key) <= 8:
        return '*' * len(key)
    
    return key[:4] + '*' * (len(key) - 8) + key[-4:]

def update_email_config(config):
    """Update email configuration"""
    print("\n📧 === Update Email Configuration ===")
    print("ℹ️  Enter your Gmail address and app password")
    print("ℹ️  App passwords: https://support.google.com/accounts/answer/185833")
    
    current_email = config.get("verification", "email_sender")
    if current_email:
        print(f"Current email: {mask_email(current_email)}")
    
    email = input("Enter new email address (or press Enter to keep current): ").strip()
    if not email and current_email:
        email = current_email
    
    if not email:
        print("❌ Email address is required")
        return
    
    print("\n🔑 Enter app password (input will be hidden):")
    password = getpass.getpass("App password: ")
    
    if not password:
        print("❌ Password is required")
        return
    
    # Update configuration
    config.update_email_config(email, password)
    print(f"✅ Email configuration updated for: {mask_email(email)}")

def regenerate_keys(config):
    """Regenerate secret keys"""
    print("\n🔑 === Regenerate Secret Keys ===")
    print("⚠️  WARNING: This will invalidate all existing user sessions!")
    print("⚠️  Users will need to log in again after this change.")
    
    confirm = input("Are you sure you want to regenerate keys? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("❌ Operation cancelled")
        return
    
    new_keys = config.regenerate_secret_keys()
    print("✅ Secret keys regenerated successfully!")
    print("🔄 Restart your application for changes to take effect")

def backup_config(config):
    """Create encrypted configuration backup"""
    print("\n💾 === Create Configuration Backup ===")
    
    backup_dir = config.backup_encrypted_config()
    print("✅ Backup created successfully!")
    print(f"📁 Location: {backup_dir}")
    print("🔐 Backup includes encrypted config and encryption keys")
    print("⚠️  Store backup in a secure location!")

def test_email_config(config):
    """Test email configuration"""
    print("\n📧 === Test Email Configuration ===")
    
    email_config = config.get_email_config()
    if not email_config.get("email_sender") or not email_config.get("password"):
        print("❌ Email configuration not complete")
        return
    
    test_email = input("Enter email address to send test to: ").strip()
    if not test_email:
        print("❌ Test email address is required")
        return
    
    print("📤 Sending test email...")
    
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        msg = MIMEMultipart()
        msg['From'] = email_config["email_sender"]
        msg['To'] = test_email
        msg['Subject'] = "🔐 Secure Config Test Email"
        
        body = """
        This is a test email from your Digital Bulletin Board application.
        
        If you received this email, your email configuration is working correctly!
        
        🔐 Your configuration is now encrypted and secure.
        
        Best regards,
        Digital Bulletin Board System
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(email_config["email_sender"], email_config["password"])
            server.send_message(msg)
        
        print("✅ Test email sent successfully!")
        print(f"📧 Check {test_email} for the test message")
        
    except Exception as e:
        print(f"❌ Failed to send test email: {e}")
        print("💡 Check your email address and app password")

def security_audit(config):
    """Perform security audit"""
    print("\n🛡️  === Security Audit ===")
    
    issues = []
    warnings = []
    
    # Check if plain text backup exists
    plain_backup = os.path.join("super_secret_stuff", "supersecret.json.backup")
    if os.path.exists(plain_backup):
        issues.append("❌ Plain text backup file still exists: supersecret.json.backup")
    
    # Check if original plain text file exists
    plain_original = os.path.join("super_secret_stuff", "supersecret.json")
    if os.path.exists(plain_original):
        issues.append("❌ Original plain text config file still exists: supersecret.json")
    
    # Check file permissions (Windows doesn't have the same permission system)
    config_file = os.path.join("super_secret_stuff", "supersecret.enc")
    key_file = os.path.join("super_secret_stuff", "config_key.key")
    
    if not os.path.exists(config_file):
        issues.append("❌ Encrypted config file not found")
    
    if not os.path.exists(key_file):
        issues.append("❌ Encryption key file not found")
    
    # Check configuration completeness
    email_config = config.get_email_config()
    if not email_config.get("email_sender"):
        warnings.append("⚠️  Email sender not configured")
    
    if not email_config.get("password"):
        warnings.append("⚠️  Email password not configured")
    
    # Display results
    if not issues and not warnings:
        print("✅ Security audit passed! No issues found.")
    else:
        if issues:
            print("🚨 SECURITY ISSUES FOUND:")
            for issue in issues:
                print(f"  {issue}")
        
        if warnings:
            print("\n⚠️  WARNINGS:")
            for warning in warnings:
                print(f"  {warning}")
        
        if issues:
            print("\n🔧 RECOMMENDED ACTIONS:")
            if any("backup" in issue for issue in issues):
                print("  • Delete plain text backup files after confirming encrypted config works")
            if any("original" in issue for issue in issues):
                print("  • Delete original plain text config file")

def emergency_decrypt(config):
    """Emergency decrypt configuration (use with caution)"""
    print("\n🚨 === EMERGENCY DECRYPT ===")
    print("⚠️  WARNING: This will create a temporary unencrypted file!")
    print("⚠️  Only use this for debugging or emergency recovery!")
    print("🔥 DELETE THE OUTPUT FILE IMMEDIATELY AFTER USE!")
    
    confirm1 = input("Are you sure you want to decrypt? (yes/no): ").strip().lower()
    if confirm1 != "yes":
        print("❌ Operation cancelled")
        return
    
    confirm2 = input("Type 'I UNDERSTAND THE RISKS' to continue: ").strip()
    if confirm2 != "I UNDERSTAND THE RISKS":
        print("❌ Operation cancelled")
        return
    
    try:
        output_file = config.export_decrypted()
        print(f"⚠️  Decrypted config exported to: {output_file}")
        print("🔥 REMEMBER TO DELETE THIS FILE IMMEDIATELY!")
        
        # Auto-delete after confirmation
        input("Press Enter after you've finished with the file to auto-delete it...")
        try:
            os.remove(output_file)
            print("✅ Temporary decrypted file deleted")
        except Exception as e:
            print(f"❌ Failed to delete file: {e}")
            print(f"🔥 MANUALLY DELETE: {output_file}")
    
    except Exception as e:
        print(f"❌ Failed to decrypt configuration: {e}")

if __name__ == "__main__":
    main()
