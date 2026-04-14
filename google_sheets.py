import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def get_sheet(sheet_id: str, worksheet_name: str = None):
    creds = Credentials.from_service_account_file("service_account.json", scopes=SCOPES)
    client = gspread.authorize(creds)
    sh = client.open_by_key(sheet_id)
    if worksheet_name:
        return sh.worksheet(worksheet_name)
    return sh.sheet1

def append_row(sheet, row: list):
    sheet.append_row(row, value_input_option="USER_ENTERED")
