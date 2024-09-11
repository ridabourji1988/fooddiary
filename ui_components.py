import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter
import unicodedata
from database import get_entries



def prepare_data(entries):
    """Prepare the data from entries into a DataFrame."""
    symptom_data = []
    for entry in entries:
        date, aliments, symptomes = entry
        symptomes_list = symptomes['symptomes_specifiques']
        intensite = symptomes['intensite_douleur']
        aliments_list = [item for sublist in aliments.values() for item in sublist]
        
        for symptome in symptomes_list:
            # Normalize the symptom name
            normalized_symptom = normalize_text(symptome)
            symptom_data.append({
                'date': date,
                'symptome': normalized_symptom,  # Use the normalized symptom
                'intensite': intensite,
                'aliments': aliments_list
            })
    
    df = pd.DataFrame(symptom_data)
    # Replace symptom names with emojis, defaulting to "❓" if not found
    df['emoji'] = df['symptome'].map(SYMPTOM_TO_EMOJI).fillna("❓")
    return df

import plotly.express as px

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
    fig.update_layout(hovermode="closest")
    
    return fig


def analyze_aliments(entries):
    """Create a bar chart showing the frequency of consumed foods."""
    all_aliments = [aliment for entry in entries for repas in entry[1].values() for aliment in repas]
    aliment_counts = Counter(all_aliments)
    
    # Create the bar chart
    fig = px.bar(x=list(aliment_counts.keys()), y=list(aliment_counts.values()),
                 title="Fréquence des aliments consommés")
    
    # Label the axes
    fig.update_xaxes(title="Aliments")
    fig.update_yaxes(title="Fréquence")
    
    return fig

def analyze_symptomes(entries):
    """Create a bar chart showing the frequency of symptoms."""
    all_symptoms = [symptom for entry in entries for symptom in entry[2]['symptomes_specifiques']]
    symptom_counts = Counter(all_symptoms)
    
    # Create the bar chart
    fig = px.bar(x=list(symptom_counts.keys()), y=list(symptom_counts.values()),
                 title="Fréquence des symptômes")
    
    # Label the axes
    fig.update_xaxes(title="Symptômes")
    fig.update_yaxes(title="Fréquence")
    
    return fig

def calculate_correlation(entries):
    """Calculate and display the correlation between foods and symptoms."""
    aliments_symptoms = {}
    
    # Collect symptoms for each food
    for entry in entries:
        aliments = [item for sublist in entry[1].values() for item in sublist]
        symptoms = entry[2]['symptomes_specifiques']
        for aliment in aliments:
            if aliment not in aliments_symptoms:
                aliments_symptoms[aliment] = Counter()
            aliments_symptoms[aliment].update(symptoms)
    
    # Create the correlation data frame
    all_symptoms = list(set([symptom for counters in aliments_symptoms.values() for symptom in counters]))
    correlation_data = pd.DataFrame({aliment: [counter.get(symptom, 0) for symptom in all_symptoms] 
                                     for aliment, counter in aliments_symptoms.items()}, 
                                    index=all_symptoms)
    
    return correlation_data.div(correlation_data.sum(axis=1), axis=0)

def analyse_mensuelle(user_email):
    """Main function to run the monthly analysis."""
    st.subheader("Analyse mensuelle")
    
    # Get entries for the user
    entries = get_entries(user_email)
    
    if not entries:
        st.warning("Aucune donnée n'est disponible pour l'analyse.")
        return
    
    # Prepare data
    df = prepare_data(entries)

    # 1. Graphique des symptômes par jour avec emojis
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
                                labels=dict(x="Symptômes", y="Aliments", color="Corrélation"))
    st.plotly_chart(fig_correlation)

if __name__ == "__main__":
    # This part is useful for testing the module independently
    import sys
    sys.path.append('..')  # Ensure the parent folder is in the PYTHONPATH
    
    # Simulate a Streamlit session for testing
    if 'user_email' not in st.session_state:
        st.session_state['user_email'] = "test@example.com"
    
    # Run the monthly analysis for the test user
    analyse_mensuelle(st.session_state['user_email'])
