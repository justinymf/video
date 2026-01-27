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
