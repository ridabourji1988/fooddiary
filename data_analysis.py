import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter
from database import get_entries

# Dictionary mapping symptoms to their corresponding emojis
SYMPTOM_TO_EMOJI = {
    "Nausées": "🤢",
    "Diarrhée": "💩",
    "Constipation": "🚽",
    "Ballonnements": "🎈",
    "Douleurs abdominales": "🔥",
    "Brûlures d'estomac": "🔥",
    "Reflux acide": "🌋",
    "Perte d'appétit": "🍽️",
    "Fatigue": "😴",
    "Vomissement": "🤮"
}

def prepare_data(entries):
    """Prepare the data from entries into a DataFrame."""
    symptom_data = []
    for entry in entries:
        date, aliments, symptomes = entry
        symptomes_list = symptomes['symptomes_specifiques']
        intensite = symptomes['intensite_douleur']
        aliments_list = [item for sublist in aliments.values() for item in sublist]
        
        for symptome in symptomes_list:
            symptom_data.append({
                'date': date,
                'symptome': symptome.strip(),  # Remove leading/trailing spaces
                'intensite': intensite,
                'aliments': aliments_list
            })
    
    df = pd.DataFrame(symptom_data)
    # Replace symptom names with emojis, defaulting to an empty string if not found
    df['emoji'] = df['symptome'].map(SYMPTOM_TO_EMOJI).fillna("❓")  # "❓" for unmapped symptoms
    return df

def analyze_symptomes_timeline(df):
    """Create a scatter plot for the evolution of symptoms over time using emojis."""
    # Ensure the date is in datetime format
    df['date'] = pd.to_datetime(df['date'])
    
    # Debugging: Check which symptoms are not being mapped
    missing_emojis = df[df['emoji'] == "❓"]['symptome'].unique()
    if len(missing_emojis) > 0:
        st.write("These symptoms were not mapped to emojis:", missing_emojis)
    
    # Create the scatter plot with emojis as text
    fig = px.scatter(df, x='date', y='intensite', 
                     text='emoji',  # Use emojis instead of colors
                     hover_data=['aliments', 'symptome'],  # Include symptom in hover
                     title="Évolution des symptômes au fil du temps")

    # Update the marker size and text position
    fig.update_traces(marker=dict(size=10), textposition='top center')

    # Format the x-axis to show the date in "day month year" format and set a tick per day
    fig.update_xaxes(
        tickformat="%d %B %Y",
        dtick=86400000.0  # Set a tick for each day (in milliseconds)
    )

    # Update layout to remove legend and ensure closest hover mode
    fig.update_layout(hovermode="closest", showlegend=False)

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
