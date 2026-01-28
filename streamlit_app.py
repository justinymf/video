import streamlit as st
import streamlit.components.v1 as components
import json
import os
import re
import base64

# --- 設定 ---
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

# --- 初始化 Session State ---
if 'cloud_idx' not in st.session_state: st.session_state.cloud_idx = 0
if 'local_idx' not in st.session_state: st.session_state.local_idx = 0
if 'local_playlist' not in st.session_state: st.session_state.local_playlist = []

# --- JavaScript 自動跳轉組件 ---
def auto_next_player(src_url):
    html_code = f"""
        <video id="vid" width="100%" controls autoplay muted style="border-radius: 10px; background: black;">
            <source src="{src_url}" type="video/mp4">
        </video>
        <script>
            var v = document.getElementById("vid");
            v.onended = function() {{
                const buttons = window.parent.document.querySelectorAll('button');
                for (let btn of buttons) {{
                    if (btn.innerText.includes('下一段')) {{
                        btn.click();
                        break;
                    }}
                }}
            }};
        </script>
    """
    components.html(html_code, height=500)

# --- UI 介面 ---
st.set_page_config(page_title="Decathlon Video Player", layout="wide")
st.title("🎬 萬能自動播放系統")

mode = st.radio("選擇模式：", ["網上同步模式", "本地上傳模式"], horizontal=True)

# ---------------------------------------------------------
# 模式 A: 網上同步模式
# ---------------------------------------------------------
if mode == "網上同步模式":
    playlist = load_data()
    
    with st.sidebar:
        st.header("🔑 Admin")
        admin_pw = st.text_input("密碼", type="password")
        if admin_pw == "admin123":
            new_name = st.text_input("影片名")
            new_url = st.text_input("影片 URL (.mp4 直連)")
            if st.button("加入清單"):
                playlist.append({"name": new_name, "url": new_url})
                save_data(playlist)
                st.rerun()
        
        st.divider()
        st.header("📜 播放清單")
        for i, vid in enumerate(playlist):
            if st.button(f"▶️ {vid['name']}" if i == st.session_state.cloud_idx else vid['name'], key=f"c_{i}", use_container_width=True):
                st.session_state.cloud_idx = i
                st.rerun()

    if playlist:
        st.session_state.cloud_idx %= len(playlist)
        current = playlist[st.session_state.cloud_idx]
        st.subheader(f"正在播放：{current['name']}")
        auto_next_player(current['url'])
        if st.button("下一段 ⏭️"):
            st.session_state.cloud_idx = (st.session_state.cloud_idx + 1) % len(playlist)
            st.rerun()

# ---------------------------------------------------------
# 模式 B: 本地上傳模式
# ---------------------------------------------------------
else:
    with st.sidebar:
        st.header("📂 本地上傳")
        files = st.file_uploader("選取多個影片", type=["mp4", "mov"], accept_multiple_files=True)
        if st.button("更新清單"):
            st.session_state.local_playlist = [{"name": f.name, "bytes": f.read()} for f in files]
            st.session_state.local_idx = 0
            st.rerun()

    if st.session_state.local_playlist:
        st.session_state.local_idx %= len(st.session_state.local_playlist)
        current = st.session_state.local_playlist[st.session_state.local_idx]
        st.subheader(f"正在播放本地：{current['name']}")
        
        # 本地影片需要轉成 Base64 格式
        b64 = base64.b64encode(current['bytes']).decode()
        src = f"data:video/mp4;base64,{b64}"
        auto_next_player(src)
        
        if st.button("下一段 ⏭️"):
            st.session_state.local_idx = (st.session_state.local_idx + 1) % len(st.session_state.local_playlist)
            st.rerun()