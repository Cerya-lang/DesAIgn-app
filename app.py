import streamlit as st
import google.generativeai as genai
import re
import streamlit.components.v1 as components

# ====================== CONFIGURATION ======================
st.set_page_config(
    page_title="DesAIgn Studio | ÉTS",
    page_icon="🎨",
    layout="wide"
)

# --- Secrets ---
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY")
HF_TOKEN = st.secrets.get("HF_TOKEN", "")

# --- Initialisation Gemini ---
def init_gemini():
    try:
        if not GOOGLE_API_KEY:
            return None, "Clé Google API manquante dans les secrets."
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")
        return model, None
    except Exception as e:
        return None, f"Erreur Gemini : {str(e)}"

model, gemini_error = init_gemini()

# ====================== INTERFACE ======================
st.title("🎨 DesAIgn | Studio de Recherche & Création")
st.caption("Analyse multilingue + Génération & Modification 3D interactive pour voitures et vêtements")

with st.sidebar:
    st.title("🎨 DesAIgn Dashboard")
    with st.expander("👤 Mon Compte", expanded=True):
        st.write("**Nom :** Cerya")
        st.write("**Institution :** ÉTS")
        st.write("**Statut :** Développeur Principal")
    
    st.divider()
    st.caption("🌐 Langue : Détection automatique")
    st.caption("🚀 Moteur 3D : Remix + Visualiseur interactif")

    if model:
        st.success("✅ Gemini connecté")
    else:
        st.error("❌ Gemini non connecté")

# ====================== TABS ======================
tab1, tab2, tab3 = st.tabs(["💬 Analyse Multilingue", "🧊 Moteur 3D", "📞 War Room"])

# ====================== TAB 1 : ANALYSE MULTILINGUE ======================
with tab1:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    container = st.container(height=520)

    for msg in st.session_state.messages:
        with container.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Analyse n'importe quel vêtement ou véhicule au monde..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with container.chat_message("user"):
            st.markdown(prompt)

        with container.chat_message("assistant"):
            if model:
                with st.spinner("Analyse approfondie en cours..."):
                    system_prompt = (
                        f"Tu es l'expert DesAIgn. RÉPONDS EXCLUSIVEMENT DANS LA LANGUE DU MESSAGE : '{prompt}'. "
                        f"Analyse en détail les matériaux, la construction, l'ergonomie et le design de : {prompt}. "
                        "Termine **obligatoirement** par : 'MASTER PROMPT 3D (EN):' suivi d'une description technique très détaillée en anglais, "
                        "optimisée pour la génération 3D (forme, proportions, textures, couleurs, matériaux, détails...)."
                    )
                    try:
                        response = model.generate_content(system_prompt)
                        text = response.text
                        st.markdown(text)
                        st.session_state.messages.append({"role": "assistant", "content": text})
                    except Exception as e:
                        st.error(f"Erreur Gemini : {e}")
            else:
                st.error(f"Gemini non disponible. {gemini_error}")

# ====================== TAB 2 : MOTEUR 3D (Complet avec Remix + Visualiseur) ======================
with tab2:
    st.subheader("🧊 Moteur 3D Interactif – Voitures & Vêtements")

    # Extraction automatique du dernier MASTER PROMPT
    last_master_prompt = ""
    for msg in reversed(st.session_state.get("messages", [])):
        if msg["role"] == "assistant":
            match = re.search(r"MASTER PROMPT 3D \(EN\):\s*(.*)", msg["content"], re.DOTALL | re.IGNORECASE)
            if match:
                last_master_prompt = match.group(1).strip()
                break

    col_prompt, col_viewer = st.columns([1, 1])

    with col_prompt:
        st.write("**Prompt 3D actuel**")
        current_prompt = st.text_area(
            "Prompt 3D (modifiable)",
            value=last_master_prompt,
            height=180,
            key="current_3d_prompt"
        )

        # Remix / Modification
        st.write("**🔧 Modifier ou créer une nouvelle version**")
        remix_instruction = st.text_input(
            "Décris la modification souhaitée :",
            placeholder="Ajoute des bandes rouges racing, style cyberpunk, couleur bleu métallisé, nouvelle tenue streetwear..."
        )

        if st.button("✨ Appliquer le remix avec Gemini", type="primary"):
            if model and current_prompt.strip():
                with st.spinner("Mise à jour du design..."):
                    remix_system = (
                        f"Voici le prompt 3D actuel :\n\n{current_prompt}\n\n"
                        f"Modifie-le selon cette demande : '{remix_instruction}'.\n"
                        "Retourne UNIQUEMENT le nouveau prompt 3D complet, très détaillé, en anglais."
                    )
                    try:
                        response = model.generate_content(remix_system)
                        new_prompt = response.text.strip()
                        st.session_state.current_3d_prompt = new_prompt
                        st.success("✅ Nouveau design généré !")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur lors du remix : {e}")
            else:
                st.warning("Le prompt est vide ou Gemini n'est pas connecté.")

        st.caption("Copie ce prompt dans Meshy.ai, Tripo.ai ou 3D AI Studio pour générer le fichier .glb")

    # Visualiseur 3D Interactif
    with col_viewer:
        st.write("**Visualiseur 3D (rotation 360°)**")

        glb_url = st.text_input(
            "Colle l'URL du fichier .glb ici :",
            placeholder="https://ton-fichier.glb",
            key="glb_url_input"
        )

        if glb_url:
            model_viewer_html = f"""
            <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
            <model-viewer 
                style="width: 100%; height: 620px; background-color: #111;"
                src="{glb_url}"
                alt="Modèle 3D DesAIgn"
                auto-rotate 
                camera-controls 
                shadow-intensity="1.5"
                exposure="0.7"
                environment-intensity="0.8"
                ar>
            </model-viewer>
            """
            components.v1.html(model_viewer_html, height=650)
            st.caption("🕹️ Souris = tourner • Molette = zoom • Double clic = recentrer")
        else:
            st.info("👆 Colle une URL de fichier .glb pour voir et tourner le modèle en 3D.")

# ====================== TAB 3 : WAR ROOM ======================
with tab3:
    st.info("📞 War Room — Espace de collaboration avancé (à développer plus tard)")

st.caption("DesAIgn Studio | École de Technologie Supérieure (ÉTS) — Version Avril 2026")
