import streamlit as st
import pandas as pd
import os

# 1. 网页全局配置
st.set_page_config(page_title="肿瘤免疫流式抗体库", page_icon="🔬", layout="wide")
st.title("🔬 肿瘤免疫流式抗体库存管理系统")

DATA_FILE = "antibodies.csv"

# 2. 初始化数据库 (如果没有则自动创建)
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["靶点 (Target)", "荧光素", "抗原位置", "克隆号", "存放位置", "状态"])
    df.to_csv(DATA_FILE, index=False)

df = pd.read_csv(DATA_FILE)

st.info("💡 交互指南：\n1. **修改**：直接双击表格任意单元格即可修改内容。\n2. **删除**：勾选表格最左侧的复选框，按键盘 Delete 键。\n3. **添加**：直接在表格最底部的空白行输入新抗体信息。")

# 3. 渲染交互式表格面板
edited_df = st.data_editor(
    df,
    num_rows="dynamic",        # 允许动态添加和删除行
    use_container_width=True,  # 自动适应屏幕宽度
    height=500
)

# 4. 保存机制
col1, col2 = st.columns([1, 4])
with col1:
    if st.button("💾 将修改保存至云端", use_container_width=True):
        edited_df.to_csv(DATA_FILE, index=False)
        st.success("最新库存状态已成功保存！")

# 5. 备份机制 (云端服务器休眠重启时可能会重置文件，建议定期备份)
with col2:
    csv = edited_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 下载 CSV 备份文件",
        data=csv,
        file_name='抗体库存备份.csv',
        mime='text/csv',
    )
