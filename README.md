# Netflix Email Confirmation Auto-Clicker

Checks for Netflix "New sign-in" confirmation emails via IMAP and automatically
clicks the "Yes, This Was Me" / "Confirm Update" button using Selenium.

## How it works

1. Connects to an IMAP inbox and searches for UNSEEN emails from `info@account.netflix.com`
2. Extracts the confirmation link from the email body
3. Opens the link in a headless Chrome browser
4. Clicks the confirmation button
5. Logs the result

## Run with GitHub Actions

The workflow in `.github/workflows/script.yaml` runs every 5 minutes and can
also be triggered manually via **Actions > Netflix Email Check > Run workflow**.

### Required secrets

Set these in **Settings > Secrets and variables > Actions**:

| Secret | Value |
|---|---|
| `EMAIL` | IMAP login email |
| `PASSWORD` | IMAP login password |
| `IMAP_SERVER` | e.g. `imap.hostinger.com` |

## Run locally

```bash
pip install selenium beautifulsoup4
python script.py
