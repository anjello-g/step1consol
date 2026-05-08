"""
Knack RCM Report — Streamlit App
Microsoft SSO login via MSAL + SharePoint data source
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import re
import warnings
import traceback
import io
import time
from datetime import datetime

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Knack RCM Report",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* ── Background ─────────────────────────────── */
.stApp {
    background: linear-gradient(135deg, #0f1117 0%, #1a1f2e 50%, #0f1117 100%);
    min-height: 100vh;
}

/* ── Sidebar ─────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #141822 0%, #0f1117 100%);
    border-right: 1px solid rgba(99, 179, 237, 0.15);
}

/* ── Cards ───────────────────────────────────── */
.knack-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(99, 179, 237, 0.12);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
    backdrop-filter: blur(10px);
}

.knack-card-accent {
    background: linear-gradient(135deg, rgba(99,179,237,0.08) 0%, rgba(154,117,234,0.05) 100%);
    border: 1px solid rgba(99, 179, 237, 0.2);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
}

/* ── Login box ───────────────────────────────── */
.login-container {
    max-width: 480px;
    margin: 80px auto;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(99, 179, 237, 0.18);
    border-radius: 24px;
    padding: 48px 40px;
    text-align: center;
    backdrop-filter: blur(20px);
    box-shadow: 0 32px 64px rgba(0,0,0,0.4), 0 0 0 1px rgba(255,255,255,0.05);
}

.login-logo {
    width: 72px;
    height: 72px;
    background: linear-gradient(135deg, #63b3ed, #9a75ea);
    border-radius: 20px;
    margin: 0 auto 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 32px;
    box-shadow: 0 8px 32px rgba(99,179,237,0.3);
}

/* ── Hero title ──────────────────────────────── */
.hero-title {
    font-size: 2.4rem;
    font-weight: 700;
    background: linear-gradient(135deg, #63b3ed 0%, #9a75ea 60%, #f093fb 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.03em;
    line-height: 1.1;
    margin-bottom: 6px;
}

.hero-sub {
    color: rgba(255,255,255,0.45);
    font-size: 0.95rem;
    font-weight: 400;
    letter-spacing: 0.01em;
}

/* ── Stat pills ──────────────────────────────── */
.stat-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(99,179,237,0.1);
    border: 1px solid rgba(99,179,237,0.2);
    border-radius: 100px;
    padding: 6px 14px;
    font-size: 0.82rem;
    font-weight: 500;
    color: #63b3ed;
    font-family: 'DM Mono', monospace;
}

.stat-pill.green {
    background: rgba(72,187,120,0.1);
    border-color: rgba(72,187,120,0.25);
    color: #48bb78;
}

.stat-pill.purple {
    background: rgba(154,117,234,0.1);
    border-color: rgba(154,117,234,0.25);
    color: #9a75ea;
}

.stat-pill.red {
    background: rgba(245,101,101,0.1);
    border-color: rgba(245,101,101,0.25);
    color: #f56565;
}

/* ── Log console ─────────────────────────────── */
.log-console {
    background: #0a0c10;
    border: 1px solid rgba(99,179,237,0.15);
    border-radius: 12px;
    padding: 16px 20px;
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    color: #a0aec0;
    max-height: 280px;
    overflow-y: auto;
    line-height: 1.7;
}

.log-ok   { color: #48bb78; }
.log-warn { color: #f6ad55; }
.log-err  { color: #f56565; }
.log-info { color: #63b3ed; }

/* ── Buttons ─────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #63b3ed 0%, #9a75ea 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    padding: 10px 24px !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 16px rgba(99,179,237,0.25) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(99,179,237,0.4) !important;
}

/* ── Download button ─────────────────────────── */
.stDownloadButton > button {
    background: linear-gradient(135deg, #48bb78 0%, #38a169 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    width: 100% !important;
    padding: 14px !important;
    font-size: 1rem !important;
    box-shadow: 0 4px 16px rgba(72,187,120,0.3) !important;
}

/* ── Tab strip ───────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03);
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
    border: 1px solid rgba(99,179,237,0.1);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    color: rgba(255,255,255,0.5);
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background: rgba(99,179,237,0.15) !important;
    color: #63b3ed !important;
}

/* ── Progress bar ────────────────────────────── */
.stProgress > div > div { background-color: #63b3ed !important; }

/* ── Inputs ──────────────────────────────────── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(99,179,237,0.2) !important;
    border-radius: 10px !important;
    color: white !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput > label, .stTextArea > label {
    color: rgba(255,255,255,0.6) !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Dataframe ───────────────────────────────── */
.stDataFrame { border-radius: 12px; overflow: hidden; }

/* ── Divider ─────────────────────────────────── */
hr { border-color: rgba(99,179,237,0.1) !important; }

/* ── Expander ────────────────────────────────── */
.streamlit-expanderHeader {
    background: rgba(255,255,255,0.03) !important;
    border-radius: 10px !important;
    color: rgba(255,255,255,0.7) !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Section labels ──────────────────────────── */
.section-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.3);
    margin-bottom: 10px;
}

.badge {
    display: inline-block;
    background: rgba(72,187,120,0.15);
    color: #48bb78;
    border: 1px solid rgba(72,187,120,0.3);
    border-radius: 6px;
    padding: 2px 10px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.05em;
}

.badge-blue {
    background: rgba(99,179,237,0.15);
    color: #63b3ed;
    border-color: rgba(99,179,237,0.3);
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# MSAL Authentication
# ══════════════════════════════════════════════════════════════
def get_msal_app():
    try:
        import msal
        CLIENT_ID     = st.secrets.get("AZURE_CLIENT_ID", os.environ.get("AZURE_CLIENT_ID", ""))
        TENANT_ID     = st.secrets.get("AZURE_TENANT_ID", os.environ.get("AZURE_TENANT_ID", ""))
        CLIENT_SECRET = st.secrets.get("AZURE_CLIENT_SECRET", os.environ.get("AZURE_CLIENT_SECRET", ""))
        REDIRECT_URI  = st.secrets.get("REDIRECT_URI", os.environ.get("REDIRECT_URI", "http://localhost:8501"))

        authority = f"https://login.microsoftonline.com/{TENANT_ID}"
        app = msal.ConfidentialClientApplication(
            CLIENT_ID,
            authority=authority,
            client_credential=CLIENT_SECRET,
        )
        return app, REDIRECT_URI, CLIENT_ID, TENANT_ID
    except Exception as e:
        st.error(f"MSAL init failed: {e}")
        return None, None, None, None


def get_auth_url():
    app, redirect_uri, _, _ = get_msal_app()
    if not app:
        return None
    scopes = [
        "https://graph.microsoft.com/User.Read",
        "https://knackglobal.sharepoint.com/.default",
    ]
    url = app.get_authorization_request_url(
        scopes=scopes,
        redirect_uri=redirect_uri,
        state="knack_rcm_state",
    )
    return url


def exchange_code_for_token(code: str):
    app, redirect_uri, _, _ = get_msal_app()
    if not app:
        return None
    scopes = [
        "https://graph.microsoft.com/User.Read",
        "https://knackglobal.sharepoint.com/.default",
    ]
    result = app.acquire_token_by_authorization_code(
        code=code,
        scopes=scopes,
        redirect_uri=redirect_uri,
    )
    return result


def get_user_info(access_token: str) -> dict:
    import requests
    headers = {"Authorization": f"Bearer {access_token}"}
    r = requests.get("https://graph.microsoft.com/v1.0/me", headers=headers)
    if r.status_code == 200:
        return r.json()
    return {}


# ══════════════════════════════════════════════════════════════
# SharePoint DataSource (token-based, no username/password)
# ══════════════════════════════════════════════════════════════
SITE_URL = "https://knackglobal.sharepoint.com/sites/KnackRCMReportPH"

SP_APP_FOLDER  = "/sites/KnackRCMReportPH/Shared Documents/Headcount/App"
SP_CLARK_FOLDER = "/sites/KnackRCMReportPH/Shared Documents/Headcount/App/Clark"
SP_EWS_FOLDER  = "/sites/KnackRCMReportPH/Shared Documents/Headcount/EWS"


class SharePointDataSource:
    def __init__(self, access_token: str, log_fn=None):
        self.access_token = access_token
        self.ctx = None
        self.log = log_fn or (lambda msg, level="info": None)
        self._connect()

    def _connect(self):
        try:
            from office365.sharepoint.client_context import ClientContext
            from office365.runtime.auth.token_response import TokenResponse

            def _token_provider():
                return TokenResponse.from_dict({"access_token": self.access_token})

            self.ctx = ClientContext(SITE_URL).with_access_token(_token_provider)
            web = self.ctx.web
            self.ctx.load(web)
            self.ctx.execute_query()
            self.log(f"Connected to SharePoint: {web.title}", "ok")
        except Exception as e:
            raise RuntimeError(f"SharePoint connection failed: {e}") from e

    def find_files(self, folder_url, name_contains=None, name_exact=None, starts_with=None):
        try:
            folder = self.ctx.web.get_folder_by_server_relative_url(folder_url)
            files  = folder.files
            self.ctx.load(files)
            self.ctx.execute_query()
            matches = []
            for f in files:
                name = f.properties.get("Name", "")
                if name_exact and name == name_exact:
                    matches.append(f.serverRelativeUrl)
                elif name_contains and name_contains in name:
                    matches.append(f.serverRelativeUrl)
                elif starts_with and name.startswith(starts_with):
                    matches.append(f.serverRelativeUrl)
                elif not any([name_exact, name_contains, starts_with]):
                    matches.append(f.serverRelativeUrl)
            return matches
        except Exception as e:
            raise RuntimeError(f"SharePoint folder read failed ({folder_url}): {e}") from e

    def _sp_bytes(self, file_ref):
        from office365.sharepoint.files.file import File
        response = File.open_binary(self.ctx, file_ref)
        return io.BytesIO(response.content)

    def read_excel_all_sheets(self, file_ref):
        bio    = self._sp_bytes(file_ref)
        xl     = pd.ExcelFile(bio)
        names  = xl.sheet_names
        bio.seek(0)
        frames = [pd.read_excel(bio, sheet_name=s, header=0) for s in names]
        frames = [f for f in frames if not f.empty]
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    def read_excel_first_sheet(self, file_ref):
        bio = self._sp_bytes(file_ref)
        return pd.read_excel(bio, sheet_name=0, header=0)


# ══════════════════════════════════════════════════════════════
# All helper / query functions (SharePoint-only version)
# ══════════════════════════════════════════════════════════════

def safe_drop(df, cols):
    existing = [c for c in cols if c in df.columns]
    return df.drop(columns=existing) if existing else df

def to_proper(val):
    if pd.isna(val):
        return val
    return str(val).title()

def safe_str_lower(series):
    return series.where(series.isna(), series.astype(str).str.lower())

def reorder_columns(df, desired_order):
    existing  = [c for c in desired_order if c in df.columns]
    remaining = [c for c in df.columns if c not in desired_order]
    return df[existing + remaining]

def ensure_columns(df, cols, default=np.nan):
    for c in cols:
        if c not in df.columns:
            df[c] = default
    return df

def clean_region_role(val):
    if pd.isna(val):
        return val
    s = str(val)
    s = re.sub(r'^\s*-\s*', '', s)
    s = re.sub(r'\s*-\s*$', '', s)
    return s.strip()


GPP_ORDER = [
    "Global ID","First Name","Last Name","Adapt Email","Region - Role",
    "HR Title","Job Code","Start Date","Leave Start Date","Leave End Date",
    "Termination Date","Termination Reason","Remote Partner","Status",
    "Remote Partner Location","Remote Team Lead","Is Agent Team Lead",
    "Buffer Resource","Domestic Manager 1","Domestic Manager 2",
    "DomesticManager1Email","DomesticManager2Email","Business Vertical","ECN Lookup"
]
CLARK_ORDER = [
    "ECN","Employee","Project","Sub-Process","Supervisor","Role",
    "Assitant Manager","Manager","Sr Manager","Director","DOJ Knack",
    "DOJ Project","Aging Knack","Aging Project","Date of Separation",
    "Shift Timing","Email","NT Login","Structure","Billable/Buffer",
    "Process Owner","Department","Aging Bucket","Start of the Month",
    "End of the Month","Equivalent Band-Level","Location","Hired For",
    "Allocated Seats","Gender","Seat Number","Global ID (GPP)",
    "Invoice Status","Days","Month","WorkWeek","Validation","Checker",
    "Validate","Source.Name","Sr No","Date","Year","Attrition Type",
    "Reason for Attrition","Column98","Active/Inactive"
]
STAFF_ORDER = [
    "ECN","Employee","Email","DOJ Knack","Date of Separation",
    "Reason for Attrition","Active/Inactive","Role","Gender","Location",
    "Supervisor","CDP Email","BufferAgent","Entitled Paid Leave",
    "Accrued Paid Leave","Carried Over Paid Leave","Available Paid Leave",
    "Total Used Paid Leave","Last Accrual Date","Column86","Adapt Email"
]
STAFF_EXTRA_COLS = [
    "BufferAgent","Entitled Paid Leave","Accrued Paid Leave",
    "Carried Over Paid Leave","Available Paid Leave","Total Used Paid Leave",
    "Last Accrual Date","Column86"
]
EWS_ORDER = [
    "Date Submitted","Employee ID","Employee Name","EWS Type","Driver",
    "Details","Expected Move Date","Location","Submitted By","Email",
    "Active/Inactive","Status"
]
EWS_EXTRA_COLS = ["Active/Inactive","Status"]
SPROUT_ORDER = ["ECN","Employee","Role","RSupervisor","Manager Name","DOJ Knack","Separation Date"]
SPROUT_EXTRA_COLS = ["Role","RSupervisor","Separation Date"]


def _cast_gpp_types(df, include_role, strict_leave_dates=False):
    for c in ["Start Date","Termination Date"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")
    for c in ["Leave Start Date","Leave End Date"]:
        if c in df.columns and strict_leave_dates:
            df[c] = pd.to_datetime(df[c], errors="coerce")
    text_cols = [
        "Global ID","First Name","Last Name","Email","HR Title",
        "Termination Reason","Remote Partner","Status","Region",
        "Remote Partner Location","Remote Team Lead",
        "Domestic Manager 1","Domestic Manager 2",
        "DomesticManager1Email","DomesticManager2Email"
    ]
    if include_role:
        text_cols.append("Role")
    for c in text_cols:
        if c in df.columns:
            df[c] = df[c].where(df[c].isna(), df[c].astype(str))
            df[c] = df[c].replace({"nan": np.nan,"None": np.nan,"NaT": np.nan})
    for c in ["Job Code","Is Agent Team Lead","Buffer Resource"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")
    return df


def query_gpp_active(ds):
    files = ds.find_files(SP_APP_FOLDER, name_exact="GPP.xlsx")
    if not files:
        raise FileNotFoundError("GPP.xlsx not found")
    df = ds.read_excel_all_sheets(files[0])
    df = _cast_gpp_types(df, include_role=False)
    if "Termination Date" in df.columns:
        df = df[df["Termination Date"].isna()].copy()
    return df

def query_gpp_inactive_new(ds):
    files = ds.find_files(SP_APP_FOLDER, name_exact="GPP.xlsx")
    if not files:
        raise FileNotFoundError("GPP.xlsx not found")
    df = ds.read_excel_all_sheets(files[0])
    df = _cast_gpp_types(df, include_role=False)
    return df

def query_gpp_inactive_old(ds):
    files = ds.find_files(SP_APP_FOLDER, name_exact="GPP - Old.xlsx")
    if not files:
        raise FileNotFoundError("GPP - Old.xlsx not found")
    df = ds.read_excel_all_sheets(files[0])
    df = _cast_gpp_types(df, include_role=True, strict_leave_dates=True)
    if "Termination Date" in df.columns:
        df = df[df["Termination Date"].notna()].copy()
    return df

def query_gpp(gpp_active, gpp_inactive_new, gpp_inactive_old):
    df = pd.concat([gpp_active, gpp_inactive_new, gpp_inactive_old], ignore_index=True)
    df = df.drop_duplicates(subset=["Global ID"], keep="first")
    if "Email" in df.columns:
        df["Email"] = safe_str_lower(df["Email"])
    df["Start Date"] = pd.to_datetime(df["Start Date"], errors="coerce")
    df = df.sort_values("Start Date", ascending=False).reset_index(drop=True)
    df = df.rename(columns={"Email": "Adapt Email"})
    region = df["Region"].fillna("").astype(str).str.strip() if "Region" in df.columns else pd.Series("", index=df.index)
    role   = df["Role"].fillna("").astype(str).str.strip()   if "Role"   in df.columns else pd.Series("", index=df.index)
    df["Region - Role"] = (region + " - " + role).apply(clean_region_role)
    df = safe_drop(df, ["Region","Role"])
    if "Global ID" in df.columns:
        df = df[~df["Global ID"].astype(str).str.contains("AH91006455", na=False)].copy()
    df["Business Vertical"] = np.nan
    df["ECN Lookup"]        = np.nan
    df = reorder_columns(df, GPP_ORDER)
    return df

def _cast_clark_types(df):
    for c in ["Date","DOJ Knack","DOJ Project","Date of Separation"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")
    for c in ["Sr No","ECN","Aging Knack","Aging Project","Start of the Month","End of the Month","Year"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")
    text_cols = [
        "Employee","Project","Sub-Process","Supervisor","Role","Manager","Sr Manager","Director",
        "Tagging","Shift Timing","Email","NT Login","Structure","Billable/Buffer","Process Owner",
        "Department","Aging Bucket","Days","Month","WorkWeek","Active/Inactive","Attrition Type",
        "Reason for Attrition","Equivalent Band-Level","Location","Hired For","Allocated Seats",
        "Gender","Seat Number","Global ID (GPP)","Validation","Source.Name"
    ]
    for c in text_cols:
        if c in df.columns:
            df[c] = df[c].where(df[c].isna(), df[c].astype(str))
            df[c] = df[c].replace({"nan": np.nan,"None": np.nan,"NaT": np.nan})
    if "Running Attrition %" in df.columns:
        df["Running Attrition %"] = pd.to_numeric(df["Running Attrition %"], errors="coerce")
    return df

def query_clark_active(ds):
    files = ds.find_files(SP_APP_FOLDER, name_contains="Clark Staffing")
    if not files:
        raise FileNotFoundError("No 'Clark Staffing' files found")
    frames = [ds.read_excel_all_sheets(f) for f in files]
    df = pd.concat(frames, ignore_index=True)
    df = _cast_clark_types(df)
    if "Date" in df.columns and df["Date"].notna().any():
        df = df[df["Date"] == df["Date"].max()].copy()
    df = safe_drop(df, ["Sr No","Date"])
    return df

def query_clark_inactive(ds):
    files = ds.find_files(SP_APP_FOLDER, name_contains="Clark Staffing")
    if not files:
        raise FileNotFoundError("No 'Clark Staffing' files found")
    frames = [ds.read_excel_all_sheets(f) for f in files]
    df = pd.concat(frames, ignore_index=True)
    df = _cast_clark_types(df)
    cols_to_remove = (
        [f"Column{i}" for i in range(34, 66)]
        + ["Running Attrition %"]
        + [f"Column{i}" for i in range(67, 98)]
    )
    df = safe_drop(df, cols_to_remove)
    return df

def query_staff(ds):
    files = ds.find_files(SP_APP_FOLDER, starts_with="Staff")
    if not files:
        raise FileNotFoundError("No 'Staff*' file found")
    df = ds.read_excel_first_sheet(files[0])
    remove_cols = [
        "HasProfileImage","DateOfBirth","AddressLine1","AddressLine2","AddressLine3",
        "Country","Postal","ContractDate","PrimaryContactNumber","SecondaryContactNumber",
        "City","State","Name","HiredDate","CivilStatus","WorkSetup",
        "HBOSEmail","PersonalEmail","TLMSUserName","VeemAccountName","VeemAccountEmail",
        "UnionBankAccount","ComputerName","PrimaryISP","SecondaryISP","PayRate","Currency",
        "PayAmount","Rice Allowance","Medical Allowance","Meal Allowance",
        "Transportation Allowance","Clothing Allowance","Laundry Allowance",
        "Internet Stipend","Equipment Fee","NBI","Contract","BAA Agreement","W8-Ben",
        "Background Check Waiver","HBOS NDA",
        "HBOS Information Security Policies and Procedures Manual",
        "HBOS Addendum to Employee And Contractor Handbook",
        "HBOS Addendum to Employee And Contractor Handbook Amendment Assigned",
        "Agreement to Return and Care for Company Equipment",
        "Company Equipment Serial and Model Information",
        "PIP Disciplinary","Referral Type","Referral","BackgroundCheckStatus",
        "TotalWorkExperience","SSS","PhilHealth","Tax Identification Number",
        "Pag Ibig #","EmploymentType","HasITR","ClientName","Campaign",
        "WorkExperience (Prior join date)","MiddleName","BiometricID","LocationName"
    ]
    df = safe_drop(df, remove_cols)
    if "EmployeeNumber" in df.columns:
        df = df.drop_duplicates(subset=["EmployeeNumber"], keep="first")
    for col in ["LastName","FirstName","ManagerName"]:
        if col in df.columns:
            df[col] = df[col].apply(to_proper)
    for col in ["Email","CSLoginName","PureCloudLoginName"]:
        if col in df.columns:
            df[col] = safe_str_lower(df[col])
    last  = df["LastName"].fillna("").astype(str).str.strip()  if "LastName"  in df.columns else pd.Series("", index=df.index)
    first = df["FirstName"].fillna("").astype(str).str.strip() if "FirstName" in df.columns else pd.Series("", index=df.index)
    df["Employee"] = (last + ", " + first).str.strip(", ")
    if "TenureDate" in df.columns:
        splits = df["TenureDate"].astype(str).str.split(" ", n=2, expand=True)
        df["DOJ Knack"] = splits[0].replace({"nan": np.nan,"None": np.nan,"NaT": np.nan})
        df = safe_drop(df, ["TenureDate"])
    rename_map = {
        "EmployeeNumber":       "ECN",
        "DischargedDate":       "Date of Separation",
        "DischargedReason":     "Reason for Attrition",
        "HireStatus":           "Active/Inactive",
        "Position":             "Role",
        "CSLoginName":          "CDP Email",
        "PureCloudLoginName":   "Adapt Email",
        "On Site Location":     "Location",
        "ManagerName":          "Supervisor",
        "LastName":             "_LastName_drop",
        "FirstName":            "_FirstName_drop",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
    df = safe_drop(df, ["_LastName_drop","_FirstName_drop"])
    if "Active/Inactive" in df.columns:
        df["Active/Inactive"] = (
            df["Active/Inactive"].astype(str).str.strip()
            .replace({"Discharged": "Inactive","Production": "Active"})
        )
    if "Gender" in df.columns:
        df["Gender"] = df["Gender"].replace({"NoneSpecified": np.nan})
    if "Location" in df.columns:
        df["Location"] = df["Location"].fillna("WFH")

    # ECN 2310158 override: Corporate -> WFH
    if "Location" in df.columns and "ECN" in df.columns:
        mask = (
            df["ECN"].astype(str).str.strip() == "2310158"
        ) & (
            df["Location"].astype(str).str.strip().str.lower() == "corporate"
        )
        df.loc[mask, "Location"] = "WFH"

    if "Role" in df.columns:
        r = df["Role"].astype(str)
        for fragment in ["Salary","Days","Hourly","Onsite"]:
            r = r.str.replace(fragment, "", regex=False)
        r = r.where(r.str.upper().str.strip() != "SUPERVISOR", "Team Leader")
        r = r.str.replace("Lead Agent", "SME", regex=False)
        r = r.str.replace("Agent", "Process Associate", regex=False)
        df["Role"] = r.str.strip().str.title()
    sep_col  = pd.to_datetime(df["Date of Separation"] if "Date of Separation" in df.columns else pd.Series(dtype="object"), errors="coerce")
    is_active = df["Active/Inactive"].astype(str).str.upper().str.strip() == "ACTIVE" if "Active/Inactive" in df.columns else pd.Series(False, index=df.index)
    df["Date of Separation Final"] = np.where(is_active, pd.NaT, sep_col)
    df["Date of Separation Final"] = pd.to_datetime(df["Date of Separation Final"], errors="coerce")
    pq_order = ["ECN","Employee","Email","DOJ Knack","Date of Separation Final","Reason for Attrition","Active/Inactive","Role","Gender","Location","Supervisor","CDP Email","Adapt Email"]
    df = reorder_columns(df, pq_order)
    df = safe_drop(df, ["Date of Separation"])
    df = df.rename(columns={"Date of Separation Final": "Date of Separation"})
    if "Adapt Email" in df.columns:
        df["Adapt Email"] = np.where(df["Adapt Email"].astype(str).str.contains("@adapthealth.com", na=False), df["Adapt Email"], np.nan)
    if "ECN" in df.columns:
        df["ECN"] = pd.to_numeric(df["ECN"], errors="coerce").astype("Int64")
    if "DOJ Knack" in df.columns:
        df["DOJ Knack"] = pd.to_datetime(df["DOJ Knack"], errors="coerce")
    if "Date of Separation" in df.columns:
        df["Date of Separation"] = pd.to_datetime(df["Date of Separation"], errors="coerce")
    df = ensure_columns(df, STAFF_EXTRA_COLS, default=np.nan)
    df = reorder_columns(df, STAFF_ORDER)
    return df

def query_ews(ds):
    files = ds.find_files(SP_EWS_FOLDER)
    if not files:
        raise FileNotFoundError(f"No files found in EWS folder")
    frames = [ds.read_excel_first_sheet(f) for f in files]
    df = pd.concat(frames, ignore_index=True)
    df = safe_drop(df, ["Source.Name","Id","Completion time"])
    df = df.rename(columns={"Start time": "Date Submitted"})
    if "Name" in df.columns:
        df = df.rename(columns={"Name": "Submitted By"})
    df = ensure_columns(df, EWS_EXTRA_COLS, default=np.nan)
    df = reorder_columns(df, EWS_ORDER)
    return df

def query_managers_clark(ds):
    files = ds.find_files(SP_CLARK_FOLDER, name_exact="exported.xlsx")
    if not files:
        raise FileNotFoundError("exported.xlsx not found in Clark folder")
    df = ds.read_excel_all_sheets(files[0])
    if "ECN" in df.columns:
        df["ECN"] = pd.to_numeric(df["ECN"], errors="coerce").astype("Int64")
    if "DOJ Knack" in df.columns:
        df["DOJ Knack"] = pd.to_datetime(df["DOJ Knack"], errors="coerce")
    for c in ["Employee","Supervisor","Manager Name"]:
        if c in df.columns:
            df[c] = df[c].astype(str).replace({"nan": np.nan,"None": np.nan})
    df = df.sort_values("DOJ Knack", ascending=False, na_position="last")
    df = df.drop_duplicates(subset=["ECN"], keep="first")
    df = ensure_columns(df, SPROUT_EXTRA_COLS, default=np.nan)
    df = reorder_columns(df, SPROUT_ORDER)
    return df

def query_clark(clark_active, clark_inactive):
    df = pd.concat([clark_active, clark_inactive], ignore_index=True)
    tagging_vals = df["Tagging"]         if "Tagging"         in df.columns else pd.Series(np.nan, index=df.index)
    ai_vals      = df["Active/Inactive"] if "Active/Inactive" in df.columns else pd.Series(np.nan, index=df.index)
    df["Custom"] = np.where(tagging_vals.notna(), tagging_vals, ai_vals)
    df = safe_drop(df, ["Tagging","Active/Inactive"])
    df = df.rename(columns={"Custom": "Active/Inactive"})
    df["Date of Separation"] = pd.to_datetime(df["Date of Separation"] if "Date of Separation" in df.columns else pd.Series(dtype="object"), errors="coerce")
    if "ECN" in df.columns:
        df["ECN"] = pd.to_numeric(df["ECN"], errors="coerce").astype("Int64")
    df = df.sort_values("ECN", ascending=True, na_position="last")
    df = df.drop_duplicates(subset=["ECN"], keep="first")
    return df

def query_final_clark(managers_clark, clark):
    CLARK_COLS = [
        "ECN","Employee","Project","Sub-Process","Supervisor","Role","Assitant Manager",
        "Manager","Sr Manager","Director","DOJ Knack","DOJ Project","Aging Knack",
        "Aging Project","Date of Separation","Shift Timing","Email","NT Login","Structure",
        "Billable/Buffer","Process Owner","Department","Aging Bucket","Start of the Month",
        "End of the Month","Equivalent Band-Level","Location","Hired For","Allocated Seats",
        "Gender","Seat Number","Global ID (GPP)","Invoice Status","Days","Month","WorkWeek",
        "Validation","Checker","Validate","Source.Name","Sr No","Date","Year","Attrition Type",
        "Reason for Attrition","Column98","Active/Inactive"
    ]
    existing_clark_cols = [c for c in CLARK_COLS if c in clark.columns]
    clark_sub = clark[existing_clark_cols].copy()
    clark_sub.columns = [f"Clark.{c}" for c in clark_sub.columns]
    df = managers_clark.copy()
    if "Role" in df.columns:
        df = df.rename(columns={"Role": "Role1"})
    df = df.merge(clark_sub, left_on="ECN", right_on="Clark.ECN", how="left")
    df = safe_drop(df, ["Clark.ECN","Clark.Employee","Clark.Supervisor","Clark.Manager","Clark.DOJ Knack","Clark.Date of Separation"])
    if "Manager Name" in df.columns:
        df = df.rename(columns={"Manager Name": "Manager"})
    if "Separation Date" in df.columns:
        df = df.rename(columns={"Separation Date": "Date of Separation"})
    clark_rename = {
        "Clark.Project":"Project","Clark.Sub-Process":"Sub-Process","Clark.Role":"Role",
        "Clark.Assitant Manager":"Assitant Manager","Clark.Sr Manager":"Sr Manager",
        "Clark.Director":"Director","Clark.DOJ Project":"DOJ Project",
        "Clark.Aging Knack":"Aging Knack","Clark.Aging Project":"Aging Project",
        "Clark.Shift Timing":"Shift Timing","Clark.Email":"Email","Clark.NT Login":"NT Login",
        "Clark.Structure":"Structure","Clark.Billable/Buffer":"Billable/Buffer",
        "Clark.Process Owner":"Process Owner","Clark.Department":"Department",
        "Clark.Aging Bucket":"Aging Bucket","Clark.Start of the Month":"Start of the Month",
        "Clark.End of the Month":"End of the Month","Clark.Equivalent Band-Level":"Equivalent Band-Level",
        "Clark.Location":"Location","Clark.Hired For":"Hired For","Clark.Allocated Seats":"Allocated Seats",
        "Clark.Gender":"Gender","Clark.Seat Number":"Seat Number","Clark.Global ID (GPP)":"Global ID (GPP)",
        "Clark.Invoice Status":"Invoice Status","Clark.Days":"Days","Clark.Month":"Month",
        "Clark.WorkWeek":"WorkWeek","Clark.Validation":"Validation","Clark.Checker":"Checker",
        "Clark.Validate":"Validate","Clark.Source.Name":"Source.Name","Clark.Sr No":"Sr No",
        "Clark.Date":"Date","Clark.Year":"Year","Clark.Attrition Type":"Attrition Type",
        "Clark.Reason for Attrition":"Reason for Attrition","Clark.Column98":"Column98",
        "Clark.Active/Inactive":"Active/Inactive",
    }
    df = df.rename(columns={k: v for k, v in clark_rename.items() if k in df.columns})
    proj_raw  = df["Project"].fillna("").astype(str).str.strip()          if "Project"          in df.columns else pd.Series("", index=df.index)
    sep_dates = pd.to_datetime(df["Date of Separation"], errors="coerce") if "Date of Separation" in df.columns else pd.Series(pd.NaT, index=df.index)
    ai_vals   = df["Active/Inactive"]                                     if "Active/Inactive"    in df.columns else pd.Series(np.nan, index=df.index)
    is_blank  = proj_raw == ""
    has_sep   = sep_dates.notna()
    df["Project1"]     = np.where(is_blank & has_sep, "Separated", np.where(is_blank & ~has_sep, "TBD", df["Project"]     if "Project"     in df.columns else np.nan))
    df["Sub-Process1"] = np.where(is_blank & has_sep, "Separated", np.where(is_blank & ~has_sep, "TBD", df["Sub-Process"] if "Sub-Process" in df.columns else np.nan))
    df["Active/Inactive1"] = np.where(is_blank & has_sep, "Inactive", np.where(is_blank & ~has_sep, "Active", ai_vals))
    df = df.sort_values("ECN", ascending=True, na_position="last")
    df = safe_drop(df, ["Active/Inactive"])
    df = df.rename(columns={"Active/Inactive1": "Active/Inactive"})
    df = safe_drop(df, ["Project","Sub-Process"])
    df = df.rename(columns={"Project1": "Project","Sub-Process1": "Sub-Process"})
    sep_dates2 = pd.to_datetime(df["Date of Separation"], errors="coerce") if "Date of Separation" in df.columns else pd.Series(pd.NaT, index=df.index)
    ai2        = df["Active/Inactive"] if "Active/Inactive" in df.columns else pd.Series(np.nan, index=df.index)
    df["Custom"] = np.where(sep_dates2.notna(), "Inactive", np.where(ai2.isin(["Inactive","Inactive "]), "Active", ai2))
    df = safe_drop(df, ["Active/Inactive"])
    df = df.rename(columns={"Custom": "Active/Inactive"})
    df = safe_drop(df, ["Role"])
    if "Role1" in df.columns:
        df = df.rename(columns={"Role1": "Role"})
    df = reorder_columns(df, CLARK_ORDER)
    return df


# ══════════════════════════════════════════════════════════════
# Excel builder (in-memory, returns bytes)
# ══════════════════════════════════════════════════════════════
def build_excel_bytes(dfs_dict: dict) -> bytes:
    from openpyxl import load_workbook
    from openpyxl.worksheet.table import Table, TableStyleInfo
    from openpyxl.utils import get_column_letter
    from openpyxl.styles import Font

    buf = io.BytesIO()
    sheet_name_map = {}
    for original in dfs_dict.keys():
        clean = re.sub(r'[:\\/*?\[\]]', '_', original)[:31]
        sheet_name_map[original] = clean

    with pd.ExcelWriter(buf, engine="openpyxl", date_format="YYYY-MM-DD", datetime_format="YYYY-MM-DD") as writer:
        for original, df in dfs_dict.items():
            df_out = df.copy()
            for col in df_out.columns:
                if pd.api.types.is_datetime64_any_dtype(df_out[col]):
                    df_out[col] = df_out[col].dt.date
            df_out.to_excel(writer, sheet_name=sheet_name_map[original], index=False)

    buf.seek(0)
    wb = load_workbook(buf)
    all_table_names = set()

    for original in dfs_dict.keys():
        ws = wb[sheet_name_map[original]]
        max_row, max_col = ws.max_row, ws.max_column
        if max_row < 2:
            continue
        safe_base  = re.sub(r'[^A-Za-z0-9]', '_', sheet_name_map[original])
        table_name = f"tbl_{safe_base}"[:30]
        suffix = 1
        while table_name in all_table_names:
            table_name = f"tbl_{safe_base}"[:27] + f"_{suffix:02d}"; suffix += 1
        all_table_names.add(table_name)
        tab = Table(displayName=table_name, ref=f"A1:{get_column_letter(max_col)}{max_row}")
        tab.tableStyleInfo = TableStyleInfo(name="TableStyleMedium9", showRowStripes=True)
        ws.add_table(tab)

    gpp_clean = sheet_name_map.get("GPP","GPP")
    if gpp_clean in wb.sheetnames:
        gpp_ws = wb[gpp_clean]
        adapt_col_idx = ecn_col_idx = None
        for idx, cell in enumerate(gpp_ws[1], start=1):
            if cell.value == "Adapt Email":  adapt_col_idx = idx
            elif cell.value == "ECN Lookup": ecn_col_idx   = idx
        if adapt_col_idx and ecn_col_idx:
            adapt_letter = get_column_letter(adapt_col_idx)
            ecn_letter   = get_column_letter(ecn_col_idx)
            for row in range(2, gpp_ws.max_row + 1):
                c = gpp_ws[f"{ecn_letter}{row}"]
                c.value = f'=_xlfn.XLOOKUP({adapt_letter}{row},Staff!U:U,Staff!A:A,"")'
                c.font  = Font(color="000000")

    out = io.BytesIO()
    wb.save(out)
    return out.getvalue()


# ══════════════════════════════════════════════════════════════
# Run all queries with live progress
# ══════════════════════════════════════════════════════════════
def run_all_queries(ds, progress_bar, status_placeholder, log_placeholder):
    logs   = []
    results = {}
    errors  = {}

    STEPS = [
        ("Q1 · GPP Active",       lambda: query_gpp_active(ds)),
        ("Q2 · GPP Inactive New", lambda: query_gpp_inactive_new(ds)),
        ("Q3 · GPP Inactive Old", lambda: query_gpp_inactive_old(ds)),
        ("Q5 · Clark Active",     lambda: query_clark_active(ds)),
        ("Q6 · Clark Inactive",   lambda: query_clark_inactive(ds)),
        ("Q7 · Staff",            lambda: query_staff(ds)),
        ("Q8 · EWS",              lambda: query_ews(ds)),
        ("Q11 · Managers Clark",  lambda: query_managers_clark(ds)),
    ]
    total = len(STEPS) + 5   # +5 for derived queries + excel build

    def add_log(msg, level="info"):
        ts = datetime.now().strftime("%H:%M:%S")
        icon = {"ok":"✓","warn":"⚠","err":"✗","info":"→"}.get(level, "→")
        css_class = {"ok":"log-ok","warn":"log-warn","err":"log-err","info":"log-info"}.get(level, "log-info")
        logs.append(f'<span class="{css_class}">[{ts}] {icon} {msg}</span>')
        log_html = "<br>".join(logs[-20:])
        log_placeholder.markdown(f'<div class="log-console">{log_html}</div>', unsafe_allow_html=True)

    step = 0
    for label, fn in STEPS:
        status_placeholder.markdown(f'<p style="color:rgba(255,255,255,0.5);font-size:0.85rem;margin:4px 0">Running {label}…</p>', unsafe_allow_html=True)
        add_log(f"Starting {label}")
        try:
            result = fn()
            results[label] = result
            add_log(f"{label} → {len(result):,} rows × {len(result.columns)} cols", "ok")
        except Exception as e:
            errors[label] = str(e)
            add_log(f"{label} FAILED: {e}", "err")
        step += 1
        progress_bar.progress(step / total)

    # Derived
    status_placeholder.markdown('<p style="color:rgba(255,255,255,0.5);font-size:0.85rem;margin:4px 0">Building Q4 · GPP…</p>', unsafe_allow_html=True)
    if all(k in results for k in ["Q1 · GPP Active","Q2 · GPP Inactive New","Q3 · GPP Inactive Old"]):
        try:
            gpp = query_gpp(results["Q1 · GPP Active"], results["Q2 · GPP Inactive New"], results["Q3 · GPP Inactive Old"])
            results["GPP"] = gpp
            add_log(f"Q4 · GPP → {len(gpp):,} rows", "ok")
        except Exception as e:
            errors["Q4 · GPP"] = str(e)
            add_log(f"Q4 · GPP FAILED: {e}", "err")
    step += 1; progress_bar.progress(step / total)

    status_placeholder.markdown('<p style="color:rgba(255,255,255,0.5);font-size:0.85rem;margin:4px 0">Building Q12 · Clark…</p>', unsafe_allow_html=True)
    if "Q5 · Clark Active" in results and "Q6 · Clark Inactive" in results:
        try:
            clark = query_clark(results["Q5 · Clark Active"], results["Q6 · Clark Inactive"])
            results["_clark"] = clark
            add_log(f"Q12 · Clark → {len(clark):,} rows", "ok")
        except Exception as e:
            errors["Q12 · Clark"] = str(e)
            add_log(f"Q12 · Clark FAILED: {e}", "err")
    step += 1; progress_bar.progress(step / total)

    status_placeholder.markdown('<p style="color:rgba(255,255,255,0.5);font-size:0.85rem;margin:4px 0">Building Q13 · Final Clark…</p>', unsafe_allow_html=True)
    if "Q11 · Managers Clark" in results and "_clark" in results:
        try:
            fc = query_final_clark(results["Q11 · Managers Clark"], results["_clark"])
            results["Clark"] = fc
            add_log(f"Q13 · Final Clark → {len(fc):,} rows", "ok")
        except Exception as e:
            errors["Q13 · Final Clark"] = str(e)
            add_log(f"Q13 · Final Clark FAILED: {e}", "err")
    step += 1; progress_bar.progress(step / total)

    # Map to output tabs
    tab_map = {
        "GPP":    results.get("GPP"),
        "Clark":  results.get("Clark"),
        "Staff":  results.get("Q7 · Staff"),
        "EWS":    results.get("Q8 · EWS"),
        "Sprout": results.get("Q11 · Managers Clark"),
    }
    output_tabs = {k: v for k, v in tab_map.items() if v is not None}

    status_placeholder.markdown('<p style="color:rgba(255,255,255,0.5);font-size:0.85rem;margin:4px 0">Building Excel file…</p>', unsafe_allow_html=True)
    add_log(f"Building Excel with {len(output_tabs)} sheets…")
    excel_bytes = None
    if output_tabs:
        try:
            excel_bytes = build_excel_bytes(output_tabs)
            add_log(f"Excel ready — {len(excel_bytes)/1024:.0f} KB", "ok")
        except Exception as e:
            errors["Excel Build"] = str(e)
            add_log(f"Excel build FAILED: {e}", "err")
    step += 1; progress_bar.progress(step / total)

    status_placeholder.markdown('<p style="color:rgba(99,179,237,0.8);font-size:0.85rem;margin:4px 0;font-weight:600">✓ Complete</p>', unsafe_allow_html=True)
    return output_tabs, errors, excel_bytes


# ══════════════════════════════════════════════════════════════
# MAIN UI
# ══════════════════════════════════════════════════════════════

def render_login_page():
    st.markdown("""
    <div style="text-align:center; padding: 60px 20px 20px;">
        <div style="display:inline-block; background: linear-gradient(135deg,#63b3ed,#9a75ea);
                    width:80px;height:80px;border-radius:22px;line-height:80px;
                    font-size:38px;margin-bottom:24px;
                    box-shadow: 0 12px 40px rgba(99,179,237,0.35);">🏥</div>
        <div class="hero-title">Knack RCM Report</div>
        <div class="hero-sub" style="margin-bottom:40px;">Headcount Intelligence Platform</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.6, 1])
    with col2:
        st.markdown('<div class="knack-card-accent">', unsafe_allow_html=True)
        st.markdown('<p class="section-label">Sign in to continue</p>', unsafe_allow_html=True)
        st.markdown("""
        <p style="color:rgba(255,255,255,0.55);font-size:0.88rem;margin-bottom:20px;line-height:1.6;">
        This app connects to your Knack SharePoint to pull live headcount data.
        Sign in with your Microsoft work account to get started.
        </p>
        """, unsafe_allow_html=True)

        auth_url = get_auth_url()
        if auth_url:
            st.markdown(f"""
            <a href="{auth_url}" target="_self" style="text-decoration:none;">
              <div style="background:linear-gradient(135deg,#0078d4,#005a9e);
                          border-radius:12px;padding:14px 24px;text-align:center;
                          color:white;font-weight:600;font-size:0.95rem;cursor:pointer;
                          box-shadow:0 4px 20px rgba(0,120,212,0.4);
                          transition:all 0.2s ease;border:1px solid rgba(255,255,255,0.15);">
                <span style="font-size:1.1em;margin-right:10px;">⊞</span>
                Sign in with Microsoft
              </div>
            </a>
            """, unsafe_allow_html=True)
        else:
            st.error("⚠️ Azure app credentials not configured. Add them to `.streamlit/secrets.toml`.")
            with st.expander("Setup instructions"):
                st.markdown("""
**1. Create Azure App Registration**
- Go to [portal.azure.com](https://portal.azure.com) → Azure Active Directory → App registrations → New
- Set Redirect URI to your Streamlit app URL + `/` (e.g. `http://localhost:8501/`)

**2. Add to `.streamlit/secrets.toml`:**
```toml
AZURE_CLIENT_ID     = "your-client-id"
AZURE_TENANT_ID     = "your-tenant-id"
AZURE_CLIENT_SECRET = "your-client-secret"
REDIRECT_URI        = "http://localhost:8501/"
```

**3. Grant API permissions:**
- Microsoft Graph → `User.Read`
- SharePoint → `AllSites.Read` or `Sites.Selected`
                """)
        st.markdown('</div>', unsafe_allow_html=True)


