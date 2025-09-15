#!/usr/bin/env python3
"""
Security Scanner for AI Review Tool
Scans for potential token/credential leaks before commits

Usage: python security_scan.py
"""

import os
import re
import sys
from pathlib import Path

# Patterns to detect sensitive information
SENSITIVE_PATTERNS = [
    # API Keys and Tokens
    (r'gh[ps]_[A-Za-z0-9]{36}', 'GitHub Personal Access Token'),
    (r'sk-[A-Za-z0-9]{48}', 'OpenAI API Key'),
    (r'xoxb-[A-Za-z0-9-]+', 'Slack Bot Token'),
    (r'ya29\.[A-Za-z0-9_-]+', 'Google OAuth Token'),
    (r'AKIA[A-Z0-9]{16}', 'AWS Access Key ID'),
    (r'[A-Za-z0-9/+=]{40}', 'Potential AWS Secret Key'),
    
    # Generic patterns
    (r'Bearer\s+[A-Za-z0-9_-]{20,}', 'Bearer Token'),
    (r'(api[_-]?key|secret[_-]?key|access[_-]?token)[\'\"]\s*[:=]\s*[\'\"]\s*[A-Za-z0-9_-]{20,}[\'\"]\s*', 'API Key Assignment'),
    (r'password\s*[:=]\s*[\'\"]\s*[^\s\'\"]{8,}[\'\"]\s*', 'Hardcoded Password'),
    
    # Email addresses (can be sensitive in some contexts)
    (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'Email Address'),
    
    # IP Addresses (can be sensitive)
    (r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', 'IP Address'),
]

# Files to scan (extensions)
SCAN_EXTENSIONS = {'.py', '.js', '.ts', '.json', '.yaml', '.yml', '.env', '.txt', '.md'}

# Directories to skip
SKIP_DIRS = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'build', 'dist'}

def scan_file(file_path):
    """Scan a single file for sensitive patterns"""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        for line_num, line in enumerate(content.split('\n'), 1):
            for pattern, description in SENSITIVE_PATTERNS:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    # Skip obvious false positives
                    if should_skip_match(match.group(), file_path, description):
                        continue
                        
                    issues.append({
                        'file': str(file_path),
                        'line': line_num,
                        'pattern': description,
                        'content': line.strip(),
                        'match': match.group()
                    })
    except Exception as e:
        print(f"[WARNING] Could not scan {file_path}: {e}")
    
    return issues

def should_skip_match(match, file_path, description):
    """Skip obvious false positives"""
    
    # Skip example/placeholder values
    if any(placeholder in match.lower() for placeholder in [
        'example', 'placeholder', 'your_', 'insert_', 'replace_', 'xxx', 'yyy'
    ]):
        return True
    
    # Skip common test/demo patterns
    if any(test_pattern in match.lower() for test_pattern in [
        'test123', 'demo', 'sample', 'fake'
    ]):
        return True
    
    # Skip localhost and private IP ranges for IP addresses
    if description == 'IP Address':
        if match.startswith(('127.', '192.168.', '10.', '172.')):
            # Allow private IPs in certain contexts, but flag corporate IPs
            if not match.startswith(('10.170.', '10.171.', '10.172.')):
                return True
    
    # Skip example email domains
    if description == 'Email Address':
        if any(domain in match.lower() for domain in [
            'example.com', 'test.com', 'domain.com', 'company.com'
        ]):
            return True
    
    return False

def scan_directory(directory):
    """Scan all files in a directory"""
    all_issues = []
    
    for root, dirs, files in os.walk(directory):
        # Skip certain directories
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        
        for file in files:
            file_path = Path(root) / file
            
            # Skip files without relevant extensions
            if file_path.suffix not in SCAN_EXTENSIONS:
                continue
            
            issues = scan_file(file_path)
            all_issues.extend(issues)
    
    return all_issues

def main():
    """Main security scan function"""
    print("[SECURITY SCAN] Starting security scan for sensitive data...")
    
    # Scan current directory
    current_dir = Path('.')
    issues = scan_directory(current_dir)
    
    if not issues:
        print("[SUCCESS] No sensitive data patterns detected!")
        return 0
    
    print(f"\n[WARNING] Found {len(issues)} potential security issues:")
    print("=" * 80)
    
    # Group issues by file
    files_with_issues = {}
    for issue in issues:
        if issue['file'] not in files_with_issues:
            files_with_issues[issue['file']] = []
        files_with_issues[issue['file']].append(issue)
    
    for file_path, file_issues in files_with_issues.items():
        print(f"\n[FILE] {file_path}")
        for issue in file_issues:
            print(f"  Line {issue['line']:4d}: {issue['pattern']}")
            print(f"              Match: {issue['match']}")
            print(f"              Context: {issue['content'][:100]}")
    
    print("\n" + "=" * 80)
    print("[ACTION REQUIRED] Review the above findings and:")
    print("1. Remove or encrypt any real tokens/credentials")
    print("2. Move sensitive config to environment variables")  
    print("3. Add patterns to .gitignore if needed")
    print("4. Consider using a secrets management system")
    
    return 1

if __name__ == "__main__":
    sys.exit(main())
