import streamlit as st
from utils import read_google_sheet, write_to_google_sheet
import pandas as pd

# Google Sheet ID
SHEET_ID = "1hxHrZKQftOE1zaPzsxlrUfK_Hs2MD8N-I5NOpTahDWU"  # Thay bằng Sheet ID của bạn

# Lấy số phòng từ URL
query_params = st.experimental_get_query_params()
room_number = query_params.get("room", [""])[0]

if not room_number:
    st.error("Không tìm thấy thông tin phòng. Vui lòng quét lại mã QR hoặc liên hệ quản lý.")
else:
    st.title("Đặt hàng Nhà Hàng")
    st.write(f"Phòng: {room_number}")

    # Đọc menu từ Google Sheets
    menu_data = read_google_sheet(SHEET_ID, "menu")
    if menu_data.empty:
        st.info("Hiện tại chưa có món ăn nào.")
    else:
        st.subheader("Menu")
        orders = []  # Danh sách các món đặt hàng

        # Hiển thị menu
        for _, row in menu_data.iterrows():
            st.subheader(row['Món ăn'])
            st.write(f"Miêu tả: {row['Miêu tả']}")
            st.write(f"Giá: {row['Giá']} VND")
            if row['Ảnh']:
                st.image(row['Ảnh'], caption=row['Món ăn'])

            # Nhập số lượng đặt món
            quantity = st.number_input(f"Số lượng {row['Món ăn']}:", min_value=0, step=1, key=row['Món ăn'])
            if quantity > 0:
                orders.append({
                    "Phòng": room_number,
                    "Món ăn": row['Món ăn'],
                    "Số lượng": quantity,
                    "Tổng giá": quantity * row['Giá']
                })

        # Gửi đơn hàng
        if st.button("Gửi Đơn Hàng"):
            if orders:
                new_order = pd.DataFrame(orders)
                # Đọc danh sách đơn hàng hiện có từ Google Sheets
                orders_data = read_google_sheet(SHEET_ID, "orders")
                # Cập nhật danh sách đơn hàng
                orders_data = pd.concat([orders_data, new_order], ignore_index=True)
                write_to_google_sheet(SHEET_ID, "orders", orders_data)  # Ghi dữ liệu vào Google Sheets
                st.success("Đơn hàng đã được gửi thành công!")
            else:
                st.warning("Vui lòng chọn ít nhất một món để đặt hàng.")
