import streamlit as st
import requests
import pandas as pd

API_BASE_URL = "http://localhost:8000"
CATEGORIES = ["transaction", "conseil"]
STATUSES = ["pending", "in_progress", "done", "canceled"]

# Fonction générique pour les appels API
def api_request(method, endpoint, data=None):
    try:
        url = f"{API_BASE_URL}/{endpoint}"
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        response.raise_for_status()
        return response.json() if method != "DELETE" else response.status_code == 204
    except requests.RequestException as e:
        st.error(f"❌ Erreur API: {e}")
        return [] if method == "GET" else None

# Fonctions API spécifiques
def get_agents():
    return api_request("GET", "agents")

def get_tickets():
    return api_request("GET", "tickets")

def get_ticket_events(ticket_id):
    return api_request("GET", f"tickets/{ticket_id}/events")

def create_agent(nom, prenoms, annee_naissance, categorie, email, telephone):
    return api_request("POST", "agents/", {
        "nom": nom, "prenoms": prenoms, "annee_naissance": annee_naissance,
        "categorie": categorie, "email": email, "telephone": telephone
    })

def update_agent(agent_id, data):
    return api_request("PUT", f"agents/{agent_id}", data)

def delete_agent(agent_id):
    return api_request("DELETE", f"agents/{agent_id}")

def create_ticket(agent_id, categorie_service, description=""):
    return api_request("POST", "tickets/", {
        "agent_id": agent_id, "categorie_service": categorie_service, "description": description
    })

def update_ticket_status(ticket_id, agent_id, statut):
    return api_request("POST", f"tickets/{ticket_id}/status", {
        "agent_id": agent_id, "ticket_id": ticket_id, "statut": statut
    })

# Interface Streamlit
st.set_page_config(page_title="Administration", layout="wide")
st.title("🎫 Administration des Agents et Tickets")

agents = get_agents()
tickets = get_tickets()

# Récupérer le dernier statut pour chaque ticket
if tickets:
    for ticket in tickets:
        events = get_ticket_events(ticket["ticket_id"])
        if events:
            # Trier les événements par date décroissante et prendre le premier
            latest_event = sorted(events, key=lambda x: x["heure"], reverse=True)[0]
            ticket["status"] = latest_event["statut"]
        else:
            ticket["status"] = "pending"  # Statut par défaut

agent_map = {f"{a['nom']} {a['prenoms']}": a["agent_id"] for a in agents}
agent_names = {a["agent_id"]: f"{a['nom']} {a['prenoms']}" for a in agents}

tab1, tab2 = st.tabs(["👤 Gestion des Agents", "📋 Gestion des Tickets"])

