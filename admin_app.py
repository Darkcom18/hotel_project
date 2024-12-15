import streamlit as st
from utils import read_google_sheet, write_to_google_sheet, create_qr_code
import pandas as pd

# Google Sheet ID
SHEET_ID = "1hxHrZKQftOE1zaPzsxlrUfK_Hs2MD8N-I5NOpTahDWU"  # Thay bằng Sheet ID của bạn

# Tabs quản lý
tab = st.sidebar.selectbox("Chọn tab", [
    "Tạo mã QR", 
    "Xem lại QR Code", 
    "Tạo menu đồ ăn/thức uống", 
    "Xem lại menu", 
    "Xem đơn hàng"
])

# 1. Tạo mã QR
if tab == "Tạo mã QR":
    st.header("Tạo mã QR cho từng phòng")
    qr_data = read_google_sheet(SHEET_ID, "qr_codes")
    room_number = st.text_input("Nhập số phòng:")
    if st.button("Tạo QR Code"):
        if room_number:
            qr_url = f"https://orderdanacitytest.streamlit.app/?room={room_number}"  # Link đến ứng dụng đặt hàng
            qr_image = create_qr_code(qr_url)
            new_qr = pd.DataFrame({"Phòng": [room_number], "Link": [qr_url]})
            qr_data = pd.concat([qr_data, new_qr], ignore_index=True)
            write_to_google_sheet(SHEET_ID, "qr_codes", qr_data)
            st.image(qr_image, caption=f"QR Code - Phòng {room_number}")
            st.success(f"QR Code cho phòng {room_number} đã được tạo và lưu.")
        else:
            st.error("Vui lòng nhập số phòng.")

# 2. Xem lại QR Code
elif tab == "Xem lại QR Code":
    st.header("Danh sách QR Code đã tạo")
    qr_data = read_google_sheet(SHEET_ID, "qr_codes")
    if qr_data.empty:
        st.info("Chưa có QR Code nào được tạo.")
    else:
        for _, row in qr_data.iterrows():
            st.subheader(f"Phòng: {row['Phòng']}")
            st.write(f"Link: [Đặt hàng tại đây]({row['Link']})")
            qr_image = create_qr_code(row['Link'])
            st.image(qr_image, caption=f"QR Code - Phòng {row['Phòng']}")

# 3. Tạo menu đồ ăn/thức uống
elif tab == "Tạo menu đồ ăn/thức uống":
    st.header("Cập nhật menu")
    menu_data = read_google_sheet(SHEET_ID, "menu")
    item_name = st.text_input("Tên món:")
    item_desc = st.text_input("Miêu tả món:")
    item_price = st.number_input("Giá món:", min_value=0.0)
    uploaded_image = st.file_uploader("Tải lên ảnh món ăn (tùy chọn)", type=["jpg", "png", "jpeg"])

    if st.button("Thêm món"):
        if item_name and item_desc and item_price > 0:
            new_item = pd.DataFrame({
                "Món ăn": [item_name], 
                "Miêu tả": [item_desc], 
                "Giá": [item_price], 
                "Ảnh": [uploaded_image.name if uploaded_image else ""]
            })
            menu_data = pd.concat([menu_data, new_item], ignore_index=True)
            write_to_google_sheet(SHEET_ID, "menu", menu_data)
            st.success("Thêm món thành công!")
        else:
            st.error("Vui lòng nhập đầy đủ thông tin món ăn.")

# 4. Xem lại menu
elif tab == "Xem lại menu":
    st.header("Menu hiện tại")
    menu_data = read_google_sheet(SHEET_ID, "menu")
    if menu_data.empty:
        st.info("Chưa có món ăn nào trong menu.")
    else:
        for _, row in menu_data.iterrows():
            st.subheader(row['Món ăn'])
            st.write(f"Miêu tả: {row['Miêu tả']}")
            st.write(f"Giá: {row['Giá']} VND")
            if row['Ảnh']:
                st.image(row['Ảnh'], caption=row['Món ăn'])
            else:
                st.warning("Không có ảnh cho món ăn này.")

# 5. Xem đơn hàng
elif tab == "Xem đơn hàng":
    st.header("Danh sách đơn hàng")
    orders_data = read_google_sheet(SHEET_ID, "orders")
    if orders_data.empty:
        st.info("Chưa có đơn hàng nào.")
    else:
        # Hiển thị danh sách đơn hàng theo phòng
        st.dataframe(orders_data)

        # Hiển thị chi tiết đơn hàng
        selected_room = st.selectbox("Chọn phòng để xem chi tiết", options=orders_data['Phòng'].unique())
        room_orders = orders_data[orders_data['Phòng'] == selected_room]
        st.subheader(f"Đơn hàng của phòng {selected_room}")
        st.table(room_orders)
