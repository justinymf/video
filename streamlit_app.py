import streamlit as st
import re

# 自動將 Google Drive 連結轉為「直連」格式的工具
def convert_google_drive_url(url):
    # 檢查係咪 Google Drive 連結
    if "drive.google.com" in url:
        # 用 Regex 抽取出 File ID
        file_id_match = re.search(r'/d/([^/]+)', url)
        if file_id_match:
            file_id = file_id_match.group(1)
            return f'https://drive.google.com/uc?export=download&id={file_id}'
    return url

# 1. 初始化 Session State
if 'playlist' not in st.session_state:
    st.session_state.playlist = [
        {"name": "示範影片 1 (W3Schools)", "url": "https://www.w3schools.com/html/mov_bbb.mp4"},
    ]

if 'current_idx' not in st.session_state:
    st.session_state.current_idx = 0

# --- 介面標題 ---
st.set_page_config(page_title="My Video Player", layout="wide")
st.title("🎬 智能影片播放清單管理員")

# --- 側邊欄：新增影片 ---
with st.sidebar:
    st.header("➕ 新增影片")
    new_name = st.text_input("影片名稱：", placeholder="例如：我的假期")
    new_url = st.text_input("影片 URL (支援 Google Drive)：", placeholder="https://...")
    
    if st.button("加入清單"):
        if new_name and new_url:
            # 喺加入清單前先做格式轉換
            final_url = convert_google_drive_url(new_url)
            st.session_state.playlist.append({"name": new_name, "url": final_url})
            st.success(f"已加入：{new_name}")
            st.rerun()
        else:
            st.error("名同埋 URL 都要填呀！")

    st.divider()
    st.header("📜 播放清單")
    
    if not st.session_state.playlist:
        st.write("清單係空嘅。")
    else:
        for i, vid in enumerate(st.session_state.playlist):
            col_name, col_del = st.columns([0.8, 0.2])
            with col_name:
                if st.button(f"▶️ {vid['name']}", key=f"play_{i}", use_container_width=True):
                    st.session_state.current_idx = i
                    st.rerun()
            with col_del:
                if st.button("❌", key=f"del_{i}"):
                    st.session_state.playlist.pop(i)
                    if st.session_state.current_idx >= len(st.session_state.playlist):
                        st.session_state.current_idx = 0
                    st.rerun()

# --- 主畫面：播放器 (呢度補返 st.video) ---
if st.session_state.playlist:
    # 攞出當前要播嘅片
    current_vid = st.session_state.playlist[st.session_state.current_idx]
    
    st.subheader(f"正在播放：{current_vid['name']}")
    
    # 顯示播放器 
    # 加入 autoplay=True 等佢一揀片就自動播
    st.video(current_vid['url'], autoplay=True)
    
    # 顯示目前用緊嘅 URL (方便你檢查)
    with st.expander("查看影片網址詳情"):
        st.write(f"原始/轉換後網址: {current_vid['url']}")
    
    # 上下首控制掣
    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        if st.button("⏮️ 上一段"):
            st.session_state.current_idx = (st.session_state.current_idx - 1) % len(st.session_state.playlist)
            st.rerun()
    with c3:
        if st.button("下一段 ⏭️"):
            st.session_state.current_idx = (st.session_state.current_idx + 1) % len(st.session_state.playlist)
            st.rerun()
else:
    st.info("清單入面冇片，請喺左邊加入影片連結。")
