# 🔐 SECURITY NOTICE

## ⚠️ CRITICAL: Exposed Secrets Detected!

**GitGuardian has detected exposed secrets in this repository's history.**

### 🚨 Immediate Actions Required:

#### 1. **Revoke Exposed Credentials**

- **Telegram Bot Token**: `8567356269:AAH839-_n3--eykejU4TQBQ4eQS8FY_10yE`
  - ✅ Action: Revoke via @BotFather → `/token` → `/revoke`
  - ✅ Create new token
  - ✅ Update `.env` file (NOT committed to git)

- **Gmail SMTP Password**: `etzrmxdkmdpw`
  - ✅ Action: Revoke App Password at https://myaccount.google.com/apppasswords
  - ✅ Create new App Password
  - ✅ Update `.env` file

#### 2. **Clean Git History**

```bash
# Install git-filter-repo
pip install git-filter-repo

# Remove .env from all commits
git filter-repo --path .env --invert-paths --force

# Remove hardcoded secrets
git filter-repo --replace-text <(echo "8567356269:AAH839-_n3--eykejU4TQBQ4eQS8FY_10yE==>***REMOVED***")
git filter-repo --replace-text <(echo "etzrmxdkmdpw==>***REMOVED***")

# Force push (WARNING: This rewrites history!)
git push origin main --force
```

#### 3. **Setup Environment Variables**

```bash
# Copy example file
cp .env.example .env

# Edit with your NEW credentials
nano .env
```

**Required variables:**
- `TELEGRAM_BOT_TOKEN` - Your NEW bot token
- `TELEGRAM_CHAT_ID` - Your chat ID
- `SMTP_USER` - Your email
- `SMTP_PASSWORD` - Your NEW App Password
- `NOTIFY_EMAIL` - Notification recipient

#### 4. **Make Repository Private**

Since this is forked from a public repo and contains sensitive data:

1. Go to: https://github.com/Xtra01/kibris-emlak-101evler-scraper/settings
2. Scroll to **Danger Zone**
3. Click **"Change repository visibility"**
4. Select **"Make private"**

OR

1. Create a new private repository
2. Push your code there
3. Delete the old public fork

#### 5. **Enable Secret Scanning**

Already configured via `.github/workflows/secret-scan.yml`

Monitor at: https://github.com/Xtra01/kibris-emlak-101evler-scraper/security/secret-scanning

---

## 📋 Security Checklist

- [ ] Revoked old Telegram Bot Token
- [ ] Created new Telegram Bot Token
- [ ] Revoked old Gmail App Password
- [ ] Created new Gmail App Password
- [ ] Updated `.env` file with NEW credentials
- [ ] Cleaned Git history (optional but recommended)
- [ ] Made repository private
- [ ] Verified no secrets in codebase: `git grep -E "856735|etzrmxdk"`
- [ ] Tested notifications with new credentials

---

## 🛡️ Best Practices Going Forward

### ✅ DO:
- Store ALL secrets in `.env` (already in `.gitignore`)
- Use environment variables via `python-dotenv`
- Review code before committing: `git diff --cached`
- Use `.env.example` as template

### ❌ DON'T:
- Hardcode secrets in Python files
- Commit `.env` to git
- Share screenshots with visible tokens
- Push to public repos without review

---

## 🔍 How to Check for Secrets

```bash
# Search for common secret patterns
git grep -E "token|password|secret|key" | grep -v ".gitignore"

# Check what's staged for commit
git diff --cached

# Use gitleaks locally
docker run -v ${PWD}:/path zricethezav/gitleaks:latest detect --source="/path" -v
```

---

## 📞 Need Help?

If you've accidentally exposed secrets:

1. **Immediately revoke** the credentials
2. **Change passwords** on affected services
3. **Monitor** for unauthorized access
4. **Contact GitHub Security**: https://github.com/security
5. **Enable 2FA** on all accounts

---

**Last Updated**: November 9, 2025  
**Status**: 🚨 **CRITICAL - ACTION REQUIRED**

