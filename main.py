import streamlit as st
from st_pages import Page, Section, show_pages, add_page_title

st.title('W12A Fitch-Style Proof Applet')

col1, col2 = st.columns([1,1])
with col2:
    st.subheader('by Asher Cohen')

show_pages(
    [
        Page("get_started.py", "Getting Started", ":books:"),
        Section(name='Writing Fitch Proofs', icon=":writing_hand:"),
        Page("prop/prop_fitch.py", "Propositional Logic"),
        Page("pred/pred_fitch.py", "Predicate Logic"),
    ]
)