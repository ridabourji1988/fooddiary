import streamlit as st
from streamlit_tags import st_tags
from datetime import datetime, timedelta
import pandas as pd
from database import get_aliments, add_aliment, add_entry, get_entries, update_entry, delete_entry

def saisie_quotidienne(user_email):
    st.subheader("Saisie quotidienne")
    date = st.date_input("Date")
    
    # Fetch existing entry for the selected date
    entries = get_entries(user_email)
    existing_entry = next((entry for entry in entries if entry[0] == date), None)

    aliments_existants = get_aliments()
    repas = {"Petit Déjeuner": [], "Déjeuner": [], "Goûter": [], "Dîner": []}
    symptomes_data = {"symptomes_specifiques": [], "intensite_douleur": 0, "autres_symptomes": ""}

    if existing_entry:
        st.info(f"Données existantes trouvées pour le {date}")
        _, existing_aliments, existing_symptomes = existing_entry
        repas = existing_aliments
        symptomes_data = existing_symptomes

    # Aliments input
    for repas_nom in repas.keys():
        st.subheader(repas_nom)
        aliments_saisis = st_tags(
            label=f"Entrez les aliments pour {repas_nom}:",
            text="Appuyez sur Entrée pour ajouter",
            value=repas[repas_nom],
            suggestions=aliments_existants,
            maxtags=-1,
            key=f"tags_{repas_nom}"
        )
        repas[repas_nom] = aliments_saisis
        
        for aliment in aliments_saisis:
            add_aliment(aliment)

    # Symptoms input
    symptomes_data = saisie_symptomes(symptomes_data)

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Enregistrer" if not existing_entry else "Mettre à jour"):
            if existing_entry:
                update_entry(user_email, date, repas, symptomes_data)
                st.success("Entrée mise à jour avec succès!")
            else:
                add_entry(user_email, date, repas, symptomes_data)
                st.success("Entrée enregistrée avec succès!")

    with col2:
        if existing_entry and st.button("Réinitialiser"):
            delete_entry(user_email, date)
            st.success("Entrée réinitialisée. Veuillez rafraîchir la page.")
            st.rerun()

    with col3:
        if st.button("Effacer le formulaire"):
            st.session_state['form_cleared'] = True
            st.rerun()

    if st.session_state.get('form_cleared', False):
        for key in st.session_state.keys():
            if key.startswith('tags_') or key.startswith('symptom_'):
                del st.session_state[key]
        st.session_state['form_cleared'] = False


def saisie_symptomes(existing_data):
    st.subheader("Symptômes/Douleurs")
    
    symptomes = {
        "Nausées 🤢": False,
        "Diarrhée 💩": False,
        "Constipation 🚽": False,
        "Ballonnements 🎈": False,
        "Douleurs abdominales 🔥": False,
        "Brûlures d'estomac 🔥": False,
        "Reflux acide 🌋": False,
        "Perte d'appétit 🍽️": False,
        "Fatigue 😴": False,
        "Vomissement 🤮": False
    }
    
    cols = st.columns(2)
    for i, (symptome, _) in enumerate(symptomes.items()):
        with cols[i % 2]:
            symptomes[symptome] = st.checkbox(symptome, 
                                              value=symptome in existing_data['symptomes_specifiques'],
                                              key=f"symptom_{symptome}")
    
    intensite_douleur = st.slider("Intensité de la douleur", 0, 10, 
                                  value=existing_data['intensite_douleur'],
                                  key="symptom_intensity")
    
    autres_symptomes = st.text_area("Autres symptômes ou commentaires", 
                                    value=existing_data['autres_symptomes'],
                                    key="symptom_notes")
    
    return {
        "symptomes_specifiques": [s for s, v in symptomes.items() if v],
        "intensite_douleur": intensite_douleur,
        "autres_symptomes": autres_symptomes
    }


import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database import get_entries

