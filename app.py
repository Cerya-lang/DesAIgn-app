import streamlit as st
import streamlit.components.v1 as components
import os
import json
import requests
import google.generativeai as genai
from google.oauth2 import service_account

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="DesAIgn Studio | ÉTS", page_icon="🎨", layout="wide")

# Récupération sécurisée des clés d'API depuis Railway
HF_TOKEN = os.environ.get('HF_TOKEN')
GOOGLE_JSON = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')

# --- INITIALISATION DE L'IA (Correction Erreur 401) ---
def init_gemini():
    try:
        if GOOGLE_JSON:
            info = json.loads(GOOGLE_JSON)
            cred = service_account.Credentials.from_service_account_info(info)
            genai.configure(credentials=cred)
            return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.sidebar.error(f"⚠️ Erreur de connexion Google : {e}")
    return None

model = init_gemini()

# --- INTERFACE : MENU LATÉRAL (SIDEBAR) ---
with st.sidebar:
    st.title("🎨 DesAIgn Dashboard")
    
    # Section Profil mise à jour pour Cerya @ ÉTS
    with st.expander("👤 Mon Compte", expanded=True):
        st.write("**Nom :** Cerya")
        st.write("**Institution :** ÉTS")
        st.write("**Statut :** Développeur Principal")
        st.write("**Plan :** Free Tier")
    
    with st.expander("💳 Abonnements & Crédits"):
        st.info("Système de crédits IA actif")
        st.radio("Forfaits disponibles :", ["Gratuit", "Pro (15$/m)", "Studio (45$/m)"])
        if st.button("Mettre à niveau le compte"):
            st.toast("Redirection vers la passerelle de paiement...")

    st.divider()
    st.subheader("🕰️ Historique de Recherche")
    st.caption("Analyses web récentes")
    st.button("📄 Hoodie Champion - Analyse Officielle", use_container_width=True)
    st.button("📄 Mercedes GT63 AMG - Specs", use_container_width=True)
    st.button("📄 Moonlight.off01 - Style Study", use_container_width=True)

# --- INTERFACE PRINCIPALE ---
st.title("DesAIgn | Studio de Recherche & Création")
st.caption("Assistant d'ingénierie design pour l'ÉTS - Propulsé par l'IA")

tabs = st.tabs(["💬 Analyse Web Profonde", "🧊 Moteur de Rendu 3D", "📞 War Room (ÉTS)"])

# --- ONGLET 1 : L'INTELLIGENCE DE RECHERCHE (DEEP-SEARCH) ---
with tabs[0]:
    if "messages" not in st.session_state: st.session_state.messages = []
    
    container = st.container(height=500)
    for m in st.session_state.messages:
        with container.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Demande une analyse (ex: Vêtement Champion, Nissan GTR, Nike...)"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with container.chat_message("user"): st.markdown(prompt)
        
        with container.chat_message("assistant"):
            if model:
                with st.spinner("DesAIgn Deep-Crawler : Analyse des sites officiels et réseaux sociaux..."):
                    # Logique universelle pour voitures, vêtements et marques de niche
                    instruction_universelle = f"""
                    Tu es l'agent 'Deep-DesAIgn'. Ta mission est d'analyser : "{prompt}".
                    
                    1. EXPLORATION DES SOURCES :
                       - Simule une recherche sur le site officiel de la marque pour extraire les matériaux, la coupe et les specs.
                       - Analyse Google Images et Pinterest pour la structure géométrique.
                       - Pour les marques Instagram (ex: moonlight.off01), analyse l'esthétique visuelle.
                    
                    2. SYNTHÈSE TECHNIQUE :
                       - Détaille les caractéristiques (ex: type de couture, aérodynamisme, matériaux PBR).
                    
                    3. MASTER PROMPT 3D :
                       - Génère un prompt final en ANGLAIS extrêmement précis pour la modélisation.
                    """
                    try:
                        response = model.generate_content(instruction_universelle)
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    except Exception as e:
                        st.error(f"Erreur d'analyse : {e}")
            else:
                st.error("L'IA n'est pas configurée. Vérifie tes variables GOOGLE sur Railway.")

# --- ONGLET 2 : MOTEUR 3D ---
with tabs[1]:
    st.subheader("Laboratoire de Modélisation 3D")
    st.write("Colle ici le 'Master Prompt' généré par l'IA pour créer ton objet.")
    
    prompt_3d = st.text_area("Prompt technique (Anglais) :", placeholder="A photorealistic 3D model of...")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Lancer la génération (Standard)", use_container_width=True):
            st.warning("Moteur Shap-E en attente de connexion...")
    with col2:
        st.button("Génération Haute Fidélité (Pro ✨)", disabled=True, use_container_width=True)

# --- ONGLET 3 : WAR ROOM (COLLABORATION) ---
with tabs[2]:
    st.subheader("Salon de Design Collaboratif - ÉTS")
    st.write("Présentez vos analyses web et vos modèles 3D à votre équipe en direct.")
    components.html("""
        <iframe allow="camera; microphone; display-capture; autoplay" 
        src="https://meet.jit.si/DesAIgn_Studio_ETS_Cerya" style="height: 600px; width: 100%; border:0; border-radius:15px;"></iframe>
    """, height=620)
