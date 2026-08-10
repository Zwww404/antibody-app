import streamlit as st
import pandas as pd
import os

# 1. 网页全局配置 (采用宽屏布局)
st.set_page_config(page_title="免疫流式抗体库存管理系统", page_icon="🔬", layout="wide")

# 隐藏 Streamlit 默认的右上角菜单和底部水印，让它看起来更像一个纯粹的软件
hide_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_style, unsafe_allow_html=True)

# 顶部标题
st.title("🔬 肿瘤免疫流式抗体库存管理系统")
st.markdown("---")

DATA_FILE = "antibodies.csv"

# 2. 初始化/加载数据函数
def load_data():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=["Target", "Fluorophore", "Localization", "Clone", "Box_Location", "Status"])
        df.to_csv(DATA_FILE, index=False)
    return pd.read_csv(DATA_FILE)

# 使用 session_state 保证数据状态实时刷新
if 'df' not in st.session_state:
    st.session_state.df = load_data()

def save_data(df):
    df.to_csv(DATA_FILE, index=False)
    st.session_state.df = df

# 3. 核心布局：划分左右两栏 (比例为 1 : 2.5)
col_left, col_right = st.columns([1, 2.5], gap="large")

# ==================== 左侧控制台 ====================
with col_left:
    st.subheader("➕ 添加新抗体")
    
    # 使用表单 (Form) 收集信息，点击确认后统一提交
    with st.form("add_antibody_form", clear_on_submit=True):
        new_target = st.text_input("靶点 (Target) *", placeholder="例如: CD8")
        new_fluor = st.text_input("荧光素 (Fluorophore) *", placeholder="例如: BV421")
        new_loc = st.selectbox("抗原位置 (Localization)", ["Surface (表面)", "Intracellular (胞内)", "Intranuclear (核内)"])
        new_clone = st.text_input("克隆号 (Clone)", placeholder="例如: 53-6.7")
        new_box = st.text_input("物理位置 (Location)", placeholder="例如: 4℃-Box1-A2")
        new_status = st.selectbox("状态 (Status)", ["In Use (使用中)", "Low (快用完)", "Empty (待采购)", "Expired (已过期)"])
        
        # 提交按钮
        submitted = st.form_submit_button("确认添加", type="primary", use_container_width=True)
        
        if submitted:
            if not new_target or not new_fluor:
                st.error("操作失败：请务必填写【靶点】和【荧光素】！")
            else:
                new_row = pd.DataFrame([{
                    "Target": new_target,
                    "Fluorophore": new_fluor,
                    "Localization": new_loc,
                    "Clone": new_clone,
                    "Box_Location": new_box,
                    "Status": new_status
                }])
                # 将新添加的行放在最上面
                updated_df = pd.concat([new_row, st.session_state.df], ignore_index=True)
                save_data(updated_df)
                st.success(f"成功添加 {new_target} ({new_fluor})！")
                st.rerun() # 强制刷新页面显示最新数据

    st.divider() # 分割线
    
    st.subheader("📥 备份与导出")
    st.caption("建议每周下载一次 CSV 文件进行本地备份，防止云端数据丢失。")
    csv = st.session_state.df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="下载全库 CSV 备份",
        data=csv,
        file_name='抗体库存备份.csv',
        mime='text/csv',
        use_container_width=True
    )

# ==================== 右侧主面板 ====================
with col_right:
    st.subheader("📊 抗体库存总览与检索")
    
    st.info("💡 操作指南：\n1. **检索**：点击表格右上角的放大镜图标 🔍 即可全局模糊搜索。\n2. **删除/修改**：如果填错了或者想删除某行，直接在下方表格内双击修改，或勾选左侧方框按 `Delete` 键即可，系统会自动保存。")

    # 渲染可交互的数据表格
    edited_df = st.data_editor(
        st.session_state.df,
        use_container_width=True,
        num_rows="dynamic", # 关键参数：允许用户在表格内直接删除行
        height=580,
        column_config={
            "Target": st.column_config.TextColumn("靶点 (Target)"),
            "Fluorophore": st.column_config.TextColumn("荧光素 (Fluor)"),
            "Localization": st.column_config.SelectboxColumn(
                "抗原位置", 
                options=["Surface (表面)", "Intracellular (胞内)", "Intranuclear (核内)"]
            ),
            "Status": st.column_config.SelectboxColumn(
                "状态",
                options=["In Use (使用中)", "Low (快用完)", "Empty (待采购)", "Expired (已过期)"]
            )
        }
    )

    # 监听表格内部的修改或删除动作，并实时保存
    if not edited_df.equals(st.session_state.df):
        save_data(edited_df)
        st.rerun()
