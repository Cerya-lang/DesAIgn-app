import streamlit as st
import streamlit.components.v1 as components
import os
import json
import google.generativeai as genai
from google.oauth2 import service_account

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Onirai Design Studio", page_icon="⛩️", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stTextInput>div>div>input { background-color: #262730; color: white; }
    .stChatMessage { background-color: #1e1e24; border-radius: 10px; padding: 10px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION DE L'HISTORIQUE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- CONNEXION À GEMINI ---
try:
    if 'GOOGLE_APPLICATION_CREDENTIALS_JSON' in os.environ:
        service_account_info = json.loads(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON'))
        scoped_credentials = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        genai.configure(credentials=scoped_credentials)
        model = genai.GenerativeModel('gemini-1.5-flash')
    else:
        st.error("Variable d'environnement manquante sur Railway.")
except Exception as e:
    st.error(f"Erreur de configuration : {e}")

st.title("⛩️ Onirai | Hub de Création")
st.caption("Studio de design, génération 3D et collaboration en temps réel")
st.divider()

# --- CRÉATION DES ONGLETS (L'architecture de ton SaaS) ---
tab_studio, tab_3d, tab_equipe = st.tabs(["🎨 Studio IA", "🧊 Générateur 3D", "📞 War Room (Équipe)"])

# ==========================================
# ONGLET 1 : LE STUDIO IA (Ce qu'on avait avant)
# ==========================================
with tab_studio:
    col_visuel, col_chat = st.columns([3, 2])
    
    with col_visuel:
        st.subheader("Concept Board")
        st.info("Ici apparaîtront les spécifications techniques de tes designs (ex: matériaux du hoodie, specs du moteur).")
        with st.container(height=400, border=True):
            st.write("En attente d'une analyse...")

    with col_chat:
        st.subheader("Assistant Onirai")
        chat_container = st.container(height=400, border=True)
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

    if prompt := st.chat_input("Demande un conseil ou analyse un concept..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)
        with chat_container:
            with st.chat_message("assistant"):
                with st.spinner("Analyse..."):
                    try:
                        system_prompt = f"Tu es 'Onirai', expert en design et tendances. Demande : {prompt}"
                        response = model.generate_content(system_prompt)
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    except Exception as e:
                        st.error(f"Erreur : {e}")

# ==========================================
# ONGLET 2 : GÉNÉRATION ET VISIONNEUSE 3D
# ==========================================
with tab_3d:
    st.subheader("API de Modélisation 3D (Meshy / Luma)")
    st.write("Génère un modèle 3D à partir d'un prompt texte et manipule-le ici.")
    
    prompt_3d = st.text_input("Que veux-tu modéliser en 3D ? (ex: Un masque Oni cybernétique)")
    
    if st.button("Générer le modèle 3D (Simulation)"):
        if prompt_3d:
            st.success("Requête envoyée à l'API 3D. (Nécessite une clé API Meshy ou Luma AI pour fonctionner réellement)")
            
            # --- VISIONNEUSE 3D INTÉGRÉE ---
            # On utilise le composant Google <model-viewer> pour afficher un modèle 3D interactif
            # J'ai mis un modèle de test d'astronaute par défaut pour te montrer que ça tourne à la souris !
            components.html("""
                <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.3.0/model-viewer.min.js"></script>
                <style>
                    model-viewer {
                        width: 100%;
                        height: 500px;
                        background-color: #1e1e24;
                        border-radius: 10px;
                    }
                </style>
                <model-viewer 
                    src="https://modelviewer.dev/shared-assets/models/Astronaut.glb" 
                    camera-controls 
                    auto-rotate 
                    shadow-intensity="1">
                </model-viewer>
            """, height=520)
        else:
            st.warning("Écris un prompt d'abord.")

# ==========================================
# ONGLET 3 : LA WAR ROOM (APPEL DE GROUPE)
# ==========================================
with tab_equipe:
    st.subheader("Salle de réunion cryptée")
    st.write("Reste en contact avec tes associés et designers pendant la création.")
    
    # Intégration de Jitsi Meet : un clic et la caméra/micro s'activent pour le groupe
    # Le nom du salon est "OniraiDesignTeam"
    components.html("""
        <iframe allow="camera; microphone; display-capture; autoplay; clipboard-write"
        src="https://meet.jit.si/OniraiDesignTeam"
        style="height: 600px; width: 100%; border: 0px; border-radius: 10px;">
        </iframe>
    """, height=620)
