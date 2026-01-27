import streamlit as st

# 1. 初始化 Session State
if 'playlist' not in st.session_state:
    # 預設一啲示範片
    st.session_state.playlist = [
        {"name": "示範影片 1", "url": "https://www.w3schools.com/html/mov_bbb.mp4"},
        {"name": "示範影片 2", "url": "https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4"}
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
    new_url = st.text_input("影片 URL：", placeholder="https://...")
    
    if st.button("加入清單"):
        if new_name and new_url:
            st.session_state.playlist.append({"name": new_name, "url": new_url})
            st.success(f"已加入：{new_name}")
            st.rerun()
        else:
            st.error("名同埋 URL 都要填呀！")

    st.divider()
    st.header("📜 播放清單")
    
    # 顯示 Playlist 同埋 刪除功能
    if not st.session_state.playlist:
        st.write("清單係空嘅。")
    else:
        for i, vid in enumerate(st.session_state.playlist):
            col_name, col_del = st.columns([0.8, 0.2])
            
            # 點擊名就轉片
            with col_name:
                if st.button(f"▶️ {vid['name']}", key=f"play_{i}", use_container_width=True):
                    st.session_state.current_idx = i
                    st.rerun()
            
            # 刪除掣
            with col_del:
                if st.button("❌", key=f"del_{i}"):
                    st.session_state.playlist.pop(i)
                    # 如果刪除嘅係而家播緊嗰條，將 index 移返去第一條
                    if st.session_state.current_idx >= len(st.session_state.playlist):
                        st.session_state.current_idx = 0
                    st.rerun()

# --- 主畫面：播放器 ---
if st.session_state.playlist:
    current_vid = st.session
