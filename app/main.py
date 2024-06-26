import streamlit as st

st.title("Nice App")

name = st.text_input("Insert your name here:")

if name:
    st.write(f"Hello {name}!")

st.text("Map illustration")

#https://docs.streamlit.io/develop/api-reference/charts/st.map
coords = [
    {
        "latitude": 51.221371, 
        "longitude": 12.500010
    }
]
st.map(data=coords)