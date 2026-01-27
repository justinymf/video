import streamlit as st
import random
import smtplib
import json
import os
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- AWS SES SMTP 配置 ---
SMTP_SERVER = "email-smtp.eu-west-1.amazonaws.com" 
SMTP_PORT = 587 # 建議使用 587 配合 TLS
SMTP_USER = "AKIAWC2TYOLMNDRUO3WQ"
SMTP_PWD = "BA5FxCqEE60BwJUQd8r5uVE+wx3URXYaqiKaHH0yvXdQ"
SENDER_EMAIL = "noreply-scan-hk@scan.decathlon.com"

# --- 2FA 功能函數 ---
def send_otp_email(receiver_email):
    otp = str(random.randint(100000, 999999))
    st.session_state.generated_otp = otp
    
    msg = MIMEMultipart()
    msg['From'] = f"Decathlon Admin <{SENDER_EMAIL}>"
    msg['To'] = receiver_email
    msg['Subject'] = f"你的驗證碼: {otp}"
    
    body = f"你好，\n\n你的登入驗證碼是：{otp}\n\n請在頁面輸入此代碼。如果不是你本人操作，請忽略此電郵。"
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        # 建立安全連接
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls() 
        server.login(SMTP_USER, SMTP_PWD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"郵件發送失敗，請聯絡 IT。錯誤: {e}")
        return False

# --- 登入邏輯介面 ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'otp_sent' not in st.session_state:
    st.session_state.otp_sent = False

st.title("🛡️ Decathlon 內部影片系統")

if not st.session_state.authenticated:
    email_input = st.text_input("輸入員工 Email (@decathlon.com):")
    
    if not st.session_state.otp_sent:
        if st.button("獲取驗證碼"):
            if email_input.lower().endswith("@decathlon.com"):
                if send_otp_email(email_input):
                    st.session_state.otp_sent = True
                    st.rerun()
            else:
                st.error("僅限 @decathlon.com 域名使用。")
    else:
        otp_code = st.text_input("輸入 6 位驗證碼:")
        if st.button("確認登入"):
            if otp_code == st.session_state.generated_otp:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("驗證碼錯誤。")
    st.stop() # 未認證前停止執行後續代碼

# --- 認證成功後的內容 ---
st.success("登入成功！")
# 這裡放置之前的播放清單管理代碼...
import streamlit as st
import json
import os
import re

# 設定檔案路徑
DB_FILE = "playlist.json"
ADMIN_PASSWORD = "admin123"  # 你可以喺度改密碼

# --- 功能：讀取與儲存 JSON ---
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- 工具：轉換 Google Drive 連結 ---
def convert_google_drive_url(url):
    if "drive.google.com" in url:
        file_id_match = re.search(r'/d/([^/]+)', url)
        if file_id_match:
            file_id = file_id_match.group(1)
            return f'https://drive.google.com/uc?export=download&id={file_id}'
    return url

# --- 初始化 ---
st.set_page_config(page_title="Shared Video Player", layout="wide")
playlist = load_data()

if 'current_idx' not in st.session_state:
    st.session_state.current_idx = 0

st.title("🌐 全球同步播放器 (Shared Playlist)")

# --- 側邊欄：權限與管理 ---
with st.sidebar:
    st.header("🔑 Admin 登入")
    password = st.text_input("輸入 Admin 密碼以編輯：", type="password")
    is_admin = (password == ADMIN_PASSWORD)

    if is_admin:
        st.success("Admin 模式已開啟")
        st.header("➕ 管理功能")
        new_name = st.text_input("影片名稱：")
        new_url = st.text_input("影片 URL：")
        
        if st.button("加入並同步"):
            if new_name and new_url:
                processed_url = convert_google_drive_url(new_url)
                playlist.append({"name": new_name, "url": processed_url})
                save_data(playlist) # 儲存到 File
                st.rerun()
    else:
        st.info("唯讀模式：你只可以睇片，唔可以改 Playlist。")

    st.divider()
    st.header("📜 播放清單")
    
    if not playlist:
        st.write("清單暫時係空嘅")
    else:
        for i, vid in enumerate(playlist):
            col_name, col_del = st.columns([0.8, 0.2])
            with col_name:
                label = f"▶️ {vid['name']}" if i == st.session_state.current_idx else vid['name']
                if st.button(label, key=f"play_{i}", use_container_width=True):
                    st.session_state.current_idx = i
                    st.rerun()
            
            # 只有 Admin 先見到刪除掣
            if is_admin:
                with col_del:
                    if st.button("❌", key=f"del_{i}"):
                        playlist.pop(i)
                        save_data(playlist) # 同步儲存
                        st.rerun()

# --- 主畫面：播放區域 ---
if playlist:
    # 確保 index 唔會過界 (如果有人喺另一邊刪咗片)
    if st.session_state.current_idx >= len(playlist):
        st.session_state.current_idx = 0
        
    current_vid = playlist[st.session_state.current_idx]
    st.subheader(f"📺 正在播放：{current_vid['name']}")
    
    # 播放器
    st.video(current_vid['url'])
    
    # 導航
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.button("⏮️ 上一段"):
            st.session_state.current_idx = (st.session_state.current_idx - 1) % len(playlist)
            st.rerun()
    with c3:
        if st.button("下一段 ⏭️"):
            st.session_state.current_idx = (st.session_state.current_idx + 1) % len(playlist)
            st.rerun()
else:
    st.warning("目前清單冇片。請聯絡 Admin 新增影片。")
