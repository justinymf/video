import streamlit as st
import json
import os
import re

# --- 配置與功能函數 ---
DB_FILE = "playlist.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return []
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
st.set_page_config(page_title="Auto-Play Video Player", layout="wide")

# --- 初始化 Session State ---
if 'cloud_idx' not in st.session_state: st.session_state.cloud_idx = 0
if 'local_idx' not in st.session_state: st.session_state.local_idx = 0
if 'local_playlist' not in st.session_state: st.session_state.local_playlist = []

st.title("🎬 萬能自動播放系統")
mode = st.radio("選擇播放模式：", ["網上清單模式 (Cloud Sync)", "本地上傳模式 (Local Playlist)"], horizontal=True)

st.divider()

# ==========================================
# 模式 1：網上清單模式 (Cloud Sync)
# ==========================================
if mode == "網上清單模式 (Cloud Sync)":
    playlist = load_data()
    
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

        st.header("📜 網上播放清單")
        for i, vid in enumerate(playlist):
            col_name, col_del = st.columns([0.8, 0.2])
            with col_name:
                label = f"▶️ {vid['name']}" if i == st.session_state.cloud_idx else vid['name']
                if st.button(label, key=f"cloud_{i}", use_container_width=True):
                    st.session_state.cloud_idx = i
                    st.rerun()
            if is_admin:
                with col_del:
                    if st.button("❌", key=f"del_cloud_{i}"):
                        playlist.pop(i)
                        save_data(playlist)
                        st.rerun()

    if playlist:
        st.session_state.cloud_idx %= len(playlist)
        current = playlist[st.session_state.cloud_idx]
        st.subheader(f"正在播放：{current['name']}")
        
        # --- 自動播放關鍵設定 ---
        st.video(current['url'], autoplay=True, muted=True)
        
        if st.button("下一段 ⏭️"):
            st.session_state.cloud_idx = (st.session_state.cloud_idx + 1) % len(playlist)
            st.rerun()
    else:
        st.info("清單係空嘅。")

# ==========================================
# 模式 2：本地上傳模式 (Local Playlist)
# ==========================================
else:
    with st.sidebar:
        st.header("📂 上傳本地影片")
        uploaded_files = st.file_uploader("選擇影片檔案", type=["mp4", "mov"], accept_multiple_files=True)
        
        if st.button("更新本地清單"):
            if uploaded_files:
                st.session_state.local_playlist = []
                for f in uploaded_files:
                    st.session_state.local_playlist.append({"name": f.name, "bytes": f.read()})
                st.session_state.local_idx = 0
                st.rerun()
        
        st.divider()
        st.header("📜 本地播放清單")
        if not st.session_state.local_playlist:
            st.write("請先選擇並上傳檔案。")
        else:
            for i, vid in enumerate(st.session_state.local_playlist):
                label = f"▶️ {vid['name']}" if i == st.session_state.local_idx else vid['name']
                if st.button(label, key=f"local_{i}", use_container_width=True):
                    st.session_state.local_idx = i
                    st.rerun()
            if st.button("🗑️ 清空本地清單"):
                st.session_state.local_playlist = []
                st.rerun()

    if st.session_state.local_playlist:
        st.session_state.local_idx %= len(st.session_state.local_playlist)
        current = st.session_state.local_playlist[st.session_state.local_idx]
        
        st.subheader(f"正在播放本地：{current['name']}")
        
        # --- 自動播放關鍵設定 ---
        st.video(current['bytes'], autoplay=True, muted=True)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("⏮️ 上一段"):
                st.session_state.local_idx = (st.session_state.local_idx - 1) % len(st.session_state.local_playlist)
                st.rerun()
        with col2:
            if st.button("下一段 ⏭️"):
                st.session_state.local_idx = (st.session_state.local_idx + 1) % len(st.session_state.local_playlist)
                st.rerun()
    else:
        st.info("請於側邊欄選擇影片檔案並按下「更新本地清單」。")
