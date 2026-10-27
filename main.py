import streamlit as st
st.title('나의 첫 웹 서비스 만들기!')
st.text_input('이름을 입력해주세요')
st.selectbox('좋아하는 음식을 선택하세요!',['마라탕','엽떡','훠궈','된찌','돼지국밥','게란초밥과마라샹궈'])
st.button('인사말 생성')
