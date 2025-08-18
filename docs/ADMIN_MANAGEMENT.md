# Admin Management Guide for AI Review Tool

## Current Admin Configuration

The admin list is stored in `AIReview/access_control.json` under the `admin_users` array.

### Current Admins:
- System User: `6126175`
- Username: `harish.sarma`
- Email: `velavalapalli.harishsarma@thomsonreuters.com`

## Methods to Add New Admins

### Method 1: Direct JSON File Edit
1. Open `AIReview/access_control.json`
2. Add new entries to the `admin_users` array:

```json
{
  "admin_users": [
    "6126175",
    "harish.sarma", 
    "velavalapalli.harishsarma@thomsonreuters.com",
    "new_system_user",
    "new.username",
    "new.admin@thomsonreuters.com"
  ]
}
```

### Method 2: Programmatic Admin Management (Recommended)
Create an admin management interface within the application.

### Method 3: Environment-Based Configuration
Use environment variables for enterprise deployment.

### Method 4: External Configuration File
Use a separate admin configuration that can be updated without touching code.

## Admin Types Supported

1. **System Username**: Windows system user (e.g., "6126175")
2. **Network Username**: Active Directory username (e.g., "harish.sarma")
3. **Email Address**: Corporate email (e.g., "user@thomsonreuters.com")
4. **Display Name**: Full name from SSO (automatically detected)

## Security Considerations

- Admin list changes require file system access
- All admin activities are logged
- Admin detection works across SSO and local authentication
- Multiple admin identifiers per person are supported

## Best Practices

1. **Use Email Addresses**: Most reliable for SSO environments
2. **Keep System Users**: Backup access method
3. **Document Changes**: Track who was added and when
4. **Regular Review**: Audit admin list periodically
5. **Backup Configuration**: Keep copies of access_control.json

## Enterprise Deployment

For large organizations, consider:
- LDAP/Active Directory integration
- Role-based access control
- Automated admin provisioning
- Centralized configuration management
