import streamlit as st
import pandas as pd
import os
import io
from github import Github
from datetime import datetime, timedelta

st.set_page_config(page_title="流式抗体管理系统", page_icon="🔬", layout="wide")

# ==========================================
# 🔐 1. 密码验证系统
# ==========================================
LAB_PASSWORD = "wangxuefeng"

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    # 专属登录页 CSS 注入
    st.markdown("""
        <style>
        /* 引入高级字体 */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        /* 隐藏顶部菜单和底部水印 */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* 全局背景微调，让毛玻璃更凸显 */
        .stApp {
            font-family: 'Inter', sans-serif;
        }

        /* 调整整体下移，居中视觉 */
        .block-container {
            padding-top: 12vh !important;
        }

        /* 标题排版美化 */
        .login-title {
            text-align: center;
            font-weight: 700;
            font-size: 2.2rem;
            margin-bottom: 0.5rem;
            letter-spacing: 1px;
        }
        .login-subtitle {
            text-align: center;
            color: #888888;
            font-size: 1rem;
            margin-bottom: 2rem;
            font-weight: 400;
        }

        /* 🌟 核心：毛玻璃悬浮表单框 */
        [data-testid="stForm"] {
            background: rgba(128, 128, 128, 0.05);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(128, 128, 128, 0.15);
            border-radius: 24px;
            padding: 40px 30px;
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.15);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        [data-testid="stForm"]:hover {
            box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.2);
        }

        /* 密码输入框美化 */
        [data-testid="stTextInput"] input {
            border-radius: 12px;
            padding: 14px 16px;
            border: 1px solid rgba(128, 128, 128, 0.2);
            background-color: rgba(255, 255, 255, 0.03);
            transition: all 0.3s ease;
            font-size: 1rem;
            letter-spacing: 2px;
        }
        [data-testid="stTextInput"] input:focus {
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.25);
            background-color: transparent;
        }

        /* 渐变解锁按钮美化 */
        [data-testid="stFormSubmitButton"] button {
            background: linear-gradient(135deg, #6366f1 0%, #3b82f6 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 12px;
            font-size: 1.05rem;
            font-weight: 600;
            letter-spacing: 1px;
            transition: all 0.3s ease;
            width: 100%;
            margin-top: 15px;
        }
        [data-testid="stFormSubmitButton"] button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px -6px rgba(59, 130, 246, 0.6);
            color: white;
            border: none;
        }
        </style>
    """, unsafe_allow_html=True)

    # 渲染精美标题
    st.markdown("<div class='login-title'>🔬 流式抗体管理系统</div>", unsafe_allow_html=True)
    st.markdown("<div class='login-subtitle'>安全验证 · 请输入课题组专属密钥</div>", unsafe_allow_html=True)
    
    # 将表单限制在中间列，控制宽度，使其看起来像一个精致的卡片
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("login_form"):
            st.markdown("<p style='font-weight: 600; margin-bottom: -10px;'>访问密码</p>", unsafe_allow_html=True)
            user_input = st.text_input("访问密码", type="password", placeholder="Press Enter to unlock", label_visibility="collapsed")
            submit_button = st.form_submit_button("解锁系统")
            
            if submit_button:
                if user_input == LAB_PASSWORD:
                    st.session_state["logged_in"] = True
                    st.rerun()
                else:
                    st.error("❌ 密钥效验失败，请重试。")
    
    # 拦截程序，密码正确前绝不加载主界面
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
    st.markdown("### 📥 数据备份")
    csv = st.session_state.df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="手动下载最新 CSV 备份",
        data=csv,
        file_name='抗体库存备份.csv',
        mime='text/csv',
        use_container_width=True
    )

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
