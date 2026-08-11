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
# ==========================================
# ==========================================
# 📊 重新定义列顺序：克隆号垫底，体积加入
# ==========================================
EXPECTED_COLS = ["Target", "Fluorophore", "Localization", "Volume", "Box_Location", "Status", "Clone"]

def load_data():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=EXPECTED_COLS)
        df.to_csv(DATA_FILE, index=False)
        return df
    
    df = pd.read_csv(DATA_FILE)
    # 兼容中英文旧表头
    rename_map = {
        "靶点 (Target)": "Target", "靶点(Target)": "Target",
        "荧光素": "Fluorophore", "荧光素 (Fluorophore)": "Fluorophore",
        "抗原位置": "Localization", "克隆号": "Clone",
        "存放位置": "Box_Location", "物理位置 (Location)": "Box_Location",
        "状态": "Status", "体积": "Volume", "余量": "Volume"
    }
    df = df.rename(columns=rename_map)
    df = df.loc[:, ~df.columns.duplicated()]
    
    # 🌟 智能补全缺失列（全部默认给空白 ""，不再强塞 100）
    for col in EXPECTED_COLS:
        if col not in df.columns:
            df[col] = ""
                
    # 强制重新排列列顺序
    df = df[EXPECTED_COLS]
    
    # 尝试将 Volume 转为数字。如果是空白或无效字符，会变成 NaN
    df["Volume"] = pd.to_numeric(df["Volume"], errors='coerce')
    
    # 🚀 极其关键的修复：
    # 先将整个表格转为包容所有类型的 object，然后再用空白字符串填充 NaN，
    # 这样就能完美避开 Pandas 严苛的数据类型检查！
    df = df.astype(object).fillna("")
    
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
# ==========================================
# 🚀 4. 全局界面渲染与左右分栏逻辑
# ==========================================

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Noto+Sans+SC:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', 'Noto Sans SC', sans-serif !important; color: #1e293b; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 核心表单与提交按钮美化 */
    [data-testid="stForm"] { background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 25px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.025); }
    [data-testid="stFormSubmitButton"] > button { background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; border: none; border-radius: 8px; font-weight: 600; padding: 0.5rem 1rem; transition: all 0.3s ease; }
    [data-testid="stFormSubmitButton"] > button:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.4); }
    
    /* 标题颜色统一 */
    h1 { font-weight: 700 !important; color: #0f172a !important; }
    h2, h3 { font-weight: 600 !important; color: #1e293b !important; }

    /* ========================================================= */
    /* 💎 双按钮高级科技 UI (已去除强制位移，完美兼容手机端) */
    /* ========================================================= */
    div[data-testid="stButton"] > button, 
    div[data-testid="stDownloadButton"] > button {
        width: 100% !important;
        background: linear-gradient(135deg, #ffffff 0%, #f0fdf9 100%) !important;
        border: 1px solid #4ecca3 !important;
        border-radius: 12px !important;
        padding: 10px 0 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 6px -1px rgba(78, 204, 163, 0.1) !important;
    }
    div[data-testid="stButton"] > button p, 
    div[data-testid="stDownloadButton"] > button p {
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        color: #1e293b !important;
        transition: all 0.3s ease !important;
        letter-spacing: 0.5px !important;
    }
    
    /* 【获取云端数据】悬浮青绿光晕 */
    div[data-testid="stButton"] > button:hover {
        background: linear-gradient(135deg, #4ecca3 0%, #45b894 100%) !important;
        border-color: #45b894 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 15px -3px rgba(78, 204, 163, 0.3) !important;
    }
    div[data-testid="stButton"] > button:hover p {
        color: #ffffff !important;
    }
    
    /* 【下载表格数据】悬浮 #0094D9 科技蓝填充 */
    div[data-testid="stDownloadButton"] > button:hover {
        background: linear-gradient(135deg, #0094D9 0%, #007bb5 100%) !important;
        border-color: #007bb5 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 15px -3px rgba(0, 148, 217, 0.3) !important;
    }
    div[data-testid="stDownloadButton"] > button:hover p {
        color: #ffffff !important;
    }
    
    /* 点击下沉动效 */
    div[data-testid="stButton"] > button:active,
    div[data-testid="stDownloadButton"] > button:active {
        transform: translateY(1px) !important;
    }
    
    /* 🚀 专属定制：让脱离表单的 Primary 按钮保持纯正的科技蓝！ */
    /* ========================================================= */
    div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.2) !important;
    }
    div[data-testid="stButton"] > button[kind="primary"] p {
        color: white !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
    }
    div[data-testid="stButton"] > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.4) !important;
    }
    </style>
""", unsafe_allow_html=True)


col_left, col_right = st.columns([1, 2.5], gap="large")

with col_left:
    # 1. 顶部：表格数据同步与下载模块
    st.markdown("### 🔄 表格数据同步与下载")
    if st.button("同步最新数据", use_container_width=True):
        st.session_state.df = load_data()
        # 👑 强刷信号：强迫右侧表格更新
        st.session_state.table_key = st.session_state.get("table_key", 0) + 1
        st.toast("✅ 已成功同步表格最新数据！", icon="🔄")
        st.rerun()

    csv = st.session_state.df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="下载表格数据",
        data=csv,
        file_name='抗体库存备份.csv',
        mime='text/csv',
        use_container_width=True
    )

    st.markdown("<div style='margin: 18px 0;'></div>", unsafe_allow_html=True)

    # 2. 中部：添加新抗体表单
    st.markdown("### ➕ 添加新抗体")
    with st.form("add_antibody_form", clear_on_submit=True):
        new_target = st.text_input("靶点 (Target) *", placeholder="例: CD4")
        new_fluor = st.text_input("荧光素 (Fluorophore) *", placeholder="例: BV421")
        new_loc = st.selectbox("抗原位置 (Localization)", ["Surface (表面)", "Intracellular (胞内)", "Intranuclear (核内)"])
        new_volume = st.number_input("初始体积 (Volume µL)", value=None, placeholder="可留空不填", min_value=0.0, step=10.0)
        new_box = st.text_input("物理位置 (Location)", placeholder="例: 4℃-Box1-A2")
        new_status = st.selectbox("状态 (Status)", ["In Use (使用中)", "Low (快用完)", "Empty (待采购)", "Expired (已过期)"])
        
        st.write("")
        submitted = st.form_submit_button("确认录入系统", use_container_width=True)
        
        if submitted:
            if not new_target or not new_fluor:
                st.error("操作失败：请务必填写【靶点】和【荧光素】！")
            else:
                vol_to_save = new_volume if new_volume is not None else ""
                new_row = pd.DataFrame([[new_target, new_fluor, new_loc, vol_to_save, new_box, new_status, ""]], columns=EXPECTED_COLS)
                updated_df = pd.concat([new_row, st.session_state.df], ignore_index=True)
                save_data(updated_df)
                st.session_state.table_key = st.session_state.get("table_key", 0) + 1
                st.rerun()

    st.markdown("<div style='margin: 15px 0;'></div>", unsafe_allow_html=True)

    # 3. 下方：实验 Panel 批量扣减引擎
    st.markdown("### 🧪 实验 Panel 批量扣减")
    
    # 🌟 常驻成功提示：再也不会一闪而过了
    if st.session_state.get("show_deduct_success", False):
        st.success("✅ 批量扣减成功，右侧库存状态已实时更新！")
        st.session_state.show_deduct_success = False
    
    with st.container():
        st.caption("按住 `Ctrl` 键可多选，一次性扣除本次实验消耗的抗体。")
        
        df_opts = st.session_state.df.copy()
        valid_opts = df_opts[df_opts["Target"] != ""]
        options = []
        for idx, row in valid_opts.iterrows():
            vol_str = f"剩 {row['Volume']} µL" if row['Volume'] != "" else "未记录体积"
            options.append(f"[{idx}] {row['Target']} - {row['Fluorophore']} ({vol_str})")
            
        if "deduct_key_counter" not in st.session_state:
            st.session_state.deduct_key_counter = 0
            
        selected_abs = st.multiselect(
            "🔍 选择本次实验使用的抗体", 
            options,
            key=f"deduct_selections_{st.session_state.deduct_key_counter}"
        )
        
        deduction_dict = {}
        if selected_abs:
            st.markdown("<p style='font-size: 0.9rem; font-weight: 600; color: #3b82f6; margin-top: 10px;'>👇 请设定单管消耗量 (µL)：</p>", unsafe_allow_html=True)
            for sel in selected_abs:
                name_display = sel.split("] ")[1].split(" (")[0]
                deduction_dict[sel] = st.number_input(f"💧 {name_display}", min_value=0.1, value=1.0, step=0.5, key=f"vol_{sel}_{st.session_state.deduct_key_counter}")
        
        st.write("")
        submitted_batch = st.button("确认扣减选定用量", type="primary", use_container_width=True)
        
        if submitted_batch:
            if not selected_abs:
                st.error("⚠️ 请先在上方选择你使用的抗体！")
            else:
                updated_df = st.session_state.df.copy()
                for sel in selected_abs:
                    idx = int(sel.split("]")[0].replace("[", ""))
                    consumed_vol = deduction_dict[sel]
                    old_vol = updated_df.at[idx, 'Volume']
                    
                    if pd.notna(old_vol) and old_vol is not None and str(old_vol).strip() != "":
                        try:
                            new_vol = max(0.0, float(old_vol) - float(consumed_vol))
                            updated_df.at[idx, 'Volume'] = new_vol
                            
                            if new_vol == 0.0:
                                updated_df.at[idx, 'Status'] = "Empty (待采购)"
                            elif new_vol <= 10.0 and updated_df.at[idx, 'Status'] == "In Use (使用中)":
                                updated_df.at[idx, 'Status'] = "Low (快用完)"
                        except (ValueError, TypeError):
                            pass
                            
                save_data(updated_df)
                st.session_state.deduct_key_counter += 1
                # 👑 强刷信号：扣减完成后强制右侧刷新！
                st.session_state.table_key = st.session_state.get("table_key", 0) + 1
                st.session_state.show_deduct_success = True
                st.rerun()

    st.markdown("<div style='margin: 15px 0;'></div>", unsafe_allow_html=True)

    # 4. 下方：数据恢复模块
    st.markdown("### ⚠️ 数据恢复")
    st.markdown("<p style='font-size:0.85rem; color:#64748b; margin-bottom:8px;'>管理员导入本地 CSV 文件覆盖全库</p>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("导入备份文件恢复库存", type=["csv"], label_visibility="collapsed")
    
    if uploaded_file is not None:
        if st.button("🚨 确认使用此文件覆盖全库数据", type="primary", use_container_width=True):
            try:
                uploaded_df = pd.read_csv(uploaded_file)
                for col in EXPECTED_COLS:
                    if col not in uploaded_df.columns:
                        uploaded_df[col] = ""
                uploaded_df = uploaded_df[EXPECTED_COLS].fillna("")
                save_data(uploaded_df)
                st.session_state.table_key = st.session_state.get("table_key", 0) + 1
                st.success("✅ 数据已成功恢复并同步至云端！")
                st.rerun()
            except Exception as e:
                st.error(f"❌ 读取失败。错误: {e}")

    st.markdown("<div style='margin: 25px 0;'></div>", unsafe_allow_html=True)

    # 专属系统架构师铭牌
   # st.markdown("""
     #   <div style='background: linear-gradient(135deg, #f0fdf9 0%, #e6fcf5 100%); border: 1.5px solid #4ecca3; border-radius: 16px; padding: 16px 20px; box-shadow: 0 4px 12px rgba(78, 204, 163, 0.12); position: relative; overflow: hidden;'>
      #      <p style='font-size: 0.7rem; font-weight: 800; color: #059669; text-transform: uppercase; letter-spacing: 2px; margin: 0 0 2px 0;'>System Architect</p>
        #    <h3 style='color: #047857; font-weight: 800; font-size: 1.4rem; margin: 0 0 2px 0; letter-spacing: 0.5px;'>ZJW</h3>
       #     <p style='font-size: 0.75rem; font-weight: 600; color: #64748b; margin: 0;'>Flow Cytometry Inventory V1.0</p>
      #  </div>
   # """, unsafe_allow_html=True)
    
    # 💎 最底部：ZJW 专属系统架构师铭牌 (GitHub 暗黑极客风 - 防报错顶格版)
    # ==========================================
    st.markdown("""
<div style='position: relative; background: #0f172a; border: 1px solid #1e293b; border-radius: 20px; padding: 24px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.3); overflow: hidden; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;'>
<!-- 科技网格背景 -->
<div style='position: absolute; inset: 0; background-image: radial-gradient(#334155 1px, transparent 1px); background-size: 16px 16px; opacity: 0.3;'></div>
<!-- 顶部状态栏 -->
<div style='display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; position: relative; z-index: 1;'>
<div style='display: flex; align-items: center; gap: 8px;'>
<div style='width: 8px; height: 8px; background: #10b981; border-radius: 50%; box-shadow: 0 0 10px rgba(16, 185, 129, 0.8);'></div>
<span style='font-size: 0.8rem; font-weight: 700; color: #94a3b8; letter-spacing: 0.15em; text-transform: uppercase;'>System Architect</span>
</div>
<span style='font-size: 1.2rem; opacity: 0.9;'>🧬</span>
</div>
<!-- 核心信息区 -->
<div style='position: relative; z-index: 1;'>
<h2 style='margin: 0 0 2px 0; font-size: 2rem; font-weight: 800; background: linear-gradient(135deg, #f8fafc, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -0.02em;'>ZJW</h2>
<p style='margin: 0 0 12px 0; font-size: 0.85rem; font-weight: 600; color: #64748b; letter-spacing: 0.05em;'>JIA WEI ZHANG</p>
<div style='display: flex; align-items: center; gap: 10px;'>
<span style='font-size: 0.85rem; font-weight: 600; color: #e2e8f0;'>Flow Cytometry Inventory</span>
<span style='padding: 2px 8px; background: rgba(16, 185, 129, 0.1); color: #10b981; border-radius: 12px; font-size: 0.65rem; font-weight: 800; border: 1px solid rgba(16, 185, 129, 0.2);'>V1.0</span>
</div>
</div>
<!-- 顶部极光线 -->
<div style='position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, transparent, #10b981, transparent);'></div>
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

    # ... 保留原本在 col_right 上方的过滤逻辑产生 filtered_df ...

    edited_df = st.data_editor(
        filtered_df,
        use_container_width=True,
        num_rows="fixed" if is_filtered else "dynamic",
        height=600,
        # 👑 接收强刷信号：只要左侧操作，这里的 Key 就会改变，彻底抛弃旧缓存！
        key=f"data_editor_{st.session_state.get('table_key', 0)}", 
        column_config={
            "Target": st.column_config.TextColumn("🎯 靶点 (Target)"),
            "Fluorophore": st.column_config.TextColumn("🌈 荧光素"),
            "Localization": st.column_config.SelectboxColumn("📍 位置", options=["Surface (表面)", "Intracellular (胞内)", "Intranuclear (核内)"]),
            "Volume": st.column_config.NumberColumn("💧 体积 (Volume)", min_value=0.0, format="%.1f"),
            "Box_Location": st.column_config.TextColumn("📦 存放位置"),
            "Status": st.column_config.SelectboxColumn("🚥 状态", options=["In Use (使用中)", "Low (快用完)", "Empty (待采购)", "Expired (已过期)"]),
            "Clone": st.column_config.TextColumn("🏷️ 克隆号")
        },
        hide_index=True
    )

    # 👑 究极防覆盖判定：全部转成字符串再对比，彻底无视 None/NaN/空白 转换导致的判定混乱！
    if not edited_df.fillna("").astype(str).equals(filtered_df.fillna("").astype(str)):
        if is_filtered:
            # 修改时，需调取最新基底数据 df 进行 update
            current_df = st.session_state.df.copy()
            current_df.update(edited_df)
            save_data(current_df)
        else:
            save_data(edited_df)
        # 表格内部修改也发送信号
        st.session_state.table_key = st.session_state.get("table_key", 0) + 1
        st.rerun()
