import streamlit as st
import os
import json
import requests
import google.generativeai as genai
from google.oauth2 import service_account

# --- CONFIGURATION ---
st.set_page_config(page_title="DesAIgn Studio | ÉTS", page_icon="🎨", layout="wide")

HF_TOKEN = os.environ.get('HF_TOKEN')
GOOGLE_JSON = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')

# --- INITIALISATION IA (Correction 404 stable) ---
def init_gemini():
    try:
        if GOOGLE_JSON:
            info = json.loads(GOOGLE_JSON)
            cred = service_account.Credentials.from_service_account_info(info)
            genai.configure(credentials=cred)
            # Utilisation de la version stable pour éviter l'erreur 404 v1beta
            return genai.GenerativeModel('gemini-1.5-flash')
    except Exception:
        return None
    return None

model = init_gemini()

# --- SIDEBAR (PROFIL) ---
with st.sidebar:
    st.title("🎨 DesAIgn Dashboard")
    with st.expander("👤 Mon Compte", expanded=True):
        st.write("**Nom :** Cerya")
        st.write("**Institution :** ÉTS")
        st.write("**Statut :** Développeur Principal")
    st.divider()
    st.caption("🌐 Détection de langue intelligente active")

# --- INTERFACE PRINCIPALE ---
st.title("DesAIgn | Studio de Recherche & Création")

tabs = st.tabs(["💬 Analyse Multilingue", "🧊 Moteur 3D", "📞 War Room"])

# --- ONGLET 1 : ANALYSE ---
with tabs[0]:
    if "messages" not in st.session_state: st.session_state.messages = []
    
    container = st.container(height=450)
    for m in st.session_state.messages:
        with container.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Écris en français, anglais, japonais..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with container.chat_message("user"): st.markdown(prompt)
        
        with container.chat_message("assistant"):
            if model:
                with st.spinner("Analyse en cours..."):
                    # Instruction stricte pour la langue
                    instr = f"Tu es l'IA DesAIgn. RÉPONDS TOUJOURS DANS LA LANGUE DU PROMPT: {prompt}. Analyse le design et termine par un 'MASTER PROMPT 3D (EN):' détaillé."
                    try:
                        response = model.generate_content(instr)
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    except Exception as e:
                        st.error(f"Erreur d'analyse : {e}")
            else:
                st.error("Erreur de connexion Gemini. Vérifie tes identifiants Google.")

# --- ONGLET 2 : MOTEUR 3D ---
with tabs[1]:
    st.subheader("Générateur 3D Haute Fidélité")
    user_prompt_3d = st.text_area("Master Prompt 3D (en anglais) :", height=100)
    
    if st.button("Lancer la fabrication"):
        if not HF_TOKEN:
            st.error("Token Hugging Face manquant dans Railway.")
        else:
            with st.spinner("Calcul des polygones..."):
                API_URL = "https://api-inference.huggingface.co/models/openai/shap-e"
                headers = {"Authorization": f"Bearer {HF_TOKEN}"}
                res = requests.post(API_URL, headers=headers, json={"inputs": user_prompt_3d})
                if res.status_code == 200:
                    st.success("✅ Objet 3D prêt !")
                    st.balloons()
                else:
                    st.error("Le moteur 3D est occupé. Réessaie dans 10 secondes.")
