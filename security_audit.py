#!/usr/bin/env python3
"""
Security Audit Tool for Digital Bulletin Board
This tool performs a comprehensive security analysis.
"""

import os
import json
import re
from pathlib import Path

def main():
    print("🔍 === SECURITY AUDIT REPORT ===")
    print("Scanning Digital Bulletin Board for security vulnerabilities...\n")
    
    issues = []
    warnings = []
    recommendations = []
    
    # Check file permissions and sensitive data exposure
    check_sensitive_files(issues, warnings)
    
    # Check code for common vulnerabilities
    check_code_security(issues, warnings, recommendations)
    
    # Check configuration security
    check_configuration_security(issues, warnings)
    
    # Check dependencies
    check_dependencies(warnings, recommendations)
    
    # Generate report
    generate_security_report(issues, warnings, recommendations)

def check_sensitive_files(issues, warnings):
    """Check for exposed sensitive files"""
    print("📁 Checking sensitive file exposure...")
    
    sensitive_files = [
        "super_secret_stuff/supersecret.json",
        "super_secret_stuff/supersecret.json.backup",
        ".env",
        "config.ini",
        "database.db"
    ]
    
    for file_path in sensitive_files:
        if os.path.exists(file_path):
            if "supersecret.json" in file_path and not file_path.endswith(".enc"):
                issues.append(f"🚨 CRITICAL: Plain text secrets file found: {file_path}")
            else:
                warnings.append(f"⚠️  Sensitive file detected: {file_path}")
    
    # Check if .gitignore exists and is properly configured
    if not os.path.exists(".gitignore"):
        issues.append("🚨 CRITICAL: No .gitignore file found - secrets may be committed to git")
    else:
        with open(".gitignore", "r") as f:
            gitignore_content = f.read()
            if "super_secret_stuff" not in gitignore_content:
                issues.append("🚨 CRITICAL: .gitignore doesn't exclude super_secret_stuff directory")

def check_code_security(issues, warnings, recommendations):
    """Check code for security vulnerabilities"""
    print("🔍 Scanning code for security vulnerabilities...")
    
    if os.path.exists("main.py"):
        with open("main.py", "r") as f:
            content = f.read()
            
        # Check for hardcoded secrets
        if re.search(r'password\s*=\s*["\'][^"\']+["\']', content, re.IGNORECASE):
            issues.append("🚨 CRITICAL: Potential hardcoded password in main.py")
        
        # Check for SQL injection vulnerabilities (shouldn't be relevant now)
        if "cursor.execute" in content and "%" in content:
            warnings.append("⚠️  Potential SQL injection patterns found (legacy code)")
        
        # Check for proper input validation
        if "Form(...)" in content:
            recommendations.append("💡 Ensure all Form inputs are properly validated")
        
        # Check for CORS configuration
        if "CORSMiddleware" not in content:
            warnings.append("⚠️  No CORS middleware configured - may cause issues in production")
        
        # Check for rate limiting
        if "slowapi" not in content and "rate" not in content.lower():
            recommendations.append("💡 Consider implementing rate limiting for API endpoints")
        
        # Check for HTTPS enforcement
        if "https_only" not in content.lower():
            recommendations.append("💡 Consider enforcing HTTPS in production")

def check_configuration_security(issues, warnings):
    """Check configuration security"""
    print("⚙️  Checking configuration security...")
    
    # Check if encrypted config exists
    encrypted_config = "super_secret_stuff/supersecret.enc"
    if not os.path.exists(encrypted_config):
        issues.append("🚨 CRITICAL: Encrypted configuration file not found")
    
    # Check if encryption keys exist
    config_key = "super_secret_stuff/config_key.key"
    db_key = "super_secret_stuff/db_key.key"
    
    if not os.path.exists(config_key):
        issues.append("🚨 CRITICAL: Configuration encryption key not found")
    
    if not os.path.exists(db_key):
        issues.append("🚨 CRITICAL: Database encryption key not found")
    
    # Check if encrypted database exists
    if not os.path.exists("encrypted_data"):
        warnings.append("⚠️  Encrypted data directory not found")

def check_dependencies(warnings, recommendations):
    """Check dependency security"""
    print("📦 Checking dependencies...")
    
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r") as f:
            deps = f.read()
        
        # Check for known vulnerable packages (basic check)
        if "cryptography" in deps:
            recommendations.append("💡 Ensure cryptography library is up to date")
        
        if "fastapi" in deps:
            recommendations.append("💡 Keep FastAPI updated for latest security patches")
    
    recommendations.append("💡 Run 'pip audit' to check for known vulnerabilities")

def generate_security_report(issues, warnings, recommendations):
    """Generate comprehensive security report"""
    print("\n" + "="*60)
    print("📋 SECURITY AUDIT RESULTS")
    print("="*60)
    
    if issues:
        print("\n🚨 CRITICAL SECURITY ISSUES:")
        for issue in issues:
            print(f"  {issue}")
    
    if warnings:
        print("\n⚠️  SECURITY WARNINGS:")
        for warning in warnings:
            print(f"  {warning}")
    
    if recommendations:
        print("\n💡 SECURITY RECOMMENDATIONS:")
        for rec in recommendations:
            print(f"  {rec}")
    
    if not issues and not warnings:
        print("\n✅ NO CRITICAL SECURITY ISSUES FOUND!")
        print("Your application appears to be well-secured.")
    
    print("\n" + "="*60)
    print("🛡️  DEPLOYMENT SECURITY CHECKLIST")
    print("="*60)
    
    checklist = [
        "🔐 All secrets are encrypted",
        "🚫 No plain text passwords in code",
        "📁 .gitignore properly configured", 
        "🔑 Encryption keys are secure",
        "🌐 HTTPS enabled in production",
        "⚡ Rate limiting implemented",
        "🛡️  Input validation on all endpoints",
        "📊 Logging configured (without secrets)",
        "🔄 Regular security updates scheduled",
        "💾 Secure backup strategy in place"
    ]
    
    for item in checklist:
        print(f"  [ ] {item}")
    
    print("\n🎯 DEPLOYMENT READINESS:")
    if not issues:
        print("  ✅ READY for secure deployment")
    else:
        print("  ❌ FIX CRITICAL ISSUES before deployment")

if __name__ == "__main__":
    main()
