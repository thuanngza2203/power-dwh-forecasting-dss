import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPRegressor
import xgboost as xgb
from db_connect import get_db_engine

# --- 1. CẤU HÌNH & CSS (Giao diện đẹp) ---
st.set_page_config(
    page_title="PowerGrid Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS tùy chỉnh cho Card UI và Nút bấm
st.markdown("""
    <style>
    .stApp {background-color: #f4f7f6;}
    
    /* Style cho Metric Card */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: 0.3s;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
        border-color: #3498db;
    }
    
    /* Style cho Tabs */
    .stTabs [data-baseweb="tab-list"] {gap: 10px;}
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: white;
        border-radius: 8px 8px 0px 0px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ebf5fb;
        border-bottom: 3px solid #3498db;
        color: #2980b9;
    }
    </style>
    """, unsafe_allow_html=True)

# Cấu hình biểu đồ
sns.set_style("whitegrid", {'grid.linestyle': '--'})
plt.rcParams.update({'font.size': 9})

# --- 2. LOAD DATA (Lấy đủ các cột: Voltage, Intensity, Reactive...) ---
@st.cache_data
def load_data():
    engine = get_db_engine()
    # Query lấy TẤT CẢ chỉ số quan trọng
    query = """
    SELECT 
        d.FullDate,
        t.Hour,
        t.TimeOfDay,
        SUM(f.Global_active_power) as Active_Power,     -- Tổng công suất thực
        SUM(f.Global_reactive_power) as Reactive_Power, -- Tổng hao phí
        AVG(f.Voltage) as Voltage,                      -- Điện áp trung bình
        AVG(f.Global_intensity) as Intensity,           -- Cường độ trung bình
        SUM(f.Sub_metering_1) as Sub_Kitchen,
        SUM(f.Sub_metering_2) as Sub_Laundry,
        SUM(f.Sub_metering_3) as Sub_AC
    FROM Fact_PowerConsumption f
    JOIN Dim_Date d ON f.DateKey = d.DateKey
    JOIN Dim_Time t ON f.TimeKey = t.TimeKey
    GROUP BY d.FullDate, t.Hour, t.TimeOfDay
    ORDER BY d.FullDate, t.Hour
    """
    df = pd.read_sql(query, engine)
    df['FullDate'] = pd.to_datetime(df['FullDate'])
    return df

# --- 3. SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2933/2933116.png", width=70)
    st.markdown("### **Power Monitor**")
    st.info("Hệ thống Giám sát & Dự báo Điện năng Thông minh.")
    st.markdown("---")
    
    try:
        with st.spinner('Kết nối Data Warehouse...'):
            df = load_data()
        st.success("🟢 Kết nối Database: Ổn định")
    except Exception as e:
        st.error(f"🔴 Lỗi kết nối: {e}")
        st.stop()
    
    st.markdown("---")
    st.caption("© 2024 Smart Grid Project")

# --- 4. HEADER ---
c1, c2 = st.columns([1, 20])
with c1: st.write("⚡")
with c2: st.title("Smart Energy Dashboard")

# TABS CHÍNH
tab_olap, tab_ai = st.tabs(["📊 DASHBOARD GIÁM SÁT", "🔮 DỰ BÁO PHỤ TẢI (AI)"])

# ================= TAB 1: GIÁM SÁT ĐA CHIỀU (Phần bạn cần) =================
with tab_olap:
    # --- A. BỘ LỌC DỮ LIỆU ---
    with st.container():
        st.caption("🛠️ **Bộ lọc dữ liệu**")
        f1, f2, f3 = st.columns([1, 1, 2])
        with f1: start_date = st.date_input("Từ ngày:", df['FullDate'].min())
        with f2: end_date = st.date_input("Đến ngày:", df['FullDate'].max())
        with f3: session = st.multiselect("Khung giờ:", df['TimeOfDay'].unique(), default=df['TimeOfDay'].unique())
    
    # Lọc DataFrame
    mask = (df['FullDate'].dt.date >= start_date) & (df['FullDate'].dt.date <= end_date) & (df['TimeOfDay'].isin(session))
    df_f = df.loc[mask]
    st.markdown("---")

    # --- B. KPI CARDS (Hiển thị tóm tắt 4 chỉ số chính) ---
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.metric("Công suất thực (Active)", f"{df_f['Active_Power'].sum()/1000:,.1f} MWh", "Tiêu thụ chính")
    with k2: st.metric("Hao phí (Reactive)", f"{df_f['Reactive_Power'].sum()/1000:,.1f} kVarh", "Tổn thất", delta_color="inverse")
    with k3: st.metric("Điện áp TB (Voltage)", f"{df_f['Voltage'].mean():,.1f} V", f"{df_f['Voltage'].mean()-220:.1f} V lệch chuẩn")
    with k4: st.metric("Cường độ dòng (Intensity)", f"{df_f['Intensity'].mean():,.1f} A", "Dòng điện")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- C. BIỂU ĐỒ TƯƠNG TÁC (INTERACTIVE CHART) ---
    # Đây là phần bạn yêu cầu: Chọn thông tin để visualize
    
    c_chart_left, c_chart_right = st.columns([2, 1])

    with c_chart_left:
        st.markdown("#### 📈 Phân tích Biến động theo Thời gian")
        
        # 1. MENU CHỌN CHỈ SỐ (Dùng st.radio dạng ngang cho đẹp)
        metric_choice = st.radio(
            "Chọn thông tin cần hiển thị:",
            ["Active Power (Công suất)", "Voltage (Điện áp)", "Intensity (Cường độ)", "Reactive Power (Hao phí)"],
            horizontal=True
        )
        
        # 2. Cấu hình màu sắc & Đơn vị tương ứng với lựa chọn
        config = {
            "Active Power (Công suất)":     {"col": "Active_Power",   "color": "#e74c3c", "unit": "kW"},
            "Voltage (Điện áp)":            {"col": "Voltage",        "color": "#f1c40f", "unit": "V"},
            "Intensity (Cường độ)":         {"col": "Intensity",      "color": "#3498db", "unit": "A"},
            "Reactive Power (Hao phí)":     {"col": "Reactive_Power", "color": "#9b59b6", "unit": "kVar"}
        }
        
        sel_cfg = config[metric_choice]
        
        # 3. Vẽ biểu đồ dựa trên lựa chọn
        fig_dyn, ax = plt.subplots(figsize=(10, 4))
        
        # Gom nhóm theo ngày
        daily_data = df_f.groupby('FullDate')[sel_cfg['col']].mean().reset_index()
        
        # Vẽ Area Chart (Vùng màu)
        ax.fill_between(daily_data['FullDate'], daily_data[sel_cfg['col']], color=sel_cfg['color'], alpha=0.2)
        sns.lineplot(data=daily_data, x='FullDate', y=sel_cfg['col'], ax=ax, color=sel_cfg['color'], linewidth=2.5)
        
        ax.set_ylabel(sel_cfg['unit'])
        ax.set_xlabel("")
        ax.set_title(f"Diễn biến {metric_choice}", fontsize=10, weight='bold')
        sns.despine()
        st.pyplot(fig_dyn)

    with c_chart_right:
        st.markdown("#### Cơ cấu Tiêu thụ")
        # Sub-metering Pie Chart
        sums = [df_f['Sub_Kitchen'].sum(), df_f['Sub_Laundry'].sum(), df_f['Sub_AC'].sum()]
        labels = ['Bếp', 'Giặt là', 'Điều hòa']
        colors = ['#ff7675', '#74b9ff', '#55efc4']
        
        fig_pie, ax_pie = plt.subplots(figsize=(5, 5))
        wedges, texts, autotexts = ax_pie.pie(
            sums, labels=labels, colors=colors, autopct='%1.0f%%', 
            startangle=90, pctdistance=0.8, 
            wedgeprops=dict(width=0.4, edgecolor='white')
        )
        plt.setp(autotexts, size=11, weight="bold", color="white")
        st.pyplot(fig_pie)
        
        # Ghi chú thêm
        st.info(f"Tổng điện năng thiết bị đo được: **{(sum(sums)/1000):,.1f} MWh**")

    # --- D. HÀNH VI TIÊU DÙNG (STACKED CHART) ---
    st.markdown("####  Hành vi sử dụng thiết bị theo giờ")
    hourly = df_f.groupby('Hour')[['Sub_Kitchen', 'Sub_Laundry', 'Sub_AC']].mean().reset_index()
    
    fig_stack, ax_stack = plt.subplots(figsize=(12, 3))
    ax_stack.stackplot(
        hourly['Hour'], 
        hourly['Sub_Kitchen'], hourly['Sub_Laundry'], hourly['Sub_AC'],
        labels=['Bếp', 'Giặt là', 'Điều hòa'],
        colors=['#ff7675', '#74b9ff', '#55efc4'], alpha=0.8
    )
    ax_stack.set_xlim(0, 23)
    ax_stack.set_xlabel("Giờ trong ngày (0h - 23h)")
    ax_stack.legend(loc='upper left', ncol=3)
    sns.despine()
    st.pyplot(fig_stack)

# ================= TAB 2: DỰ BÁO AI (Giữ nguyên tính năng) =================
with tab_ai:
    st.markdown("### 🤖 Trung tâm Dự báo & Kịch bản")
    
    # 1. CẤU HÌNH & TRAIN
    with st.expander("⚙️ Cấu hình Mô hình", expanded=False):
        c_train1, c_train2 = st.columns([1, 3])
        with c_train1:
            ai_model = st.selectbox("Thuật toán:", ["Neural Network (MLP)", "XGBoost", "Linear Regression"])
        with c_train2:
            st.write("") 
            st.write("")
            if st.button("🔄 Huấn luyện lại từ DWH", use_container_width=True):
                with st.spinner('Đang Training...'):
                    # (Logic Train như cũ)
                    scaler = MinMaxScaler((0, 1))
                    data = scaler.fit_transform(df[['Active_Power']])
                    SEQ = 48
                    X, y = [], []
                    for i in range(len(data) - SEQ):
                        X.append(data[i:(i+SEQ)])
                        y.append(data[i+SEQ])
                    X, y = np.array(X), np.array(y)
                    X = X.reshape(X.shape[0], X.shape[1])
                    split = int(len(X)*0.9)
                    
                    if "Neural" in ai_model:
                        model = MLPRegressor(hidden_layer_sizes=(100,50), max_iter=500, random_state=42)
                    elif "XGBoost" in ai_model:
                        model = xgb.XGBRegressor(n_estimators=500, max_depth=6)
                    else:
                        model = LinearRegression()
                    
                    model.fit(X[:split], y[:split])
                    st.session_state['ai_pkg'] = {'model': model, 'scaler': scaler, 'name': ai_model}
                    st.success(f"Đã cập nhật mô hình: {ai_model}")

    st.markdown("---")

    # 2. FILE UPLOAD & PREDICT
    c_up, c_res = st.columns([1, 2])
    with c_up:
        st.markdown("#### 📂 Upload dữ liệu mới")
        st.caption("Tải file log (.txt/.csv) để dự báo 24h tiếp theo.")
        uploaded_file = st.file_uploader("Chọn file", type=['txt', 'csv'], label_visibility="collapsed")
        
        if uploaded_file and st.button("⚡ Chạy Dự Báo", type="primary"):
            if 'ai_pkg' not in st.session_state:
                st.error("Vui lòng Huấn luyện mô hình trước!")
            else:
                try:
                    with st.spinner('Đang phân tích...'):
                        raw = pd.read_csv(uploaded_file, sep=';', na_values=['?'], low_memory=False)
                        raw.dropna(inplace=True)
                        raw['Active'] = raw['Global_active_power'].astype(float)
                        raw['DT'] = pd.to_datetime(raw['Date'] + ' ' + raw['Time'], dayfirst=True)
                        hourly = raw.set_index('DT').resample('H')['Active'].sum()
                        
                        if len(hourly) < 48:
                            st.error("Dữ liệu < 48 giờ.")
                        else:
                            pkg = st.session_state['ai_pkg']
                            last_48 = hourly.tail(48).values.reshape(-1, 1)
                            scaled = pkg['scaler'].transform(last_48).reshape(1, 48)
                            
                            preds = []
                            curr = scaled
                            for _ in range(24):
                                p = pkg['model'].predict(curr)
                                val = p[0] if "Neural" not in pkg['name'] else p
                                preds.append(val)
                                curr = np.append(curr[:, 1:], np.array([[float(val)]]), axis=1)
                            
                            final_preds = pkg['scaler'].inverse_transform(np.array(preds).reshape(-1,1))
                            st.session_state['forecast'] = {'hist': last_48, 'pred': final_preds}
                except Exception as e:
                    st.error(f"Lỗi file: {e}")

    with c_res:
        st.markdown("#### 📊 Kết quả Dự báo")
        if 'forecast' in st.session_state:
            res = st.session_state['forecast']
            st.info(f"Tổng tải dự kiến 24h tới: **{np.sum(res['pred']):,.2f} kW**")
            
            fig_ai, ax_ai = plt.subplots(figsize=(10, 4))
            x_hist = np.arange(0, 48)
            x_fut = np.arange(48, 72)
            
            ax_ai.plot(x_hist, res['hist'], color='#95a5a6', label='Lịch sử (48h)')
            ax_ai.plot(x_fut, res['pred'], color='#2ecc71', label='Dự báo (24h)', marker='o')
            ax_ai.fill_between(x_fut, res['pred'].flatten(), color='#2ecc71', alpha=0.1)
            ax_ai.legend()
            sns.despine()
            st.pyplot(fig_ai)
        else:
            st.info("👈 Tải file dữ liệu bên trái để xem kết quả")