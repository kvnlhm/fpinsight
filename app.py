import streamlit as st
import importlib.util
import sys
import os

st.set_page_config(
    page_title="My App",
    page_icon="chart_with_upwards_trend",
    layout="wide",
    initial_sidebar_state="auto"
)

# Define a dictionary to store the pages and their corresponding roles
pages = {
    "Data_Transaksi": ["admin"],
    "Penamaan_Kode": ["admin"],
    "Perhitungan_FPGrowth": ["admin"],
    "Association_Rules": ["admin"],
    "Laporan": ["admin", "pimpinan"]
}

def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "admin" and password == "admin123":  # Replace with your admin credentials
            st.session_state.username = "admin"
            st.experimental_rerun()
        elif username == "pimpinan" and password == "pimpinan123":  # Replace with your pimpinan credentials
            st.session_state.username = "pimpinan"
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")

def main():
    if 'username' not in st.session_state or st.session_state.username is None:
        login()
        return

    # Add a logout button
    if st.sidebar.button("Logout"):
        st.session_state.username = None
        st.experimental_rerun()

    # Get the user's role
    role = st.session_state.username

    # Create buttons to display the available pages
    st.sidebar.title("Navigation")
    for page, roles in pages.items():
        if role in roles:
            if st.sidebar.button(page, key=page):
                st.session_state.selected_page = page

    # Default to the first available page if no page is selected
    if 'selected_page' not in st.session_state:
        st.session_state.selected_page = next(page for page, roles in pages.items() if role in roles)

    selected_page = st.session_state.selected_page

    # Import the selected page module
    page_path = os.path.join("pages", "page", f"{selected_page}.py")
    spec = importlib.util.spec_from_file_location(selected_page, page_path)
    page_module = importlib.util.module_from_spec(spec)
    sys.modules[selected_page] = page_module
    spec.loader.exec_module(page_module)
    page_module.main()  # Assuming each page module has a main() function

# Add custom CSS to style the buttons
st.markdown("""
    <style>
    .stButton button {
        width: 100%;
        margin: 5px 0;
        padding: 10px;
        font-size: 16px;
        border: none;
        border-radius: 5px;
        transition: background-color 0.3s, box-shadow 0.3s;
    }
    .stButton button:hover {
        background-color: #e6e6e6;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .stButton button:active {
        background-color: #d4d4d4;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()