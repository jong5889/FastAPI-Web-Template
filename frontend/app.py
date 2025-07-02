import streamlit as st
from components import render_header, render_footer, show_toast, show_modal
from theme import apply_theme

def main():
    dark_mode = st.sidebar.checkbox("Dark mode", value=False)
    apply_theme(dark_mode=dark_mode)
    render_header()

    st.write("Enter your name below:")
    with st.form(key="basic_form"):
        name = st.text_input("Name")
        submitted = st.form_submit_button("Submit")
        if submitted:
            show_toast(f"Hello, {name}!")

    if st.button("Open Modal"):
        show_modal("Modal Title", "This is a simple modal example.")

    render_footer()


if __name__ == "__main__":
    main()
