import streamlit as st

from st_pages import Page, Section, show_pages, add_page_title

# Optional -- adds the title and icon to the current page
st.title('Philosophy W12A Fitch-Style Proof Checker')

# Specify what pages should be shown in the sidebar, and what their titles and icons
# should be
show_pages(
    [
        Page("get_started.py", "Getting Started", ":books:"),
        Section(name='Writing Fitch Proofs', icon=":writing_hand:"),
        Page("prop/prop_fitch.py", "Propositional Logic"),
        Page("pred/pred_fitch.py", "Predicate Logic"),
    ]
)