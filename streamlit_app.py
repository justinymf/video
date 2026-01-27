import streamlit as st
import random
import smtplib
from email.mime.text import MIMEText

# --- 模擬設定 (實際應用請用環境變數) ---
# 你需要一個公司或個人的 SMTP Server 嚟寄 Email
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your-app-email@gmail.com"
SENDER_PASSWORD = "your-app-password" 

# --- 初始化 Session State ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'otp_sent' not in st.session_state:
    st.session_state.otp_sent = False
if 'generated_otp' not in st.session_state:
    st.session_state.generated_otp = None

def send_otp(target_email):
    otp = str(random.randint(100000, 999999))
    st.session_state.generated_otp = otp
    # 呢度理論上要寫 smtplib 寄信 Code
    # 為咗示範，我哋直接 print 出嚟
    st.write(f"🔐 [Debug] OTP 已經寄出到 {target_email}: {otp}")
    st.session_state.otp_sent = True

# --- 登入介面 ---
if not st.session_state.authenticated:
    st.title("Decathlon 內部影片管理系統")
    
    email = st.text_input("輸入公司 Email:", placeholder="username@decathlon.com")
    
    if not st.session_state.otp_sent:
        if st.button("獲取驗證碼"):
            if email.endswith("@decathlon.com"):
                send_otp(email)
                st.success("驗證碼已寄出，請檢查 Email。")
            else:
                st.error("❌ 只准許 @decathlon.com 的員工登入。")
    else:
        otp_input = st.text_input("輸入 6 位數驗證碼：")
        if st.button("確認登入"):
            if otp_input == st.session_state.generated_otp:
                st.session_state.authenticated = True
                st.success("登入成功！")
                st.rerun()
            else:
                st.error("驗證碼錯誤。")
        
        if st.button("重新發送"):
            st.session_state.otp_sent = False
            st.rerun()
    st.stop() # 唔登入就唔俾行落去

# --- 登入後嘅內容 ---
st.success(f"歡迎回來，Decathlon 團隊成員！")
# 之後接返你個 Playlist 管理 Code...
