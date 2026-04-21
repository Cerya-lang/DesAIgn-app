import streamlit as st
import re
from huggingface_hub import InferenceClient
import requests
import streamlit.components.v1 as components
from datetime import datetime
import uuid

st.set_page_config(
    page_title="DesAIgn Studio | ÉTS",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== SESSION STATE ======================
if "user" not in st.session_state:
    st.session_state.user = None

if "subscription" not in st.session_state:
    st.session_state.subscription = "Free"

if "current_ai" not in st.session_state:
    st.session_state.current_ai = "Gemini 2.5 Flash"

if "history" not in st.session_state:
    st.session_state.history = []

if "saved_models" not in st.session_state:
    st.session_state.saved_models = []

if "messages" not in st.session_state:
    st.session_state.messages = []

if "rooms" not in st.session_state:
    st.session_state.rooms = {}

if "current_room" not in st.session_state:
    st.session_state.current_room = None

# ====================== SIDEBAR ======================
with st.sidebar:
    st.title("🎨 DesAIgn Studio")
    
    # Connexion
    if st.session_state.user is None:
        st.markdown("### 👤 Connexion")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔑 Se connecter avec Google", use_container_width=True):
                st.session_state.user = {"name": "Cerya", "email": "cerya@etsmtl.ca", "avatar": "🎨"}
                st.success("✅ Connecté avec Google")
                st.rerun()
        with col2:
            if st.button("Créer un compte", use_container_width=True):
                st.info("Création de compte bientôt disponible")
        
        st.divider()
        email = st.text_input("Email", placeholder="ton@email.com")
        if st.button("Se connecter avec email", use_container_width=True):
            if email:
                st.session_state.user = {"name": email.split("@")[0].title(), "email": email, "avatar": "👤"}
                st.success("✅ Connecté")
                st.rerun()
    else:
        st.success(f"✅ {st.session_state.user['avatar']} {st.session_state.user['name']}")
        st.write(st.session_state.user["email"])
        if st.button("🚪 Déconnexion", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    st.divider()

    # Choix du modèle IA
    st.caption("🤖 Modèle IA")
    st.session_state.current_ai = st.selectbox(
        "Modèle actif",
        ["Gemini 2.5 Flash", "Grok 4", "ChatGPT-4o", "Claude 3.5 Sonnet"],
        index=0
    )

    st.divider()

    # Navigation
    page = st.radio(
        "Navigation",
        ["🏠 Accueil", "💬 Analyse Multilingue", "🧊 Moteur 3D", "📞 War Room", "📚 Bibliothèque"],
        label_visibility="collapsed"
    )

# ====================== ACCUEIL ======================
if page == "🏠 Accueil":
    st.title("🎨 DesAIgn Studio")
    st.subheader("L'assistant d'ingénierie design de l'ÉTS")

    if st.session_state.user:
        st.success(f"Bienvenue {st.session_state.user['name']} !")
    else:
        st.warning("🔒 Connecte-toi pour débloquer toutes les fonctionnalités")

    # Abonnements
    st.markdown("### 💎 Abonnements")
    cols = st.columns(3)
    with cols[0]:
        st.metric("Free", "0 $")
        st.write("Gemini Flash\n50 générations 3D/jour\nChat basique")
        st.button("Utiliser gratuitement", use_container_width=True)
    with cols[1]:
        st.metric("Pro", "19 $/mois", "Recommandé")
        st.write("• Tous les modèles IA\n• Génération 3D illimitée\n• Sauvegarde illimitée\n• War Room HD")
        if st.button("Passer à Pro", type="primary", use_container_width=True):
            st.session_state.subscription = "Pro"
            st.toast("✅ Abonnement Pro activé (simulation)")
    with cols[2]:
        st.metric("Team / ÉTS", "49 $/mois")
        st.write("Collaboration avancée\nPartage de modèles\nSupport priorité")
        st.button("Choisir Team", use_container_width=True)

    # Historique rapide
    st.markdown("### 📜 Historique récent")
    if st.session_state.history:
        for item in st.session_state.history[-8:]:
            st.caption(f"• {item['date']} — **{item['type']}** : {item['title']}")
    else:
        st.info("Aucune activité pour l’instant. Commence une analyse ou un modèle 3D !")

# ====================== ANALYSE MULTILINGUE ======================
elif page == "💬 Analyse Multilingue":
    st.subheader("💬 Analyse Multilingue")
    container = st.container(height=550)
    for m in st.session_state.messages:
        with container.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("Analyse n'importe quel vêtement ou véhicule au monde..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.history.append({"type": "Analyse", "title": prompt[:40], "date": datetime.now().strftime("%H:%M")})
        with container.chat_message("user"):
            st.markdown(prompt)
        with container.chat_message("assistant"):
            st.info("🔴 Gemini est limité pour le moment. Analyse simulée.")
            st.session_state.messages.append({"role": "assistant", "content": "Analyse détaillée simulée en attente de quota."})

# ====================== MOTEUR 3D ======================
elif page == "🧊 Moteur 3D":
    st.subheader("🧊 Moteur 3D")
    last_prompt = ""
    for msg in reversed(st.session_state.messages):
        match = re.search(r"MASTER PROMPT 3D \(EN\):\s*(.*)", msg.get("content", ""), re.DOTALL | re.IGNORECASE)
        if match:
            last_prompt = match.group(1).strip()
            break

    current_prompt = st.text_area("Prompt 3D", value=last_prompt, height=180, placeholder="Décris ta voiture ou ton vêtement en détail...")
    
    if st.button("🚀 Générer avec Shap-E", type="primary"):
        st.info("Génération Shap-E en cours (simulation)...")
        st.session_state.history.append({"type": "Modèle 3D", "title": "Nouveau modèle", "date": datetime.now().strftime("%H:%M")})
        st.success("Modèle généré ! (dans la vraie version Shap-E fonctionnera)")

    st.caption("Pour modifier : copie le prompt et va sur Spline ou Tripo Studio")

# ====================== WAR ROOM ======================
elif page == "📞 War Room":
    st.subheader("📞 War Room – Collaboration en direct")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Créer une nouvelle salle", type="primary", use_container_width=True):
            code = str(uuid.uuid4())[:8].upper()
            st.session_state.rooms[code] = {"name": f"Salle {code}", "messages": []}
            st.success(f"Salle créée ! Code : **{code}**")
            st.info(f"Lien Jitsi : https://meet.jit.si/DesAIgn-{code}")
    with col2:
        code = st.text_input("Rejoindre une salle (code)")
        if st.button("Rejoindre la salle", use_container_width=True) and code:
            st.session_state.current_room = code.upper()
            st.success(f"Connecté à la salle {code.upper()}")

    if st.session_state.current_room and st.session_state.current_room in st.session_state.rooms:
        room = st.session_state.rooms[st.session_state.current_room]
        st.write(f"**Salle active :** {room['name']}")
        # Chat
        for m in room["messages"]:
            st.chat_message(m["role"]).markdown(m["content"])
        if msg := st.chat_input("Message dans le War Room..."):
            room["messages"].append({"role": "user", "content": msg})
            st.rerun()

# ====================== BIBLIOTHÈQUE ======================
elif page == "📚 Bibliothèque":
    st.subheader("📚 Ma Bibliothèque de Modèles")
    if st.session_state.saved_models:
        for model in st.session_state.saved_models:
            with st.expander(model["name"]):
                st.write(model["prompt"])
    else:
        st.info("Aucun modèle sauvegardé pour l’instant.")

st.caption("DesAIgn Studio | École de Technologie Supérieure (ÉTS) — Version complète Avril 2026")
