import streamlit as st
import re

# --- 工具函數：轉換 Google Drive 連結 ---
def convert_google_drive_url(url):
    if "drive.google.com" in url:
        file_id_match = re.search(r'/d/([^/]+)', url)
        if file_id_match:
            file_id = file_id_match.group(1)
            return f'https://drive.google.com/uc?export=download&id={file_id}'
    return url

# --- 1. 初始化 Session State ---
if 'playlist' not in st.session_state:
    st.session_state.playlist = [
        {"name": "YouTube 範例", "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
        {"name": "MP4 範例", "url": "https://www.w3schools.com/html/mov_bbb.mp4"}
    ]

if 'current_idx' not in st.session_state:
    st.session_state.current_idx = 0

# --- 2. 介面設定 ---
st.set_page_config(page_title="Universal Player", layout="wide")
st.title("📺 萬能影片播放清單")

# --- 3. 側邊欄：管理功能 ---
with st.sidebar:
    st.header("➕ 新增影片")
    new_name = st.text_input("影片名稱：")
    new_url = st.text_input("影片 URL (YT / Drive / MP4)：")
    
    if st.button("加入清單"):
        if new_name and new_url:
            # 自動處理網址：如果是 Drive 就轉，YouTube 則保持原樣
            processed_url = convert_google_drive_url(new_url)
            st.session_state.playlist.append({"name": new_name, "url": processed_url})
            st.rerun()
        else:
            st.error("請填寫名稱同網址！")

    st.divider()
    st.header("📜 播放清單")
    
    if not st.session_state.playlist:
        st.write("清單暫時係空嘅")
    else:
        for i, vid in enumerate(st.session_state.playlist):
            col_name, col_del = st.columns([0.8, 0.2])
            with col_name:
                # 顯示當前播放緊嘅標記
                label = f"▶️ {vid['name']}" if i == st.session_state.current_idx else vid['name']
                if st.button(label, key=f"play_{i}", use_container_width=True):
                    st.session_state.current_idx = i
                    st.rerun()
            with col_del:
                if st.button("❌", key=f"del_{i}"):
                    st.session_state.playlist.pop(i)
                    # 調整 index 廢事 index out of range
                    st.session_state.current_idx = min(st.session_state.current_idx, max(0, len(st.session_state.playlist)-1))
                    st.rerun()

# --- 4. 主畫面：播放區域 ---
if st.session_state.playlist:
    current_vid = st.session_state.playlist[st.session_state.current_idx]
    
    st.subheader(f"正在播放：{current_vid['name']}")
    
    # 判斷係咪 YouTube (YouTube 唔支援 loop/autoplay 等 Streamlit 參數)
    is_youtube = "youtube.com" in current_vid['url'] or "youtu.be" in current_vid['url']
    
    if is_youtube:
        # YouTube 直接播，控制權交俾 YouTube Player
        st.video(current_vid['url'])
        st.info("💡 YouTube 影片請使用播放器內置控制掣。")
    else:
        # 普通 MP4 / Drive 直連，可以用埋參數
        st.video(current_vid['url'], autoplay=True)

    # 上下首導航
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.button("⏮️ 上一段") and len(st.session_state.playlist) > 1:
            st.session_state.current_idx = (st.session_state.current_idx - 1) % len(st.session_state.playlist)
            st.rerun()
    with c3:
        if st.button("下一段 ⏭️") and len(st.session_state.playlist) > 1:
            st.session_state.current_idx = (st.session_state.current_idx + 1) % len(st.session_state.playlist)
            st.rerun()
else:
    st.warning("請喺左邊加入影片開始播放。")
