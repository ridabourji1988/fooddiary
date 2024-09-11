import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from collections import Counter
from database import get_entries

def prepare_data(entries):
    symptom_data = []
    for entry in entries:
        date, aliments, symptomes = entry
        symptomes_list = symptomes['symptomes_specifiques']
        intensite = symptomes['intensite_douleur']
        aliments_list = [item for sublist in aliments.values() for item in sublist]
        for symptome in symptomes_list:
            symptom_data.append({
                'date': date,
                'symptome': symptome,
                'intensite': intensite,
                'aliments': aliments_list
            })
    
    return pd.DataFrame(symptom_data)



def analyze_symptomes_timeline(df):
    # Create the scatter plot
    fig = px.scatter(df, x='date', y='intensite', color='symptome',
                     hover_data=['aliments'],
                     title="Évolution des symptômes au fil du temps")
    
    # Update marker size
    fig.update_traces(marker=dict(size=10))
    
    # Remove hours from the date format and set one tick per day
    fig.update_xaxes(
        tickformat="%d %B %Y",  # Format date as 'day month year'
        dtick=86400000.0  # Set tick every day (1 day = 86400000 ms)
    )
    
    # Update hover mode to show the closest data point
    fig.update_layout(
        hovermode="closest",
        legend=dict(
            orientation="h",  # Horizontal layout
            yanchor="top",  # Anchor to the bottom
            y=-0.9,  # Position slightly below the graph
            xanchor="center",  # Center the legend
            x=0.5 # Horizontal center of the graph
        )
    )
    
    return fig

def analyze_aliments(entries):
    all_aliments = [aliment for entry in entries for repas in entry[1].values() for aliment in repas]
    aliment_counts = Counter(all_aliments)
    fig = px.bar(x=list(aliment_counts.keys()), y=list(aliment_counts.values()),
                 title="Fréquence des aliments consommés")
    fig.update_xaxes(title="Aliments")
    fig.update_yaxes(title="Fréquence")
    return fig

def analyze_symptomes(entries):
    all_symptoms = [symptom for entry in entries for symptom in entry[2]['symptomes_specifiques']]
    symptom_counts = Counter(all_symptoms)
    fig = px.bar(x=list(symptom_counts.keys()), y=list(symptom_counts.values()),
                 title="Fréquence des symptômes")
    fig.update_xaxes(title="Symptômes")
    fig.update_yaxes(title="Fréquence")
    return fig

def calculate_correlation(entries):
    aliments_symptoms = {}
    for entry in entries:
        aliments = [item for sublist in entry[1].values() for item in sublist]
        symptoms = entry[2]['symptomes_specifiques']
        for aliment in aliments:
            if aliment not in aliments_symptoms:
                aliments_symptoms[aliment] = Counter()
            aliments_symptoms[aliment].update(symptoms)
    
    all_symptoms = list(set([symptom for counters in aliments_symptoms.values() for symptom in counters]))
    correlation_data = pd.DataFrame({aliment: [counter.get(symptom, 0) for symptom in all_symptoms] 
                                     for aliment, counter in aliments_symptoms.items()}, 
                                    index=all_symptoms)
    
    return correlation_data.div(correlation_data.sum(axis=1), axis=0)

def analyse_mensuelle(user_email):
    st.subheader("Analyse mensuelle")
    entries = get_entries(user_email)
    
    if not entries:
        st.warning("Aucune donnée n'est disponible pour l'analyse.")
        return

    df = prepare_data(entries)

    # 1. Graphique des symptômes par jour
    fig_symptoms = analyze_symptomes_timeline(df)
    st.plotly_chart(fig_symptoms)

    # 2. Fréquence des aliments consommés
    fig_aliments = analyze_aliments(entries)
    st.plotly_chart(fig_aliments)

    # 3. Fréquence des symptômes
    fig_symptom_freq = analyze_symptomes(entries)
    st.plotly_chart(fig_symptom_freq)

    # 4. Corrélation entre aliments et symptômes
    correlation_data = calculate_correlation(entries)
    fig_correlation = px.imshow(correlation_data, 
                                title="Corrélation entre aliments et symptômes",
                                labels=dict(x="Aliments", y="Symptômes", color="Corrélation"))
    st.plotly_chart(fig_correlation)

if __name__ == "__main__":
    # Cette partie est utile pour tester le module indépendamment
    import sys
    sys.path.append('..')  # Assurez-vous que le dossier parent est dans le PYTHONPATH
    
    # Simuler une session Streamlit pour le test
    if 'user_email' not in st.session_state:
        st.session_state['user_email'] = "test@example.com"
    
    analyse_mensuelle(st.session_state['user_email'])