def render_dashboard(user_info: dict):
    display_name = user_info.get("displayName", "User")
    mail         = user_info.get("mail") or user_info.get("userPrincipalName", "")

    # ── Sidebar ──────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:16px 0 8px;">
            <div style="background:linear-gradient(135deg,#63b3ed22,#9a75ea22);
                        border:1px solid rgba(99,179,237,0.2);border-radius:14px;padding:16px;">
                <div style="width:44px;height:44px;background:linear-gradient(135deg,#63b3ed,#9a75ea);
                            border-radius:12px;display:flex;align-items:center;justify-content:center;
                            font-weight:700;font-size:1.1rem;color:white;margin-bottom:12px;">
                    {display_name[0].upper()}
                </div>
                <div style="font-weight:600;color:rgba(255,255,255,0.9);font-size:0.9rem;">{display_name}</div>
                <div style="color:rgba(255,255,255,0.4);font-size:0.75rem;margin-top:2px;">{mail}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('<p class="section-label">SharePoint</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="color:rgba(255,255,255,0.45);font-size:0.78rem;word-break:break-all;">{SITE_URL}</p>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('<p class="section-label">Output Sheets</p>', unsafe_allow_html=True)
        for sheet in ["GPP","Clark","Staff","EWS","Sprout"]:
            st.markdown(f'<div style="display:flex;align-items:center;gap:8px;padding:4px 0;color:rgba(255,255,255,0.6);font-size:0.82rem;"><span style="color:#63b3ed;">▸</span> {sheet}</div>', unsafe_allow_html=True)

        st.markdown("---")
        if st.button("🚪 Sign Out"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

    # ── Main header ──────────────────────────────────────────
    st.markdown("""
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
        <div>
            <div class="hero-title" style="font-size:1.9rem;">Knack RCM Report</div>
            <div class="hero-sub">Pull, transform and download your headcount data</div>
        </div>
        <span class="badge badge-blue">SharePoint Mode</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # ── Run button ───────────────────────────────────────────
    col_run, col_info = st.columns([2, 5])
    with col_run:
        run_clicked = st.button("▶ Generate Report", use_container_width=True)

    # ── Results state ────────────────────────────────────────
    if "report_ready" not in st.session_state:
        st.session_state.report_ready = False

    if run_clicked:
        st.session_state.report_ready = False
        st.markdown("---")
        st.markdown('<p class="section-label">Processing</p>', unsafe_allow_html=True)
        prog_bar       = st.progress(0)
        status_ph      = st.empty()
        log_ph         = st.empty()

        try:
            ds = SharePointDataSource(st.session_state["access_token"], log_fn=lambda m, l="info": None)
            output_tabs, errors, excel_bytes = run_all_queries(ds, prog_bar, status_ph, log_ph)
            st.session_state["output_tabs"]  = output_tabs
            st.session_state["report_errors"] = errors
            st.session_state["excel_bytes"]  = excel_bytes
            st.session_state.report_ready    = True
        except Exception as e:
            st.error(f"Fatal error: {e}")
            traceback.print_exc()

    # ── Results ──────────────────────────────────────────────
    if st.session_state.report_ready:
        output_tabs = st.session_state.get("output_tabs", {})
        errors      = st.session_state.get("report_errors", {})
        excel_bytes = st.session_state.get("excel_bytes")

        st.markdown("---")

        # Summary row
        total_rows = sum(len(v) for v in output_tabs.values())
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="knack-card"><div class="section-label">Sheets</div><div style="font-size:2rem;font-weight:700;color:#63b3ed;">{len(output_tabs)}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="knack-card"><div class="section-label">Total Rows</div><div style="font-size:2rem;font-weight:700;color:#9a75ea;">{total_rows:,}</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="knack-card"><div class="section-label">Errors</div><div style="font-size:2rem;font-weight:700;color:{"#f56565" if errors else "#48bb78"};">{len(errors)}</div></div>', unsafe_allow_html=True)
        with c4:
            ts = datetime.now().strftime("%b %d, %H:%M")
            st.markdown(f'<div class="knack-card"><div class="section-label">Generated</div><div style="font-size:1.1rem;font-weight:600;color:rgba(255,255,255,0.7);margin-top:6px;">{ts}</div></div>', unsafe_allow_html=True)

        # Download
        if excel_bytes:
            fname = f"Knack_RCM_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
            st.markdown('<div style="margin:16px 0 8px;"><p class="section-label">Download</p></div>', unsafe_allow_html=True)
            dl_col, _ = st.columns([1, 2])
            with dl_col:
                st.download_button(
                    label="⬇ Download Knack_RCM_Report.xlsx",
                    data=excel_bytes,
                    file_name=fname,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

        # Data preview tabs
        if output_tabs:
            st.markdown('<div style="margin-top:24px;"><p class="section-label">Data Preview</p></div>', unsafe_allow_html=True)
            tab_objs = st.tabs(list(output_tabs.keys()))
            for tab_obj, (name, df) in zip(tab_objs, output_tabs.items()):
                with tab_obj:
                    c_l, c_r = st.columns([3, 1])
                    with c_l:
                        st.markdown(f'<span class="stat-pill">{len(df):,} rows</span> <span class="stat-pill purple">{len(df.columns)} cols</span>', unsafe_allow_html=True)
                    with c_r:
                        st.markdown(f'<div style="text-align:right;color:rgba(255,255,255,0.35);font-size:0.75rem;font-family:\'DM Mono\',monospace;">{name}</div>', unsafe_allow_html=True)
                    st.dataframe(df.head(100), use_container_width=True, height=320)

        # Errors
        if errors:
            with st.expander(f"⚠ {len(errors)} query error(s)"):
                for q, msg in errors.items():
                    st.markdown(f'<div style="background:rgba(245,101,101,0.08);border:1px solid rgba(245,101,101,0.2);border-radius:8px;padding:10px 14px;margin-bottom:8px;"><span style="color:#f56565;font-weight:600;">{q}</span><br><span style="color:rgba(255,255,255,0.5);font-size:0.8rem;font-family:\'DM Mono\',monospace;">{msg}</span></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# Auth flow — handle redirect code
# ══════════════════════════════════════════════════════════════
def handle_auth_callback():
    """Exchange ?code= from Microsoft redirect for tokens."""
    try:
        params = st.query_params
        code   = params.get("code")
        if not code:
            return False

        result = exchange_code_for_token(code)
        if result and "access_token" in result:
            st.session_state["access_token"]  = result["access_token"]
            st.session_state["id_token_claims"] = result.get("id_token_claims", {})
            user_info = get_user_info(result["access_token"])
            st.session_state["user_info"]     = user_info
            st.session_state["authenticated"] = True
            # Clear code from URL
            st.query_params.clear()
            return True
        else:
            err = result.get("error_description", "Unknown error") if result else "No response"
            st.error(f"Authentication failed: {err}")
            return False
    except Exception as e:
        st.error(f"Auth callback error: {e}")
        return False


def main():
    # 1. Handle OAuth callback
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        if handle_auth_callback():
            st.rerun()

    # 2. Route to login or dashboard
    if st.session_state["authenticated"]:
        user_info = st.session_state.get("user_info", {})
        render_dashboard(user_info)
    else:
        render_login_page()


if __name__ == "__main__":
    main()
