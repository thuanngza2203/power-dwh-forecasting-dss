# db_connect.py
from sqlalchemy import create_engine, text
import urllib

def get_db_engine():
    """
    Hàm thiết lập kết nối tới SQL Server và trả về đối tượng Engine.
    """

    SERVER_NAME = 'ThuanNguyen\SQLEXPRESS'  
    DATABASE_NAME = 'DW_Electric'          
    DRIVER = 'ODBC Driver 17 for SQL Server'

    # connection string
    params = urllib.parse.quote_plus(
        f"DRIVER={{{DRIVER}}};SERVER={SERVER_NAME};DATABASE={DATABASE_NAME};Trusted_Connection=yes;"
    )
    
    engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
    return engine

if __name__ == "__main__":
    print("--- ĐANG KIỂM TRA KẾT NỐI... ---")
    try:
        engine = get_db_engine()
        # Thử thực hiện một kết nối thực tế
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print(f"--> KẾT NỐI THÀNH CÔNG! Server phản hồi: {result.scalar()}")
    except Exception as e:
        print("\n--> KẾT NỐI THẤT BẠI! Hãy kiểm tra lỗi bên dưới:")
        print(e)