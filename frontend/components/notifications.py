import streamlit as st


def show_toast(message: str, icon: str = "✅"):
    """Display a toast notification with an optional icon."""
    st.toast(message, icon=icon)


def show_modal(title: str, body: str):
    """Display a simple modal dialog with a close button."""
    with st.modal(title):
        st.write(body)
        st.button("Close", key=f"close_{title}")
