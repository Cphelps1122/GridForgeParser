import gspread
from google.oauth2.service_account import Credentials
import os

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def get_sheet(sheet_id: str, worksheet_name: str = None):
    # Path to service account file inside repo
    json_path = os.path.join(os.path.dirname(__file__), "service_account.json")

    creds = Credentials.from_service_account_file(json_path, scopes=SCOPES)
    client = gspread.authorize(creds)
    sh = client.open_by_key(sheet_id)

    if worksheet_name:
        return sh.worksheet(worksheet_name)
    return sh.sheet1

def append_row(sheet, row: list):
    sheet.append_row(row, value_input_option="USER_ENTERED")
