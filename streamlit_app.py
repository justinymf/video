import streamlit as st
import json
import os
import re

# --- 配置與初始化 ---
DB_FILE = "playlist.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def convert_google_drive_url(url):
    if "drive.google.com" in url:
        file_id_match = re.search(r'/d/([^/]+)', url)
        if file_id_match:
            file_id = file_id_match.group(1)
            return f'https://drive.google.com/uc?export=download&id={file_id}'
    return url

# --- 介面啟動 ---
st.set_page_config(page_title="Hybrid Video Player", layout="wide")

# --- 頂部切換按鈕 ---
st.title("🎬 萬能影片播放系統")
mode = st.radio("選擇播放模式：", ["網上清單模式 (Cloud Sync)", "本地檔案模式 (Local File)"], horizontal=True)

st.divider()

# ==========================================
# 模式 1：網上清單模式 (之前寫落的邏輯)
# ==========================================
if mode == "網上清單模式 (Cloud Sync)":
    playlist = load_data()
    
    if 'current_idx' not in st.session_state:
        st.session_state.current_idx = 0

    with st.sidebar:
        st.header("🔑 管理權限")
        admin_pw = st.text_input("輸入管理密碼：", type="password")
        is_admin = (admin_pw == "admin123")

        if is_admin:
            st.header("➕ 新增網上影片")
            new_name = st.text_input("名稱：")
            new_url = st.text_input("URL (YouTube/Drive/MP4)：")
            if st.button("加入同步清單"):
                if new_name and new_url:
                    processed_url = convert_google_drive_url(new_url)
                    playlist.append({"name": new_name, "url": processed_url})
                    save_data(playlist)
                    st.rerun()

        st.header("📜 同步清單")
        if not playlist:
            st.write("清單係空嘅")
        else:
            for i, vid in enumerate(playlist):
                col_name, col_del = st.columns([0.8, 0.2])
                with col_name:
                    label = f"▶️ {vid['name']}" if i == st.session_state.current_idx else vid['name']
                    if st.button(label, key=f"cloud_{i}", use_container_width=True):
                        st.session_state.current_idx = i
                        st.rerun()
                if is_admin:
                    with col_del:
                        if st.button("❌", key=f"del_{i}"):
                            playlist.pop(i)
                            save_data(playlist)
                            st.rerun()

    # 主播放區域
    if playlist:
        if st.session_state.current_idx >= len(playlist):
            st.session_state.current_idx = 0
        current_vid = playlist[st.session_state.current_idx]
        st.subheader(f"正在播放 (網上)：{current_vid['name']}")
        st.video(current_vid['url'])
    else:
        st.info("請於側邊欄加入網上影片連結。")

# ==========================================
# 模式 2：本地檔案模式
# ==========================================
else:
    st.subheader("📂 本地檔案播放")
    st.write("從你的電腦選擇影片檔案直接播放（唔會同步到其他 User）。")
    
    uploaded_file = st.file_uploader("選擇影片 (.mp4, .mov)", type=["mp4", "mov", "avi"])
    
    if uploaded_file is not None:
        video_bytes = uploaded_file.read()
        st.video(video_bytes)
        st.success(f"正在預覽本地檔案：{uploaded_file.name}")
    else:
        st.info("請選擇電腦入面嘅影片檔案。")