# Onglet Agents
with tab1:
    with st.expander("➕ Ajouter un agent", expanded=True):
        with st.form("form_add_agent", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            nom = col1.text_input("Nom *")
            prenoms = col2.text_input("Prénoms *")
            email = col3.text_input("Email *")

            col4, col5, col6 = st.columns(3)
            annee = col4.number_input("Année de naissance", 1950, 2025, step=1)
            categorie = col5.selectbox("Catégorie", CATEGORIES)
            telephone = col6.text_input("Téléphone")

            submit = st.form_submit_button("Créer l'agent")
            if submit and nom and prenoms and email:
                if create_agent(nom, prenoms, annee, categorie, email, telephone):
                    st.success("✅ Agent ajouté")
                    st.rerun()

    if agents:
        st.divider()
        st.subheader("👥 Liste des agents")
        df = pd.DataFrame(agents)
        st.dataframe(df[["agent_id", "nom", "prenoms", "categorie", "email"]])

        with st.expander("✏️ Modifier un agent"):
            selected = st.selectbox("Choisir un agent", list(agent_map.keys()))
            agent_id = agent_map[selected]
            agent = next(a for a in agents if a["agent_id"] == agent_id)

            with st.form("edit_agent_form"):
                col1, col2, col3 = st.columns(3)
                nom = col1.text_input("Nom", agent["nom"])
                prenoms = col2.text_input("Prénoms", agent["prenoms"])
                email = col3.text_input("Email", agent["email"])

                col4, col5, col6 = st.columns(3)
                annee = col4.number_input("Année", 1950, 2025, value=agent["annee_naissance"])
                categorie = col5.selectbox("Catégorie", CATEGORIES, index=CATEGORIES.index(agent["categorie"]))
                telephone = col6.text_input("Téléphone", agent["telephone"] or "")

                col7, col8 = st.columns(2)
                if col7.form_submit_button("Mettre à jour"):
                    data = {"nom": nom, "prenoms": prenoms, "annee_naissance": annee,
                            "categorie": categorie, "email": email, "telephone": telephone}
                    if update_agent(agent_id, data):
                        st.success("✅ Agent mis à jour")
                        st.rerun()
                if col8.form_submit_button("Supprimer"):
                    if delete_agent(agent_id):
                        st.success("✅ Agent supprimé")
                        st.rerun()
    else:
        st.info("Aucun agent enregistré.")

# Onglet Tickets
with tab2:
    with st.expander("➕ Créer un ticket", expanded=True):
        if agents:
            with st.form("add_ticket_form"):
                col1, col2 = st.columns(2)
                agent_name = col1.selectbox("Agent responsable", list(agent_map.keys()))
                categorie = col2.selectbox("Catégorie", CATEGORIES)
                description = st.text_area("Description (facultatif)")

                if st.form_submit_button("Créer le ticket"):
                    if create_ticket(agent_map[agent_name], categorie, description):
                        st.success("✅ Ticket créé")
                        st.rerun()
        else:
            st.warning("Ajoutez d'abord un agent")

    if tickets:
        st.divider()
        st.subheader("📋 Liste des tickets")

        # Ajout nom agent
        for t in tickets:
            t["agent_nom"] = agent_names.get(t["agent_id"], "Inconnu")

        df = pd.DataFrame(tickets)

        # Filtres
        st.markdown("### 🔍 Filtres")
        col1, col2, col3 = st.columns(3)
        filtre_agent = col1.selectbox("Agent", ["Tous"] + list(agent_map.keys()))
        filtre_cat = col2.selectbox("Catégorie", ["Toutes"] + CATEGORIES)
        filtre_statut = col3.selectbox("Statut", ["Tous"] + STATUSES)

        filtered_df = df.copy()
        if filtre_agent != "Tous":
            filtered_df = filtered_df[filtered_df["agent_nom"] == filtre_agent]
        if filtre_cat != "Toutes":
            filtered_df = filtered_df[filtered_df["categorie_service"] == filtre_cat]
        if filtre_statut != "Tous" and "status" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["status"] == filtre_statut]

        st.dataframe(filtered_df[["ticket_id", "categorie_service", "status", "agent_nom"]])

        with st.expander("🔄 Modifier le statut d'un ticket"):
            ticket_options = [f"#{t['ticket_id']} - {t['categorie_service']}" for t in filtered_df.to_dict("records")]
            if ticket_options:
                selected_ticket_label = st.selectbox("Sélectionner un ticket", ticket_options)
                selected_ticket_id = int(selected_ticket_label.split("#")[1].split(" -")[0])
                selected_ticket = next(t for t in tickets if t['ticket_id'] == selected_ticket_id)

                with st.form("update_status_form"):
                    col1, col2 = st.columns(2)
                    new_agent = col1.selectbox("Reassigner à", ["-- inchangé --"] + list(agent_map.keys()))
                    new_status = col2.selectbox("Nouveau statut", STATUSES)

                    if st.form_submit_button("Mettre à jour"):
                        agent_id = selected_ticket["agent_id"]
                        if new_agent != "-- inchangé --":
                            agent_id = agent_map[new_agent]
                        if update_ticket_status(selected_ticket["ticket_id"], agent_id, new_status):
                            st.success("✅ Statut mis à jour")
                            st.rerun()

        with st.expander("📜 Historique d'un ticket"):
            selected = st.selectbox("Ticket pour historique", [f"#{t['ticket_id']}" for t in filtered_df.to_dict("records")])
            ticket_id = int(selected.strip("#"))
            events = get_ticket_events(ticket_id)
            if events:
                df_events = pd.DataFrame(events)
                df_events["date"] = pd.to_datetime(df_events["heure"]).dt.strftime("%d/%m/%Y %H:%M")
                df_events["agent"] = df_events["agent_id"].map(agent_names)
                st.dataframe(df_events[["date", "statut", "agent"]])
            else:
                st.info("Aucun événement pour ce ticket.")
    else:
        st.info("Aucun ticket enregistré.")