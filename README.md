# Knack RCM Report — Streamlit App

Microsoft SSO + SharePoint headcount report generator.

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Azure App Registration

Go to [portal.azure.com](https://portal.azure.com) and:

1. **Azure Active Directory → App registrations → New registration**
   - Name: `Knack RCM Report`
   - Supported account types: *Accounts in this organizational directory only*
   - Redirect URI: `Web` → `http://localhost:8501/`

2. **Certificates & secrets → New client secret**
   - Copy the **Value** (not the ID) — you only see it once

3. **API permissions → Add a permission:**
   | API | Permission | Type |
   |-----|-----------|------|
   | Microsoft Graph | `User.Read` | Delegated |
   | SharePoint | `AllSites.Read` | Delegated |

4. Click **Grant admin consent**

5. Copy from Overview:
   - **Application (client) ID**
   - **Directory (tenant) ID**

---

### 3. Set up secrets

```bash
mkdir -p .streamlit
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
# Edit .streamlit/secrets.toml with your values
```

`.streamlit/secrets.toml`:
```toml
AZURE_CLIENT_ID     = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
AZURE_TENANT_ID     = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
AZURE_CLIENT_SECRET = "your~secret~value"
REDIRECT_URI        = "http://localhost:8501/"
```

---

### 4. Run the app
```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) and click **Sign in with Microsoft**.

---

## Deploying to Streamlit Community Cloud

1. Push your repo to GitHub (**without** `.streamlit/secrets.toml` — add it to `.gitignore`)
2. Go to [share.streamlit.io](https://share.streamlit.io) → deploy from GitHub
3. In **Advanced settings → Secrets**, paste the contents of `secrets.toml`
4. Update `REDIRECT_URI` to your Streamlit Cloud URL (e.g. `https://your-app.streamlit.app/`)
5. Add that URL to Azure App Registration → Redirect URIs

---

## SharePoint Folder Structure Expected

```
Shared Documents/
├── Headcount/
│   └── App/
│       ├── GPP.xlsx
│       ├── GPP - Old.xlsx
│       ├── Staff*.xlsx          (starts with "Staff")
│       ├── Clark Staffing*.xlsx (contains "Clark Staffing")
│       └── Clark/
│           └── exported.xlsx
└── EWS/
    └── *.xlsx                   (all files)
```

---

## Output Sheets

| Sheet | Source | Description |
|-------|--------|-------------|
| GPP | GPP.xlsx + GPP - Old.xlsx | Combined active/inactive, deduped by Global ID |
| Clark | Clark Staffing files + exported.xlsx | Final Clark with project/status rules |
| Staff | Staff*.xlsx | Cleaned headcount with role/location transforms |
| EWS | EWS folder | Early Warning System entries |
| Sprout | exported.xlsx (Clark subfolder) | Managers Clark for Sprout tab |

---

## Notes

- **No passwords stored** — authentication is entirely via Microsoft OAuth 2.0
- The app token is scoped to `User.Read` + SharePoint read access only
- Session expires when the browser tab closes (no persistent storage)
