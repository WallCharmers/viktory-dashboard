# 🔒 Security Setup Guide

## ⚠️ Important Security Notice

This application uses sensitive credentials that must NEVER be committed to git. All credentials are now loaded from environment variables for security.

## 🛡️ Credential Management

### Backend Environment Variables

1. Copy the template:
```bash
cp backend/.env.example backend/.env
```

2. Edit `backend/.env` with your actual credentials:
```env
# Replace with your actual SP-API credentials
SP_API_CLIENT_ID=amzn1.application-oa2-client.YOUR_ACTUAL_CLIENT_ID
SP_API_CLIENT_SECRET=amzn1.oa2-cs.v1.YOUR_ACTUAL_CLIENT_SECRET  
SP_API_REFRESH_TOKEN=Atzr|YOUR_ACTUAL_REFRESH_TOKEN

# Replace with your actual AWS credentials
AWS_ACCESS_KEY_ID=YOUR_ACTUAL_ACCESS_KEY
AWS_SECRET_ACCESS_KEY=YOUR_ACTUAL_SECRET_KEY
AWS_REGION=us-east-1
AWS_ROLE_ARN=arn:aws:iam::YOUR_ACCOUNT:role/YOUR_ROLE_NAME

# Replace with your actual seller information
SELLER_ID=YOUR_ACTUAL_SELLER_ID
MARKETPLACE_ID=ATVPDKIKX0DER
```

### Streamlit Secrets

1. Edit `.streamlit/secrets.toml` with your password:
```toml
app_password = "your_secure_password_here"
```

## 🚨 Security Checklist

- [ ] ✅ Never commit actual credentials to git
- [ ] ✅ Always use `.env` and `secrets.toml` files (already in `.gitignore`)  
- [ ] ✅ Use strong, unique passwords
- [ ] ✅ Rotate credentials regularly
- [ ] ✅ Use environment variables in production
- [ ] ✅ Never share credentials in chat/email

## 🔄 Credential Rotation

When rotating credentials:

1. Update your environment files
2. Restart the application
3. Test functionality
4. Revoke old credentials

## 📞 Security Issues

If you suspect credential exposure:

1. **Immediately** revoke the exposed credentials
2. Generate new credentials  
3. Update your environment files
4. Contact your security team

## 🛠️ Development Setup

For development, ensure all team members:

1. Have their own `.env` files (never shared)
2. Use placeholder values for testing when possible
3. Never commit real credentials
4. Use secure credential sharing tools for team secrets

Remember: **Security is everyone's responsibility!** 🔐