import streamlit as st
from links import FROH, TRAURIG

# Emojis: 😎 💻 🚀 😢 😁
# mehr Emojis gibt es hier: https://apps.timwhitlock.info/emoji/tables/unicode

# Erstelle Eingabebox
st.title("Willkommen zu meiner App! 😎")
st.write(
    "Hier kannst du deine Links zu den verschiedenen Seiten finden. "
    "Klicke einfach auf die Links, um die Seiten zu besuchen. 💻"
)
selected = st.multiselect(
    "Wähle die Links aus, die du besuchen möchtest:",
    ["Froh", "Traurig"],
    ["Froh", "Traurig"],
)

for select in selected:
    if select == "Froh":
        st.write("Hier ist der Link zu Froh: 😁")
        st.markdown(FROH)
    elif select == "Traurig":
        st.write("Hier ist der Link zu Traurig: 😢")
        st.markdown(TRAURIG)
    else:
        st.write("Bitte wähle einen Link aus.")
