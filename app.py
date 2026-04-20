import streamlit as st
import streamlit.components.v1 as components
import os
import json
import requests
import google.generativeai as genai
from google.oauth2 import service_account

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="DesAIgn Studio | ÉTS", page_icon="🎨", layout="wide")

# À METTRE À LA PLACE
# Force la conversion en chaîne de caractères pour éviter les erreurs de format
HF_TOKEN = str(st.secrets.get('HF_TOKEN', ""))
GOOGLE_JSON = str(st.secrets.get('GOOGLE_SERVICE_ACCOUNT_INFO', ""))

# --- INITIALISATION IA (Correction Force Stable) ---
def init_gemini():
    try:
        if GOOGLE_JSON is not None:
            info = json.loads(str(GOOGLE_JSON))
            cred = service_account.Credentials.from_service_account_info(info)
            # Utilisation de la version stable pour éviter l'erreur 404
            genai.configure(credentials=cred)
            return genai.GenerativeModel(model_name='gemini-1.5-flash')
    except Exception:
        return None
    return None

model = init_gemini()

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

# --- ONGLET 1 : ANALYSE ---
with tabs[0]:
    if "messages" not in st.session_state: 
        st.session_state.messages = []
    
    container = st.container(height=500)
    for m in st.session_state.messages:
        with container.chat_message(m["role"]): 
            st.markdown(m["content"])

    # Placeholder universel demandé
    if prompt := st.chat_input("Analyse n'importe quel vêtement ou véhicule au monde..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with container.chat_message("user"): 
            st.markdown(prompt)
        
        with container.chat_message("assistant"):
            if model:
                with st.spinner("Analyse approfondie en cours..."):
                    # Instruction système pour forcer la langue du prompt utilisateur
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
                        st.error(f"Erreur d'accès à l'IA : {e}")
            else:
                st.error("L'IA n'est pas connectée. Vérifie tes Secrets dans Streamlit Cloud.")

# --- ONGLET 2 : MOTEUR 3D ---
with tabs[1]:
    st.subheader("Laboratoire de Modélisation 3D")
    st.info("Colle ici la description technique générée par l'analyse.")
    
    # "Master Prompt 3D :" simplifié (sans mention English)
    user_prompt_3d = st.text_area("Master Prompt 3D :", height=150)
    
    if st.button("Lancer la fabrication de l'objet"):
        if not HF_TOKEN:
            st.error("Le Token Hugging Face est manquant dans Railway.")
        elif not user_prompt_3d:
            st.warning("Veuillez entrer un prompt technique.")
        else:
            with st.spinner("Génération des polygones en cours..."):
                API_URL = "https://api-inference.huggingface.co/models/openai/shap-e"
                headers = {"Authorization": f"Bearer {HF_TOKEN}"}
                try:
                    res = requests.post(API_URL, headers=headers, json={"inputs": user_prompt_3d})
                    if res.status_code == 200:
                        st.success("✅ Modèle 3D généré avec succès !")
                        st.balloons()
                    else:
                        st.error(f"Le serveur 3D est saturé (Code {res.status_code}). Réessaie dans 20 secondes.")
                except Exception as e:
                    st.error(f"Erreur de connexion : {e}")

# --- ONGLET 3 : WAR ROOM ---
with tabs[2]:
    components.html("""
        <iframe allow="camera; microphone; display-capture; autoplay" 
        src="https://meet.jit.si/DesAIgn_Studio_ETS_Cerya" 
        style="height: 600px; width: 100%; border:0; border-radius:15px;"></iframe>
    """, height=620)
