import pandas as pd
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from io import BytesIO
import qrcode
import json
import streamlit as st

sheet_id = "1hxHrZKQftOE1zaPzsxlrUfK_Hs2MD8N-I5NOpTahDWU"

def connect_to_google_sheet(sheet_id):
    """
    Kết nối đến Google Sheets bằng Sheet ID.
    Args:
        sheet_id (str): ID của Google Sheet.
    Returns:
        gspread.models.Spreadsheet: Đối tượng Google Sheet.
    """
    try:
        credentials_dict = st.secrets["GCP_CREDENTIALS"]
        temp_credentials_file = "temp_credentials.json"
        with open(temp_credentials_file, "w") as f:
            json.dump(dict(credentials_dict), f)

        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(temp_credentials_file, scope)
        client = gspread.authorize(creds)
        os.remove(temp_credentials_file)

        # Kết nối Google Sheet
        return client.open_by_key(sheet_id)

    except SpreadsheetNotFound:
        raise ValueError(f"Google Sheet với ID '{sheet_id}' không được tìm thấy. Kiểm tra Sheet ID và quyền truy cập.")

def read_google_sheet(sheet_id, worksheet_name):
    """
    Đọc dữ liệu từ một worksheet trong Google Sheet.
    Args:
        sheet_id (str): ID của Google Sheet.
        worksheet_name (str): Tên worksheet trong Google Sheet.
    Returns:
        pd.DataFrame: DataFrame chứa dữ liệu từ worksheet.
    """
    sheet = connect_to_google_sheet(sheet_id)
    worksheet = sheet.worksheet(worksheet_name)
    data = worksheet.get_all_records()  # Lấy tất cả các bản ghi dưới dạng danh sách từ điển
    return pd.DataFrame(data)

def write_to_google_sheet(sheet_id, worksheet_name, df):
    """
    Ghi dữ liệu từ DataFrame vào một worksheet trong Google Sheet.
    Args:
        sheet_id (str): ID của Google Sheet.
        worksheet_name (str): Tên worksheet trong Google Sheet.
        df (pd.DataFrame): DataFrame chứa dữ liệu cần ghi.
    """
    sheet = connect_to_google_sheet(sheet_id)
    worksheet = sheet.worksheet(worksheet_name)
    worksheet.clear()  # Xóa toàn bộ dữ liệu cũ
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())  # Cập nhật dữ liệu mới

def read_menu(sheet_id):
    """
    Đọc dữ liệu menu từ worksheet "menu".
    Args:
        sheet_id (str): ID của Google Sheet.
    Returns:
        pd.DataFrame: DataFrame chứa dữ liệu menu.
    """
    return read_google_sheet(sheet_id, "menu")

def write_menu(sheet_id, menu_df):
    """
    Ghi dữ liệu menu vào worksheet "menu".
    Args:
        sheet_id (str): ID của Google Sheet.
        menu_df (pd.DataFrame): DataFrame chứa dữ liệu menu cần ghi.
    """
    write_to_google_sheet(sheet_id, "menu", menu_df)
def read_orders(sheet_id):
    """
    Đọc dữ liệu đơn hàng từ worksheet "orders".
    Args:
        sheet_id (str): ID của Google Sheet.
    Returns:
        pd.DataFrame: DataFrame chứa dữ liệu đơn hàng.
    """
    return read_google_sheet(sheet_id, "orders")
def write_orders(sheet_id, orders_df):
    """
    Ghi dữ liệu đơn hàng vào worksheet "orders".
    Args:
        sheet_id (str): ID của Google Sheet.
        orders_df (pd.DataFrame): DataFrame chứa dữ liệu đơn hàng cần ghi.
    """
    write_to_google_sheet(sheet_id, "orders", orders_df)

def create_qr_code(url):
    """
    Tạo mã QR từ URL và trả về dữ liệu ảnh dưới dạng byte.
    """
    qr = qrcode.make(url)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    return buffer.getvalue()
