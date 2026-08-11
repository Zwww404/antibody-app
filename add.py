import streamlit as st
import pandas as pd
import os
import io
from github import Github
from datetime import datetime, timedelta

st.set_page_config(page_title="抗体管理系统", page_icon="🔬", layout="wide")
# ==========================================
# 🔐 1. 旗舰级高级密码验证 UI (青绿定制版)
# ==========================================
LAB_PASSWORD = "wangxuefeng"

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* 强制整个网页大背景变为柔和的亮色 */
        [data-testid="stAppViewContainer"] {
            background-color: #f0f4f8 !important; 
        }
        
        .stApp { font-family: 'Inter', sans-serif; }
        .block-container { padding-top: 22vh !important; }

        .login-title {
            text-align: center;
            font-weight: 700;
            font-size: 2.2rem;
            margin-bottom: 0.5rem;
            letter-spacing: 1px;
            color: #0f172a !important; 
        }
        .login-subtitle {
            text-align: center;
            font-size: 1rem;
            margin-bottom: 2rem;
            font-weight: 400;
            color: #64748b !important; 
        }

        /* 表单框样式 */
        [data-testid="stForm"] {
            background-color: #ffffff !important; 
            border: 1px solid #e2e8f0 !important;
            border-radius: 20px;
            padding: 40px 30px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
        }
        
        /* 💥 修复 1：彻底隐藏输入框点击后自带的提示小字 (Press Enter to submit) */
        [data-testid="InputInstructions"] {
            display: none !important;
        }

        /* 💥 修复 2：访问密码 字体加粗并放大 */
        [data-testid="stForm"] label, [data-testid="stForm"] label p {
            color: #1e293b !important;
            font-weight: 800 !important; 
            font-size: 1.2rem !important; /* 强制拉大字号 */
            margin-bottom: 0.4rem !important;
        }
        
        /* 密码输入框清爽样式，同步修改聚焦时的边框颜色为 #4ecca3 */
        [data-testid="stTextInput"] input {
            border-radius: 10px;
            padding: 14px 16px;
            background-color: #f8fafc !important;
            border: 1px solid #cbd5e1 !important;
            color: #0f172a !important;
            font-size: 1.1rem;
        }
        [data-testid="stTextInput"] input:focus {
            border-color: #4ecca3 !important; 
            box-shadow: 0 0 0 2px rgba(78, 204, 163, 0.25) !important;
        }
        
        /* 💥 修复 3：定制解锁按钮颜色、字体加粗放大 */
        [data-testid="stForm"] .stButton { margin-top: 25px; }
        [data-testid="stFormSubmitButton"] button {
            background-color: #4ecca3 !important; /* 更改为青绿色 */
            border: none !important;
            border-radius: 10px !important;
            transition: all 0.3s ease !important;
        }
        [data-testid="stFormSubmitButton"] button p {
            font-size: 1.25rem !important; /* 放大字体 */
            font-weight: 700 !important;   /* 加粗字体 */
            color: #ffffff !important;
        }
        [data-testid="stFormSubmitButton"] button:hover {
            background-color: #45b894 !important; /* 悬浮时颜色微调加深 */
            transform: translateY(-2px);
            box-shadow: 0 8px 15px -5px rgba(78, 204, 163, 0.4) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='login-title'>🔬 抗体管理系统</div>", unsafe_allow_html=True)
    st.markdown("<div class='login-subtitle'>安全验证 · 请输入课题组密码</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("login_form"):
            user_input = st.text_input("密码", type="password", placeholder="Press Enter to unlock")
            
            # 按钮抛弃原生 primary 属性，全靠 CSS 定制颜色
            submit_button = st.form_submit_button("登录系统", use_container_width=True)
            
            if submit_button:
                if user_input == LAB_PASSWORD:
                    st.session_state["logged_in"] = True
                    st.rerun()
                else:
                    st.error("❌ 密码错误，请重试。")
    
    st.stop()
# ==========================================
# 🔬 2. 核心 UI 与逻辑
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Noto+Sans+SC:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', 'Noto Sans SC', sans-serif !important; color: #1e293b; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stForm"] { background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 25px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.025); }
    [data-testid="stFormSubmitButton"] > button { background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; border: none; border-radius: 8px; font-weight: 600; padding: 0.5rem 1rem; transition: all 0.3s ease; }
    [data-testid="stFormSubmitButton"] > button:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.4); }
    h1 { font-weight: 700 !important; color: #0f172a !important; }
    h2, h3 { font-weight: 600 !important; color: #1e293b !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; margin-bottom: 2rem;'>🔬 流式抗体管理系统</h1>", unsafe_allow_html=True)

DATA_FILE = "antibodies.csv"
EXPECTED_COLS = ["Target", "Fluorophore", "Localization", "Clone", "Box_Location", "Status"]

def load_data():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=EXPECTED_COLS)
        df.to_csv(DATA_FILE, index=False)
        return df
    
    df = pd.read_csv(DATA_FILE)
    rename_map = {
        "靶点 (Target)": "Target", "靶点(Target)": "Target",
        "荧光素": "Fluorophore", "荧光素 (Fluorophore)": "Fluorophore",
        "抗原位置": "Localization", "克隆号": "Clone",
        "存放位置": "Box_Location", "物理位置 (Location)": "Box_Location",
        "状态": "Status"
    }
    df = df.rename(columns=rename_map)
    df = df.loc[:, ~df.columns.duplicated()]
    
    for col in EXPECTED_COLS:
        if col not in df.columns:
            df[col] = ""
    df = df[EXPECTED_COLS].fillna("")
    return df

if 'df' not in st.session_state:
    st.session_state.df = load_data()

# ==========================================
# ☁️ 3. 核心升级：GitHub 每日按文件夹自动回传
# ==========================================
def save_data(df):
    st.session_state.df = df
    df.to_csv(DATA_FILE, index=False)
    
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_content = csv_buffer.getvalue()
    
    try:
        token = st.secrets["GITHUB_TOKEN"]
        repo_name = st.secrets["GITHUB_REPO"]
        
        g = Github(token)
        repo = g.get_repo(repo_name)
        
        # 1. 覆盖主文件 (供系统每次重启时读取)
        try:
            contents = repo.get_contents(DATA_FILE)
            repo.update_file(contents.path, "🤖 主数据实时覆盖更新", csv_content, contents.sha)
        except:
            repo.create_file(DATA_FILE, "🤖 初始化主数据", csv_content)
        
        # 2. 建立带日期的每日快照备份 (存放在 backups 文件夹下)
        # 注意：Streamlit 云端服务器默认是 UTC 时间，我们需要 +8 小时转换为北京时间
        beijing_time = datetime.utcnow() + timedelta(hours=8)
        date_str = beijing_time.strftime("%Y-%m-%d")
        
        # 设定备份路径：系统会自动生成 backups 文件夹
        backup_path = f"backups/antibodies_{date_str}.csv"
        
        try:
            # 如果今天已经有备份了，就覆盖更新今天的文件
            backup_contents = repo.get_contents(backup_path)
            repo.update_file(backup_contents.path, f"🤖 每日快照更新 ({date_str})", csv_content, backup_contents.sha)
        except:
            # 如果是今天第一次修改，则新建当天的备份文件
            repo.create_file(backup_path, f"🤖 生成今日快照 ({date_str})", csv_content)
            
        st.toast("✅ 数据与每日快照已永久保存至 GitHub！", icon="☁️")
        
    except Exception as e:
        st.error(f"⚠️ 云端同步失败！错误信息: {e}")

# ==========================================
# 后续界面渲染逻辑 (保持不变)
# ==========================================
col_left, col_right = st.columns([1, 2.5], gap="large")

with col_left:
    st.markdown("### ➕ 添加新抗体")
    with st.form("add_antibody_form", clear_on_submit=True):
        new_target = st.text_input("靶点 (Target) *", placeholder="例: CD4")
        new_fluor = st.text_input("荧光素 (Fluorophore) *", placeholder="例: BV421")
        new_loc = st.selectbox("抗原位置 (Localization)", ["Surface (表面)", "Intracellular (胞内)", "Intranuclear (核内)"])
        new_clone = st.text_input("克隆号 (Clone)", placeholder="例: RM4-5")
        new_box = st.text_input("物理位置 (Location)", placeholder="例: 4℃-Box1-A2")
        new_status = st.selectbox("状态 (Status)", ["In Use (使用中)", "Low (快用完)", "Empty (待采购)", "Expired (已过期)"])
        
        st.write("")
        submitted = st.form_submit_button("确认录入系统", use_container_width=True)
        
        if submitted:
            if not new_target or not new_fluor:
                st.error("操作失败：请务必填写【靶点】和【荧光素】！")
            else:
                new_row = pd.DataFrame([[new_target, new_fluor, new_loc, new_clone, new_box, new_status]], columns=EXPECTED_COLS)
                updated_df = pd.concat([new_row, st.session_state.df], ignore_index=True)
                save_data(updated_df)
                st.rerun()
    st.write("")
# ==========================================
    # 🔄 新增：数据实时同步模块
    # ==========================================
    st.markdown("### 🔄 团队数据同步")
    if st.button("获取云端最新库存", use_container_width=True):
        st.session_state.df = load_data()
        st.toast("✅ 已成功同步团队最新数据！", icon="🔄")
        st.rerun()

    st.write("")
# 🚨 新增：灾备模块 (下载与覆盖恢复)
# 💎 为下载按钮单独注入的高级 CSS 样式
    st.markdown("""
        <style>
        /* 针对下载按钮的专属美化 */
        [data-testid="stDownloadButton"] button {
            background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%) !important;
            border: 1px solid #cbd5e1 !important;
            color: #334155 !important;
            border-radius: 12px !important;
            padding: 10px 0 !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.04), 0 1px 2px -1px rgba(0, 0, 0, 0.02) !important;
        }
        [data-testid="stDownloadButton"] button p {
            font-weight: 600 !important;
            font-size: 1.05rem !important;
            letter-spacing: 0.5px !important;
        }
        /* 鼠标悬浮时的高级青绿交互动效 */
        [data-testid="stDownloadButton"] button:hover {
            background: #ffffff !important;
            border-color: #4ecca3 !important;
            color: #4ecca3 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 10px 15px -3px rgba(78, 204, 163, 0.25), 0 4px 6px -2px rgba(78, 204, 163, 0.1) !important;
        }
        </style>
    """, unsafe_allow_html=True)
    st.write("")
    st.markdown("### 📥 数据备份与恢复")
    csv = st.session_state.df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="下载最新 CSV 备份",
        data=csv,
        file_name='抗体库存备份.csv',
        mime='text/csv',
        use_container_width=True
    )
    st.markdown("<p style='font-size:0.9rem; color:#64748b; margin-top:20px; margin-bottom:5px;'>⚠️ 数据恢复 (管理员上传覆盖)</p>", unsafe_allow_html=True)
    # st.markdown("<p style='font-size:0.9rem; color:#64748b; margin-top:15px; margin-bottom:5px;'>⚠️ 数据恢复 (仅限管理员上传覆盖)</p>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("导入本地 CSV 文件恢复库存", type=["csv"], label_visibility="collapsed")
    
    if uploaded_file is not None:
        if st.button("🚨 确认使用此文件覆盖全库数据", type="primary", use_container_width=True):
            try:
                uploaded_df = pd.read_csv(uploaded_file)
                # 严格按照规范重置表头，防止传入脏数据
                for col in EXPECTED_COLS:
                    if col not in uploaded_df.columns:
                        uploaded_df[col] = ""
                uploaded_df = uploaded_df[EXPECTED_COLS].fillna("")
                
                # 覆盖保存并触发云端回传
                save_data(uploaded_df)
                st.success("✅ 数据已成功恢复，并同步至云端！")
                st.rerun()
            except Exception as e:
                st.error(f"❌ 文件读取失败，请确保上传的是标准备份文件。错误: {e}")
