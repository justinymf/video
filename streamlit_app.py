import streamlit as st

st.title('你好！呢個係 Streamlit App')
name = st.text_input('話我知你叫咩名？')
age = st.slider('你幾多歲？', 0, 100, 25)

st.write(f'喂 {name}，原來你已經 {age} 歲喇！')
