import streamlit as st
import streamlit.components.v1 as components
import os
import json
import requests
import google.generativeai as genai
from google.oauth2 import service_account

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="DesAIgn Studio | ÉTS", page_icon="🎨", layout="wide")

# RÉCUPÉRATION SÉCURISÉE DES SECRETS
# On utilise str() et on gère le cas où le secret n'existe pas du tout
HF_TOKEN = str(st.secrets.get('HF_TOKEN', ""))
# --- INITIALISATION IA ---
def init_gemini():
    try:
        api_key = st.secrets.get("GOOGLE_API_KEY")
        if not api_key:
            return None, "Secret GOOGLE_API_KEY introuvable."
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model, None
        
    except Exception as e:
        return None, f"Erreur système : {e}"

# On récupère le modèle ET l'erreur potentielle
model, error_msg = init_gemini()

# --- INTERFACE : MENU LATÉRAL (SIDEBAR) ---
with st.sidebar:
    st.title("🎨 DesAIgn Dashboard")
    with st.expander("👤 Mon Compte", expanded=True):
        st.write("**Nom :** Cerya")
        st.write("**Institution :** ÉTS")
        st.write("**Statut :** Développeur Principal")
    st.divider()
    st.caption("🌐 Langue : Détection automatique active")
    st.caption("🚀 Moteur 3D : Hugging Face Shap-E")

# --- INTERFACE PRINCIPALE ---
st.title("DesAIgn | Studio de Recherche & Création")
st.caption("Assistant d'ingénierie design pour l'ÉTS")

tabs = st.tabs(["💬 Analyse Multilingue", "🧊 Moteur 3D", "📞 War Room"])

with tabs[0]:
    if "messages" not in st.session_state: 
        st.session_state.messages = []
    
    container = st.container(height=500)
    for m in st.session_state.messages:
        with container.chat_message(m["role"]): 
            st.markdown(m["content"])

    if prompt := st.chat_input("Analyse n'importe quel vêtement ou véhicule au monde..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with container.chat_message("user"): 
            st.markdown(prompt)
        
        with container.chat_message("assistant"):
            if model:
                with st.spinner("Analyse approfondie en cours..."):
                    system_prompt = (
                        f"Tu es l'expert DesAIgn. RÉPONDS EXCLUSIVEMENT DANS LA LANGUE DU MESSAGE SUIVANT : '{prompt}'. "
                        f"Analyse les matériaux et le design de : {prompt}. "
                        "Termine obligatoirement par : 'MASTER PROMPT 3D (EN):' suivi d'une description technique en anglais."
                    )
                    try:
                        response = model.generate_content(system_prompt)
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    except Exception as e:
                        st.error(f"Erreur Gemini : {e}")
            else:
                # ICI : On affiche l'erreur réelle récupérée plus haut
                st.error(f"L'IA n'est pas connectée. {error_msg if error_msg else ''}")
                st.info("Vérifie que ton Secret dans Streamlit commence bien par ''' et finit par '''")

# --- (Le reste de ton code pour le Moteur 3D et War Room reste identique) ---
