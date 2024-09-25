import gspread
from oauth2client.service_account import ServiceAccountCredentials

class GoogleSheets:
    def __init__(self, credentials_file, sheet_name):
        self.credentials_file = credentials_file
        self.sheet_name = sheet_name
        self.gc = self.authorize_google_sheets()
        self.ensure_headers_exist()

    def authorize_google_sheets(self):
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_file, scope)
        return gspread.authorize(credentials)

    def append_row(self, row_data):
        worksheet = self.gc.open(self.sheet_name).sheet1
        worksheet.append_row(row_data)

    def ensure_headers_exist(self):
        worksheet = self.gc.open(self.sheet_name).sheet1
        existing_headers = worksheet.row_values(1)
        if existing_headers != ['User id', 'Username', 'Date', 'Last Message Status']:
            worksheet.insert_row(['User id', 'Username', 'Date', 'Last Message Status'], 1)

    def update_cell(self, row, col, value):
        worksheet = self.gc.open(self.sheet_name).sheet1
        worksheet.update_cell(row, col, value)