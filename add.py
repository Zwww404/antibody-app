import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="免疫流式抗体库存管理系统", page_icon="🔬", layout="wide")

# --- 1. 顶级 UI 与字体优化 (CSS 注入) ---
st.markdown("""
    <style>
    /* 引入 Google 顶级网页字体 (Inter & Noto Sans SC) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Noto+Sans+SC:wght@400;500;600;700&display=swap');
    
    /* 全局字体与颜色 */
    html, body, [class*="css"] {
        font-family: 'Inter', 'Noto Sans SC', sans-serif !important;
        color: #1e293b;
    }
    
    /* 隐藏 Streamlit 默认的水印和菜单，更像独立软件 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 美化左侧输入表单 (圆角、阴影、背景) */
    [data-testid="stForm"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.025);
    }
    
    /* 确认添加按钮的高级渐变与悬浮动效 */
    [data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        letter-spacing: 0.5px;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    [data-testid="stFormSubmitButton"] > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.4);
        border-color: transparent;
        color: white;
    }
    
    /* 标题层级美化 */
    h1 { font-weight: 700 !important; color: #0f172a !important; }
    h2, h3 { font-weight: 600 !important; color: #1e293b !important; }
    </style>
""", unsafe_allow_html=True)

# 居中主标题
st.markdown("<h1 style='text-align: center; margin-bottom: 2rem;'>🔬 肿瘤免疫流式抗体库存系统</h1>", unsafe_allow_html=True)

DATA_FILE = "antibodies.csv"
# 后台标准英文字段，防止重复列
EXPECTED_COLS = ["Target", "Fluorophore", "Localization", "Clone", "Box_Location", "Status"]

# --- 2. 数据读取与自动修复机制 ---
def load_data():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=EXPECTED_COLS)
        df.to_csv(DATA_FILE, index=False)
        return df
    
    df = pd.read_csv(DATA_FILE)
    
    # 【关键修复】处理表头不一致导致的重复列问题
    rename_map = {
        "靶点 (Target)": "Target",
        "靶点(Target)": "Target",
        "荧光素": "Fluorophore",
        "荧光素 (Fluorophore)": "Fluorophore",
        "抗原位置": "Localization",
        "克隆号": "Clone",
        "存放位置": "Box_Location",
        "物理位置 (Location)": "Box_Location",
        "状态": "Status"
    }
    df = df.rename(columns=rename_map)
    
    # 补齐缺失列，过滤由于之前 Bug 产生的多余乱码列
    for col in EXPECTED_COLS:
        if col not in df.columns:
            df[col] = ""
    
    df = df[EXPECTED_COLS]
    df = df.fillna("") # 填充 NaN 以免表格报错
    return df

if 'df' not in st.session_state:
    st.session_state.df = load_data()

def save_data(df):
    df.to_csv(DATA_FILE, index=False)
    st.session_state.df = df

# --- 3. 页面核心布局 ---
col_left, col_right = st.columns([1, 2.5], gap="large")

# ==================== 左侧：美化后的控制台 ====================
with col_left:
    st.markdown("### ➕ 添加新抗体")
    
    with st.form("add_antibody_form", clear_on_submit=True):
        new_target = st.text_input("靶点 (Target) *", placeholder="例: CD4")
        new_fluor = st.text_input("荧光素 (Fluorophore) *", placeholder="例: BV421")
        new_loc = st.selectbox("抗原位置 (Localization)", ["Surface (表面)", "Intracellular (胞内)", "Intranuclear (核内)"])
        new_clone = st.text_input("克隆号 (Clone)", placeholder="例: RM4-5")
        new_box = st.text_input("物理位置 (Location)", placeholder="例: 4℃-Box1-A2")
        new_status = st.selectbox("状态 (Status)", ["In Use (使用中)", "Low (快用完)", "Empty (待采购)", "Expired (已过期)"])
        
        st.write("") # 使用空行挤占空间，让布局更透气
        submitted = st.form_submit_button("确认录入系统", use_container_width=True)
        
        if submitted:
            if not new_target or not new_fluor:
                st.error("操作失败：请务必填写【靶点】和【荧光素】！")
            else:
                new_row = pd.DataFrame([[new_target, new_fluor, new_loc, new_clone, new_box, new_status]], columns=EXPECTED_COLS)
                updated_df = pd.concat([new_row, st.session_state.df], ignore_index=True)
                save_data(updated_df)
                st.success(f"✅ 成功添加 {new_target} ({new_fluor})")
                st.rerun()

    st.write("")
    st.markdown("### 📥 数据备份")
    csv = st.session_state.df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="下载最新 CSV 备份",
        data=csv,
        file_name='抗体库存备份.csv',
        mime='text/csv',
        use_container_width=True
    )

# ==================== 右侧：强大的主面板 ====================
with col_right:
    st.markdown("### 📊 库存总览与快速筛选")
    
    # --- 全新快速筛选组件 ---
    f1, f2, f3 = st.columns([1.5, 1.5, 2])
    search_target = f1.text_input("🔍 搜靶点 (如: CD8)", "")
    search_fluor = f2.text_input("🔍 搜荧光素 (如: APC)", "")
    filter_loc = f3.selectbox("🎯 筛选抗原位置", ["全部", "Surface (表面)", "Intracellular (胞内)", "Intranuclear (核内)"])
    
    # --- 数据过滤核心逻辑 ---
    df = st.session_state.df.copy()
    mask = pd.Series(True, index=df.index)
    
    if search_target:
        mask &= df['Target'].str.contains(search_target, case=False, na=False)
    if search_fluor:
        mask &= df['Fluorophore'].str.contains(search_fluor, case=False, na=False)
    if filter_loc != "全部":
        mask &= (df['Localization'] == filter_loc)
        
    filtered_df = df[mask]
    is_filtered = not mask.all()

    st.caption("✨ 提示：双击表格内容即可直接修改。选中行最左侧方框并按 `Delete` 键即可删除。")

    # --- 渲染高清交互表格 ---
    edited_df = st.data_editor(
        filtered_df,
        use_container_width=True,
        # 聪明的设计：如果正在使用筛选功能，则锁定新增行，防止数据保存时索引错乱；如果不筛选，则允许无限向下添加。
        num_rows="fixed" if is_filtered else "dynamic",
        height=600,
        column_config={
            "Target": st.column_config.TextColumn("🎯 靶点 (Target)"),
            "Fluorophore": st.column_config.TextColumn("🌈 荧光素"),
            "Localization": st.column_config.SelectboxColumn("📍 位置", options=["Surface (表面)", "Intracellular (胞内)", "Intranuclear (核内)"]),
            "Clone": st.column_config.TextColumn("🏷️ 克隆号"),
            "Box_Location": st.column_config.TextColumn("📦 存放位置"),
            "Status": st.column_config.SelectboxColumn("🚥 状态", options=["In Use (使用中)", "Low (快用完)", "Empty (待采购)", "Expired (已过期)"])
        },
        hide_index=True
    )

    # --- 丝滑无感的保存逻辑 ---
    if not edited_df.equals(filtered_df):
        if is_filtered:
            # 如果在筛选状态下修改了内容，自动根据行号替换原表格内容
            df.update(edited_df)
            save_data(df)
        else:
            # 如果没有筛选（包含在底部添加新行或删除旧行），直接覆盖保存
            save_data(edited_df)
        st.rerun()
