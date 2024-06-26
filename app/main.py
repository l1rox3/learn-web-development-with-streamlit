import streamlit as st

name = st.text_input("Insert your name here:")

if st.button("Click me"):
    st.write(f"Hello {name}!")