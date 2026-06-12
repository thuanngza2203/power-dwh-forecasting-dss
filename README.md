# Smart Energy Data Warehouse

Project xây dựng Data Warehouse và dashboard giám sát điện năng hộ gia đình. Dữ liệu được xử lý bằng ETL, lưu vào SQL Server, trực quan hóa bằng Streamlit và dùng để dự báo phụ tải bằng các mô hình Machine Learning.

## Chức năng chính

- Làm sạch và biến đổi dữ liệu tiêu thụ điện theo phút.
- Xây dựng mô hình dữ liệu gồm `Dim_Date`, `Dim_Time` và `Fact_PowerConsumption`.
- Theo dõi công suất, điện áp, cường độ dòng điện và mức tiêu thụ theo thiết bị.
- Lọc dữ liệu theo ngày và khung giờ trên dashboard.
- Huấn luyện và so sánh các mô hình:
  - Linear Regression
  - XGBoost
  - Neural Network (`MLPRegressor`)
- Dự báo phụ tải cho 24 giờ tiếp theo từ 48 giờ dữ liệu gần nhất.

## Cấu trúc thư mục

```text
Assignment/
|-- app.py                         # Ứng dụng Streamlit
|-- db_connect.py                  # Kết nối database cho ứng dụng
|-- data/                          # Dữ liệu thô, không đưa lên Git
|-- ETL/
|   |-- ETL_Process.ipynb          # Làm sạch và nạp dữ liệu vào DWH
|   `-- db_connect.py              # Kết nối database cho ETL
|-- model/
|   |-- DM_Predection.ipynb        # Thử nghiệm và đánh giá mô hình
|   `-- db_connect.py              # Kết nối database cho notebook model
|-- .gitignore
`-- README.md
```

## Yêu cầu hệ thống

- Python 3.10 trở lên
- SQL Server hoặc SQL Server Express
- Microsoft ODBC Driver 17 for SQL Server
- Jupyter Notebook hoặc JupyterLab

## Cài đặt

Tạo và kích hoạt môi trường ảo:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Cài đặt các thư viện:

```powershell
pip install streamlit pandas numpy matplotlib seaborn scikit-learn xgboost sqlalchemy pyodbc jupyter
```

## Chuẩn bị dữ liệu

Project sử dụng bộ dữ liệu **Individual Household Electric Power Consumption**. Sau khi tải và giải nén, đặt file theo đường dẫn:

```text
data/household_power_consumption.txt/household_power_consumption.txt
```

File dữ liệu cần có các cột:

```text
Date
Time
Global_active_power
Global_reactive_power
Voltage
Global_intensity
Sub_metering_1
Sub_metering_2
Sub_metering_3
```

Thư mục `data/` được khai báo trong `.gitignore` vì chứa file dữ liệu lớn.

## Cấu hình SQL Server

Tạo database có tên `DW_Electric`, sau đó cập nhật thông tin kết nối trong các file `db_connect.py`:

```python
SERVER_NAME = r'ThuanNguyen\SQLEXPRESS'
DATABASE_NAME = 'DW_Electric'
DRIVER = 'ODBC Driver 17 for SQL Server'
```

Các file cần kiểm tra:

- `db_connect.py`
- `ETL/db_connect.py`
- `model/db_connect.py`

Project hiện sử dụng Windows Authentication qua `Trusted_Connection=yes`.

Có thể kiểm tra kết nối từ thư mục gốc:

```powershell
python db_connect.py
```

## Chạy project

### 1. Chạy ETL

Mở notebook:

```powershell
jupyter notebook ETL/ETL_Process.ipynb
```

Chạy lần lượt toàn bộ cell để đọc dữ liệu, làm sạch và nạp ba bảng sau vào SQL Server:

- `Dim_Date`
- `Dim_Time`
- `Fact_PowerConsumption`

Notebook đang sử dụng `if_exists='append'`. Không chạy lại bước nạp nhiều lần nếu chưa xóa dữ liệu cũ, vì có thể tạo dữ liệu trùng lặp.

### 2. Thử nghiệm mô hình

```powershell
jupyter notebook model/DM_Predection.ipynb
```

Notebook huấn luyện và đánh giá các mô hình bằng RMSE, MAE và R².

### 3. Khởi động dashboard

```powershell
streamlit run app.py
```

Sau đó mở địa chỉ Streamlit hiển thị trong terminal, mặc định là:

```text
http://localhost:8501
```

## Dự báo từ file mới

Trong tab dự báo:

1. Chọn thuật toán và nhấn **Huấn luyện lại từ DWH**.
2. Upload file `.txt` hoặc `.csv`.
3. Nhấn **Chạy Dự Báo** để dự báo 24 giờ tiếp theo.

File upload phải:

- Phân cách các cột bằng dấu chấm phẩy (`;`).
- Có ít nhất 48 giờ dữ liệu.
- Có các cột `Date`, `Time` và `Global_active_power`.
- Dùng định dạng ngày theo thứ tự ngày/tháng/năm.

## Lưu ý

- Dashboard chỉ chạy sau khi ETL đã tạo và nạp dữ liệu vào Data Warehouse.
- Mô hình được huấn luyện trong phiên Streamlit hiện tại và chưa được lưu thành file.
- Không commit thông tin đăng nhập, file `.env`, Streamlit secrets, dữ liệu thô hoặc model artifact lên Git.
"# power-dwh-forecasting-dss" 
