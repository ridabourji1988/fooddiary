import streamlit as st
from database import register_user, login_user, get_aliments, add_aliment, add_entry, get_entries
from ui_components import saisie_quotidienne, afficher_historique_calendrier
from data_analysis import analyse_mensuelle

def auth_form():
    st.header("Login / Sign Up")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Login"):
            success = login_user(email, password)
            if success:
                st.session_state['logged_in'] = True
                st.session_state['user_email'] = email
                st.success("You are successfully logged in!")
                st.rerun()
            else:
                st.error("Invalid email or password")
    
    with col2:
        if st.button("Sign Up"):
            st.session_state['show_signup'] = True
    
    if st.session_state.get('show_signup', False):
        with st.form("signup_form"):
            st.subheader("Sign Up")
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            if st.form_submit_button("Complete Sign Up"):
                if password != confirm_password:
                    st.error("Passwords do not match!")
                elif not all([first_name, last_name, email, password]):
                    st.error("All fields are required!")
                else:
                    success = register_user(email, password, first_name, last_name)
                    if success:
                        st.success("You have successfully signed up!")
                        st.session_state['logged_in'] = True
                        st.session_state['user_email'] = email
                        st.rerun()
                    else:
                        st.error("This email is already registered.")

def logout():
    st.session_state['logged_in'] = False
    st.session_state['user_email'] = None
    st.session_state['show_signup'] = False
    st.success("You have been logged out.")
    st.rerun()

def main():
    st.title("Health Tracking App")

    if st.session_state.get('logged_in'):
        st.sidebar.button("Logout", on_click=logout)
        
        tab1, tab2, tab3 = st.tabs(["Saisie Quotidienne", "Analyse Mensuelle", "Historique Calendrier"])
        
        with tab1:
            saisie_quotidienne(st.session_state['user_email'])
        
        with tab2:
            analyse_mensuelle(st.session_state['user_email'])
        
        with tab3:
            afficher_historique_calendrier(st.session_state['user_email'])
    else:
        auth_form()

# Initialize the session state if it doesn't exist
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = None
if 'show_signup' not in st.session_state:
    st.session_state['show_signup'] = False

if __name__ == "__main__":
    main()