import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Configuration de la page
st.set_page_config(
    page_title="Smart Agence - Tableau de Bord",
    page_icon="📊",
    layout="wide"
)

# URL de base de l'API
API_URL = "http://localhost:8000"

# Fonction pour obtenir les données depuis l'API
def get_data(endpoint):
    try:
        response = requests.get(f"{API_URL}/{endpoint}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur lors de la récupération des données: {e}")
        return []

# Style CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 36px;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 30px;
    }
    .dashboard-card {
        padding: 20px;
        border-radius: 5px;
        background-color: #f8f9fa;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        text-align: center;
    }
    .metric-value {
        font-size: 36px;
        font-weight: bold;
        margin: 10px 0;
        color: #1565C0;
    }
    .metric-label {
        font-size: 16px;
        color: #555;
    }
</style>
""", unsafe_allow_html=True)

# En-tête de la page
st.markdown('<p class="main-header">Tableau de Bord</p>', unsafe_allow_html=True)

# Récupération des données
agents = get_data("agents")
tickets = get_data("tickets")

# Récupérer le dernier statut pour chaque ticket
if tickets:
    for ticket in tickets:
        events = get_data(f"tickets/{ticket['ticket_id']}/events")
        if events:
            # Trier les événements par date décroissante et prendre le premier
            latest_event = sorted(events, key=lambda x: x["heure"], reverse=True)[0]
            ticket["status"] = latest_event["statut"]
        else:
            ticket["status"] = "pending"  # Statut par défaut

# Conversion en DataFrame pour faciliter l'analyse
df_agents = pd.DataFrame(agents) if agents else pd.DataFrame()
df_tickets = pd.DataFrame(tickets) if tickets else pd.DataFrame()

# Préparation des métriques
total_agents = len(df_agents)
total_tickets = len(df_tickets)

# Calcul des tickets par statut
if not df_tickets.empty and "status" in df_tickets.columns:
    pending_tickets = df_tickets[df_tickets['status'] == 'pending'].shape[0]
    progress_tickets = df_tickets[df_tickets['status'] == 'in_progress'].shape[0]
    done_tickets = df_tickets[df_tickets['status'] == 'done'].shape[0]
    canceled_tickets = df_tickets[df_tickets['status'] == 'canceled'].shape[0]
else:
    pending_tickets = progress_tickets = done_tickets = canceled_tickets = 0

# Calcul du temps moyen de traitement (pour les tickets terminés)
avg_processing_time = "N/A"
if tickets:
    # Collecter tous les événements pour tous les tickets terminés
    processing_times = []
    for ticket in tickets:
        events = get_data(f"tickets/{ticket['ticket_id']}/events")
        if events:
            # Chercher l'événement de création (statut pending)
            creation_events = [e for e in events if e["statut"] == "pending"]
            # Chercher l'événement de clôture (statut done)
            done_events = [e for e in events if e["statut"] == "done"]
            
            if creation_events and done_events:
                creation_time = datetime.fromisoformat(creation_events[0]["heure"].replace("Z", "+00:00"))
                done_time = datetime.fromisoformat(done_events[0]["heure"].replace("Z", "+00:00"))
                processing_time = (done_time - creation_time).total_seconds() / 3600
                processing_times.append(processing_time)
    
    if processing_times:
        avg_hours = sum(processing_times) / len(processing_times)
        avg_processing_time = f"{avg_hours:.2f} heures"

# Affichage des métriques principales
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown('<p class="metric-label">Nombre d\'agents</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="metric-value">{total_agents}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown('<p class="metric-label">Total des tickets</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="metric-value">{total_tickets}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown('<p class="metric-label">Tickets en attente</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="metric-value">{pending_tickets}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown('<p class="metric-label">Temps moyen de traitement</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="metric-value">{avg_processing_time}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Graphiques
st.markdown("## Analyses détaillées")

# Disposition en colonnes pour les graphiques
col1, col2 = st.columns(2)

# Graphique 1: Tickets par statut
with col1:
    if not df_tickets.empty and "status" in df_tickets.columns:
        status_counts = df_tickets['status'].value_counts().reset_index()
        status_counts.columns = ['Statut', 'Nombre']
        
        fig = px.pie(
            status_counts, 
            values='Nombre', 
            names='Statut', 
            title='Répartition des tickets par statut',
            color_discrete_sequence=px.colors.sequential.Blues_r
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Pas de données pour afficher la répartition des tickets par statut")

# Graphique 2: Tickets par catégorie
with col2:
    if not df_tickets.empty:
        category_counts = df_tickets['categorie_service'].value_counts().reset_index()
        category_counts.columns = ['Catégorie', 'Nombre']
        
        fig = px.bar(
            category_counts, 
            x='Catégorie', 
            y='Nombre', 
            title='Tickets par catégorie',
            color='Nombre',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Pas de données pour afficher les tickets par catégorie")

# Graphique 3: Tickets traités par agent
if not df_tickets.empty and not df_agents.empty:
    # Compter le nombre de tickets par agent
    agent_ticket_counts = df_tickets['agent_id'].value_counts().reset_index()
    agent_ticket_counts.columns = ['agent_id', 'Nombre de tickets']
    
    # Fusionner avec les informations des agents
    agent_performance = pd.merge(
        agent_ticket_counts,
        df_agents[['agent_id', 'nom', 'prenoms']],
        on='agent_id'
    )
    
    # Créer une colonne pour le nom complet
    agent_performance['Nom complet'] = agent_performance['nom'] + ' ' + agent_performance['prenoms']
    
    # Créer le graphique
    fig = px.bar(
        agent_performance,
        x='Nom complet',
        y='Nombre de tickets',
        title='Tickets traités par agent',
        color='Nombre de tickets',
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Pas assez de données pour afficher les tickets traités par agent")

# Graphique 4: Évolution des tickets dans le temps
if not df_tickets.empty and 'date_creation' in df_tickets.columns:
    # Convertir la date de création en format datetime
    df_tickets['date_creation'] = pd.to_datetime(df_tickets['date_creation'])
    
    # Regrouper par jour
    tickets_by_day = df_tickets.groupby(df_tickets['date_creation'].dt.date).size().reset_index(name='count')
    tickets_by_day.columns = ['Date', 'Nombre de tickets']
    
    # S'assurer que toutes les dates sont présentes (y compris les jours sans tickets)
    if len(tickets_by_day) > 1:
        date_range = pd.date_range(start=tickets_by_day['Date'].min(), end=tickets_by_day['Date'].max())
        date_range_df = pd.DataFrame({'Date': date_range.date})
        tickets_by_day = pd.merge(date_range_df, tickets_by_day, on='Date', how='left').fillna(0)
    
    # Créer le graphique
    fig = px.line(
        tickets_by_day,
        x='Date',
        y='Nombre de tickets',
        title='Évolution quotidienne du nombre de tickets',
        markers=True
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Pas assez de données pour afficher l'évolution des tickets dans le temps")

# Pied de page
st.markdown("---")
st.markdown("© 2025 Smart Agence - Application de Gestion de Tickets")