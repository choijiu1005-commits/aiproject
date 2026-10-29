import streamlit as st
st.title('집가고싶다!')
a=st.text_input('이름을 입력해줘')
b=st.selectbox('오늘 저녁 뭐 먹지?!',['마라탕','엽떡','훠궈','된찌','돼지국밥','계란초밥과마라샹궈'])
if st.button('인사말 생성'):
  st.write('반가워!!!')
  st.info(a+'! 안뇽 돈 줘!')
  st.warning(b+'이거 야무지지')
  st.error('잘 부탁행!!')
  st.balloons()
