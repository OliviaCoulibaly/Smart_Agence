import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="Smart Agence - Gestion de Tickets",
    page_icon="",
    layout="wide"
)

# URL de base de l'API
API_URL = "http://localhost:8000"

# Fonction pour obtenir les données depuis l'API
def get_data(endpoint):
    try:
        # Suppression du slash final pour éviter les erreurs 500
        if endpoint.endswith('/'):
            endpoint = endpoint[:-1]
            
        response = requests.get(f"{API_URL}/{endpoint}")
        response.raise_for_status()
        data = response.json()
        return data if isinstance(data, list) else []
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur lors de la récupération des données : {e}")
        return []

# Fonction pour créer un ticket
def create_ticket(agent_id, categorie_service, description=None):
    try:
        ticket_data = {
            "agent_id": agent_id,
            "categorie_service": categorie_service,
            "description": description
        }
        response = requests.post(f"{API_URL}/tickets", json=ticket_data)  # Pas de slash final
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur lors de la création du ticket : {e}")
        return None

# Style CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 42px;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 30px;
    }
    .sub-header {
        font-size: 26px;
        font-weight: bold;
        color: #1565C0;
        margin-top: 20px;
        margin-bottom: 15px;
    }
    .card {
        padding: 20px;
        border-radius: 5px;
        background-color: #f8f9fa;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# En-tête de l'application
st.markdown('<p class="main-header">Smart Agence - Gestion de Tickets</p>', unsafe_allow_html=True)

# Section d'information
with st.container():
    st.markdown('<p class="sub-header">Bienvenue sur l\'application de gestion de tickets</p>', unsafe_allow_html=True)
    st.markdown("""
    Cette application vous permet de gérer les tickets clients de votre agence. Vous pouvez :
    - Créer et gérer des tickets clients
    - Suivre l'état des tickets en temps réel
    - Visualiser des statistiques sur les performances des agents
    
    Utilisez le menu latéral pour naviguer entre les différentes sections.
    """)

# État de l'API
api_status = st.empty()

# Actions rapides
st.markdown('<p class="sub-header">Actions rapides</p>', unsafe_allow_html=True)
col1, col2 = st.columns(2)

# Vérifier si l'API est disponible
try:
    requests.get(f"{API_URL}/")
    api_online = True
except:
    api_online = False
    api_status.error("⚠️ API non disponible. Certaines fonctionnalités peuvent ne pas fonctionner correctement.")

# Colonne de création de ticket
with col1:
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Créer un nouveau ticket")

        agents = get_data("agents")
        if agents:
            agent_options = {f"{agent['nom']} {agent['prenoms']}": agent['agent_id'] for agent in agents}
            selected_agent = st.selectbox("Sélectionner un agent", list(agent_options.keys()))
            categorie_service = st.selectbox("Catégorie du service", ["transaction", "conseil"])
            description = st.text_area("Description du ticket", height=100)

            if st.button("Créer le ticket"):
                agent_id = agent_options[selected_agent]
                result = create_ticket(agent_id, categorie_service, description)
                if result:
                    ticket_id = result.get("ticket_id", "N/A")
                    st.success(f"✅ Ticket créé avec succès ! ID : {ticket_id}")
        else:
            st.warning(" Aucun agent disponible. Veuillez en ajouter d'abord.")
        st.markdown('</div>', unsafe_allow_html=True)

# Colonne des tickets récents
with col2:
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Tickets récents")

        # Récupération des tickets (sans slash final)
        tickets = get_data("tickets")
        if tickets:
            # Limiter à 5 tickets côté client
            recent_tickets = tickets[:5] if len(tickets) > 5 else tickets
            df_tickets = pd.DataFrame(recent_tickets)
            if not df_tickets.empty:
                # Vérifier si la colonne created_at existe
                if "created_at" in df_tickets.columns:
                    df_tickets["created_at"] = pd.to_datetime(df_tickets["created_at"]).dt.strftime("%d/%m/%Y %H:%M")
                
                # Vérifier quelles colonnes sont présentes dans le dataframe
                available_columns = ["ticket_id", "agent_id"]
                if "categorie_service" in df_tickets.columns:
                    available_columns.append("categorie_service")
                elif "category" in df_tickets.columns:  # Alternative si le nom de la colonne est différent
                    available_columns.append("category")
                    
                if "status" in df_tickets.columns:
                    available_columns.append("status")
                if "created_at" in df_tickets.columns:
                    available_columns.append("created_at")
                
                column_config = {
                    "ticket_id": "ID du ticket",
                    "agent_id": "ID de l'agent"
                }
                
                if "categorie_service" in df_tickets.columns:
                    column_config["categorie_service"] = "Catégorie"
                elif "category" in df_tickets.columns:
                    column_config["category"] = "Catégorie"
                    
                if "status" in df_tickets.columns:
                    column_config["status"] = "Statut"
                if "created_at" in df_tickets.columns:
                    column_config["created_at"] = "Date de création"
                
                st.dataframe(
                    df_tickets[available_columns],
                    column_config=column_config,
                    use_container_width=True
                )
            else:
                st.info("Aucun ticket à afficher.")
        else:
            st.info("Aucun ticket récent à afficher.")
        st.markdown('</div>', unsafe_allow_html=True)

# Pied de page
st.markdown("---")
st.markdown("© 2025 Smart Agence - Application de Gestion de Tickets")