# 💎 左侧专属开发者控制台铭牌
    st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(78,204,163,0.08) 0%, rgba(78,204,163,0.02) 100%); border: 1px solid rgba(78,204,163,0.3); padding: 22px; border-radius: 16px; margin-top: 2rem; box-shadow: 0 4px 15px -5px rgba(0,0,0,0.05);">
            <p style="margin: 0; color: #64748b; font-size: 0.8rem; font-weight: 700; letter-spacing: 1.5px;">SYSTEM ARCHITECT</p>
            <p style="margin: 5px 0 0 0; color: #4ecca3; font-size: 1.6rem; font-weight: 800;">ZJW <span style="font-size: 1.2rem;"> </span></p>
            <p style="margin: 5px 0 0 0; color: #94a3b8; font-size: 0.85rem;">Flow Cytometry Inventory V1.0</p>
        </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown("### 📊 库存总览与快速筛选")
    f1, f2, f3 = st.columns([1.5, 1.5, 2])
    search_target = f1.text_input("🔍 搜靶点 (如: CD8)", "")
    search_fluor = f2.text_input("🔍 搜荧光素 (如: APC)", "")
    filter_loc = f3.selectbox("🎯 筛选抗原位置", ["全部", "Surface (表面)", "Intracellular (胞内)", "Intranuclear (核内)"])
    
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

    edited_df = st.data_editor(
        filtered_df,
        use_container_width=True,
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

    if not edited_df.equals(filtered_df):
        if is_filtered:
            df.update(edited_df)
            save_data(df)
        else:
            save_data(edited_df)
        st.rerun()

