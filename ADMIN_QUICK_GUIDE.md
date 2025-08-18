# Complete Admin Management Guide

## 🚀 Quick Start - Adding New Admins

### Method 1: Command Line (Fastest)
```bash
# Add a single admin
python admin_cli.py add "new.admin@thomsonreuters.com"

# List current admins
python admin_cli.py list

# Remove an admin
python admin_cli.py remove "old.admin@thomsonreuters.com"

# Add multiple admins from file
python admin_cli.py bulk-add sample_admins.txt
```

### Method 2: GUI Interface (User-Friendly)
```bash
# Launch the admin management GUI
python admin_manager.py
```

### Method 3: Direct File Edit (Manual)
Edit `AIReview/access_control.json`:
```json
{
  "admin_users": [
    "6126175",
    "harish.sarma",
    "velavalapalli.harishsarma@thomsonreuters.com",
    "NEW_ADMIN_HERE"
  ]
}
```

## 🔧 Available Tools

| Tool | Purpose | Usage |
|------|---------|-------|
| `admin_cli.py` | Command-line management | `python admin_cli.py list` |
| `admin_manager.py` | GUI management interface | `python admin_manager.py` |
| `access_control.json` | Direct configuration file | Edit manually |

## 👥 Admin Types Supported

1. **System Username**: Windows login name (e.g., `"6126175"`)
2. **Network Username**: Active Directory username (e.g., `"harish.sarma"`)
3. **Email Address**: Corporate email (e.g., `"user@thomsonreuters.com"`)
4. **Display Name**: Full name from SSO (e.g., `"John Smith"`)

## 🔒 Security Features

- ✅ **Automatic Backups**: Every change creates a timestamped backup
- ✅ **Multiple Identifiers**: Same person can have multiple admin entries
- ✅ **SSO Integration**: Works with corporate single sign-on
- ✅ **Activity Logging**: All admin activities are tracked
- ✅ **Validation**: Duplicate prevention and error checking

## 📋 Common Scenarios

### Adding a New Team Member
```bash
# Add by email (recommended)
python admin_cli.py add "newmember@thomsonreuters.com"

# Add by system username (backup method)
python admin_cli.py add "newuser123"
```

### Department Migration
```bash
# Create list of new admins
echo "manager@thomsonreuters.com" > new_team.txt
echo "lead@thomsonreuters.com" >> new_team.txt
echo "senior@thomsonreuters.com" >> new_team.txt

# Bulk add
python admin_cli.py bulk-add new_team.txt
```

### Emergency Access
```bash
# Quickly add emergency admin
python admin_cli.py add "emergency.admin@thomsonreuters.com"
```

### Regular Audit
```bash
# Review current admins
python admin_cli.py list

# Remove departing users
python admin_cli.py remove "former.employee@thomsonreuters.com"
```

## 🚨 Best Practices

1. **Use Email Addresses**: Most reliable for corporate environments
2. **Keep System Users**: Backup access method for local authentication
3. **Regular Audits**: Review admin list monthly
4. **Document Changes**: Track who was added/removed and when
5. **Test Access**: Verify new admins can access dev monitor
6. **Backup Configuration**: Keep copies of access_control.json

## 🔧 Troubleshooting

### Admin Can't Access Dev Monitor
1. Check if user is in admin list: `python admin_cli.py list`
2. Verify correct identifier (try email, username, system user)
3. Restart AI Review Tool after changes
4. Check usage logs for authentication attempts

### Configuration File Issues
- **File not found**: Run from AI Review Tool main directory
- **Permission denied**: Check file permissions
- **Backup corrupted**: Use `.backup.*` files to restore

### Authentication Problems
- Try multiple identifiers for same person
- Check SSO vs local authentication
- Verify email format matches SSO

## 📞 Support

For issues with admin management:
1. Check backup files in case of problems
2. Use GUI tool if command line fails
3. Manual file edit as last resort
4. Contact: `velavalapalli.harishsarma@thomsonreuters.com`

## 🔄 Enterprise Integration

For large-scale deployment:
- Consider LDAP/Active Directory integration
- Implement role-based access control
- Use centralized configuration management
- Set up automated admin provisioning

---

*Admin Management Tools Version: 1.0*  
*Compatible with: AI Review Tool v2.1.3+*
