import streamlit as st
from links import FROH, TRAURIG

# Emojis: 😎 💻 🚀 😢 😁
# mehr Emojis gibt es hier: https://apps.timwhitlock.info/emoji/tables/unicode

st.title("😎 💻 🚀 Meine erste App 😎 💻 🚀")

name = st.text_input("Hallo! Wer bist du?")

if name:
    st.write("Hallo " + name + "!")
    st.write("---")
    stimmung = st.selectbox("Hast einen schönen Tag?", ["Weiß nicht", "Ja", "Nein"])
    if stimmung == "Ja":
        st.markdown(FROH)
        st.write("Toll!")
    if stimmung == "Nein":
        st.markdown(TRAURIG)
        st.write("Schade!")

    st.write("---")
    st.write("Wie gefällt dir diese App," + name)
    sterne = st.feedback("stars")
    if sterne:
        if sterne < 3:
            st.write("Schade! 😢")
        if sterne >= 3:
            st.write("Wow! 😁")