def afficher_historique_calendrier(user_email):
    st.subheader("Historique hebdomadaire")
    
    entries = get_entries(user_email)
    df = pd.DataFrame(entries, columns=['date', 'aliments', 'symptomes'])
    df['date'] = pd.to_datetime(df['date'])

    # Sélection de la semaine
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    selected_week = st.date_input("Sélectionnez une semaine", start_of_week)
    start_date = pd.to_datetime(selected_week - timedelta(days=selected_week.weekday()))
    end_date = start_date + timedelta(days=6)

    # Filtrer les données pour la semaine sélectionnée
    week_data = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

    # Afficher le calendrier
    for day in pd.date_range(start_date, end_date):
        with st.expander(day.strftime("%A %d/%m"), expanded=True):
            day_data = week_data[week_data['date'].dt.date == day.date()]
            if not day_data.empty:
                for _, row in day_data.iterrows():
                    st.markdown("### Repas")
                    for repas, aliments in row['aliments'].items():
                        if aliments:
                            st.markdown(f"**{repas}:** {', '.join(aliments)}")
                    
                    st.markdown("### Symptômes")
                    symptomes = row['symptomes'].get('symptomes_specifiques', [])
                    if symptomes:
                        st.markdown(", ".join(symptomes))
                    
                    intensite = row['symptomes'].get('intensite_douleur', 'N/A')
                    st.markdown(f"**Intensité:** {intensite}")
                    
                    # Ajouter une ligne de séparation
                    st.markdown("---")
            else:
                st.info("Pas de données pour ce jour")
                
                
import streamlit as st
from streamlit_tags import st_tags
from datetime import datetime
from database import get_aliments, add_aliment, add_entry, get_entries, update_entry, delete_entry

def saisie_quotidienne(user_email):
    st.subheader("Saisie quotidienne")
    date = st.date_input("Date")
    
    # Fetch existing entry for the selected date
    entries = get_entries(user_email)
    existing_entry = next((entry for entry in entries if entry[0] == date), None)

    aliments_existants = get_aliments()
    repas = {"Petit Déjeuner": [], "Déjeuner": [], "Goûter": [], "Dîner": []}
    symptomes_data = {"symptomes_specifiques": [], "intensite_douleur": 0, "autres_symptomes": ""}

    if existing_entry:
        st.info(f"Données existantes trouvées pour le {date}")
        _, existing_aliments, existing_symptomes = existing_entry
        repas = existing_aliments
        symptomes_data = existing_symptomes

    for repas_nom in repas.keys():
        st.subheader(repas_nom)
        aliments_saisis = st_tags(
            label=f"Entrez les aliments pour {repas_nom}:",
            text="Appuyez sur Entrée pour ajouter",
            value=repas[repas_nom],
            suggestions=aliments_existants,
            maxtags=-1,
            key=f"tags_{repas_nom}"
        )
        repas[repas_nom] = aliments_saisis
        
        for aliment in aliments_saisis:
            add_aliment(aliment)

    symptomes_data = saisie_symptomes(symptomes_data)

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Enregistrer" if not existing_entry else "Mettre à jour"):
            if existing_entry:
                update_entry(user_email, date, repas, symptomes_data)
                st.success("Entrée mise à jour avec succès!")
            else:
                add_entry(user_email, date, repas, symptomes_data)
                st.success("Entrée enregistrée avec succès!")

    with col2:
        if existing_entry and st.button("Réinitialiser"):
            delete_entry(user_email, date)
            st.success("Entrée réinitialisée. Veuillez rafraîchir la page.")
            st.rerun()

    with col3:
        if st.button("Effacer le formulaire"):
            st.session_state['form_cleared'] = True
            st.rerun()

    if st.session_state.get('form_cleared', False):
        for key in st.session_state.keys():
            if key.startswith('tags_'):
                del st.session_state[key]
        st.session_state['form_cleared'] = False

def saisie_symptomes(existing_data):
    st.subheader("Symptômes/Douleurs")
    
    symptomes = {
        "Nausées 🤢": False,
        "Diarrhée 💩": False,
        "Constipation 🚽": False,
        "Ballonnements 🎈": False,
        "Douleurs abdominales 🔥": False,
        "Brûlures d'estomac 🔥": False,
        "Reflux acide 🌋": False,
        "Perte d'appétit 🍽️": False,
        "Fatigue 😴": False,
        "Vomissement 🤮": False
    }
    
    cols = st.columns(2)
    for i, (symptome, _) in enumerate(symptomes.items()):
        with cols[i % 2]:
            symptomes[symptome] = st.checkbox(symptome, value=symptome in existing_data['symptomes_specifiques'])
    
    intensite_douleur = st.slider("Intensité de la douleur", 0, 10, existing_data['intensite_douleur'])
    
    autres_symptomes = st.text_area("Autres symptômes ou commentaires", existing_data['autres_symptomes'])
    
    return {
        "symptomes_specifiques": [s for s, v in symptomes.items() if v],
        "intensite_douleur": intensite_douleur,
        "autres_symptomes": autres_symptomes
    }
