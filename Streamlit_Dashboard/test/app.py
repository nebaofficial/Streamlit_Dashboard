import streamlit as st
st.title("my first app by streamlit")
st.write("welcome to our chat app")
st.sidebar.header("let's build the chat app")
if st.button("click me"):
    st.write("button is clickd")
    st.balloons()
else:
    st.write("button is not clicked yet")
    favorite_color=st.selectbox(
        "what is your favorite color"
        ,["","yellow","blue","green","red"]
    )