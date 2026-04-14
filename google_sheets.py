import gspread
import json
from google.oauth2.service_account import Credentials
import streamlit as st

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def get_sheet(sheet_id: str, worksheet_name: str = None):
    # FORCE: Only load from Streamlit secrets
    if "google" not in st.secrets:
        raise RuntimeError("Google service account JSON not found in Streamlit secrets")

    service_account_info = json.loads(st.secrets["google"]["service_account_json"])
    creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)

    client = gspread.authorize(creds)
    sh = client.open_by_key(sheet_id)

    if worksheet_name:
        return sh.worksheet(worksheet_name)
    return sh.sheet1

def append_row(sheet, row: list):
    sheet.append_row(row, value_input_option="USER_ENTERED")
