import streamlit as st
import google.generativeai as genai
import re
import requests
import time
import streamlit.components.v1 as components

# ====================== CONFIGURATION ======================
st.set_page_config(page_title="DesAIgn Studio | ÉTS", page_icon="🎨", layout="wide")

# === SECRETS ===
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY")
MESHY_API_KEY = st.secrets.get("MESHY_API_KEY")

def init_gemini():
    if not GOOGLE_API_KEY:
        return None, "Clé Google API manquante"
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        return genai.GenerativeModel("gemini-2.5-flash"), None
    except Exception as e:
        return None, str(e)

model, gemini_error = init_gemini()

# ====================== INTERFACE ======================
st.title("🎨 DesAIgn | Studio de Recherche & Création")
st.caption("Analyse multilingue + **VRAIE génération 3D** (Meshy.ai)")

with st.sidebar:
    st.title("🎨 DesAIgn Dashboard")
    with st.expander("👤 Mon Compte", expanded=True):
        st.write("**Nom :** Cerya")
        st.write("**Institution :** ÉTS")
        st.write("**Statut :** Développeur Principal")
    st.divider()
    if MESHY_API_KEY:
        st.success("✅ Meshy connecté → Qualité excellente")
    else:
        st.warning("⚠️ MESHY_API_KEY manquant dans les secrets")
    if model:
        st.success("✅ Gemini connecté")

tab1, tab2, tab3 = st.tabs(["💬 Analyse Multilingue", "🧊 Moteur 3D", "📞 War Room"])

# ====================== TAB 1 : ANALYSE (inchangé) ======================
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
                with st.spinner("Analyse en cours..."):
                    system_prompt = (
                        f"Tu es l'expert DesAIgn. RÉPONDS EXCLUSIVEMENT DANS LA LANGUE DU MESSAGE : '{prompt}'. "
                        f"Analyse en détail les matériaux, construction, ergonomie et design de : {prompt}. "
                        "Termine **obligatoirement** par : 'MASTER PROMPT 3D (EN):' suivi d'une description très détaillée en anglais."
                    )
                    response = model.generate_content(system_prompt)
                    text = response.text
                    st.markdown(text)
                    st.session_state.messages.append({"role": "assistant", "content": text})
            else:
                st.error(gemini_error)

# ====================== TAB 2 : MOTEUR 3D (GÉNÉRATION RÉELLE) ======================
with tab2:
    st.subheader("🧊 Générateur 3D Réel – Qualité Excellente (Meshy.ai)")

    # Extraction du dernier master prompt
    last_master_prompt = ""
    for msg in reversed(st.session_state.get("messages", [])):
        if msg["role"] == "assistant":
            match = re.search(r"MASTER PROMPT 3D \(EN\):\s*(.*)", msg["content"], re.DOTALL | re.IGNORECASE)
            if match:
                last_master_prompt = match.group(1).strip()
                break

    if "master_3d_prompt" not in st.session_state:
        st.session_state.master_3d_prompt = last_master_prompt

    col1, col2 = st.columns([1, 1])

    with col1:
        st.write("**Prompt 3D (modifiable)**")
        current_prompt = st.text_area(
            "Prompt actuel",
            value=st.session_state.master_3d_prompt,
            height=180,
            key="prompt_area"
        )
        st.session_state.master_3d_prompt = current_prompt

        # Remix
        remix_instruction = st.text_input("Modifier le design :", placeholder="Ajoute des bandes rouges racing, style cyberpunk...")
        if st.button("✨ Remix avec Gemini"):
            if model and current_prompt:
                with st.spinner("Gemini modifie le prompt..."):
                    remix = model.generate_content(
                        f"Voici le prompt 3D actuel :\n{current_prompt}\n\nModifie-le selon : {remix_instruction}\n"
                        "Retourne UNIQUEMENT le nouveau prompt complet en anglais."
                    )
                    st.session_state.master_3d_prompt = remix.text.strip()
                    st.success("✅ Prompt mis à jour !")
                    st.rerun()

        # === GÉNÉRATION RÉELLE 3D ===
        if st.button("🚀 Générer le modèle 3D avec Meshy (qualité excellente)", type="primary", disabled=not MESHY_API_KEY):
            if not current_prompt.strip():
                st.error("Le prompt est vide")
            else:
                with st.spinner("Création du modèle 3D en cours... (30 à 120 secondes)"):
                    try:
                        headers = {
                            "Authorization": f"Bearer {MESHY_API_KEY}",
                            "Content-Type": "application/json"
                        }
                        BASE_URL = "https://api.meshy.ai/openapi/v2"

                        # 1. Preview (mesh)
                        preview_resp = requests.post(
                            f"{BASE_URL}/text-to-3d",
                            headers=headers,
                            json={"mode": "preview", "prompt": current_prompt, "target_formats": ["glb"]}
                        )
                        preview_resp.raise_for_status()
                        preview_id = preview_resp.json()["result"]

                        # Poll preview
                        while True:
                            task = requests.get(f"{BASE_URL}/text-to-3d/{preview_id}", headers=headers).json()
                            if task["status"] == "SUCCEEDED":
                                break
                            time.sleep(4)

                        # 2. Refine (texture)
                        refine_resp = requests.post(
                            f"{BASE_URL}/text-to-3d",
                            headers=headers,
                            json={"mode": "refine", "preview_task_id": preview_id, "enable_pbr": True, "target_formats": ["glb"]}
                        )
                        refine_resp.raise_for_status()
                        refine_id = refine_resp.json()["result"]

                        # Poll refine
                        while True:
                            task = requests.get(f"{BASE_URL}/text-to-3d/{refine_id}", headers=headers).json()
                            if task["status"] == "SUCCEEDED":
                                glb_url = task["model_urls"]["glb"]
                                st.success("✅ Modèle 3D généré avec succès !")
                                break
                            time.sleep(4)

                        # Sauvegarde dans session_state
                        st.session_state.last_glb_url = glb_url

                    except Exception as e:
                        st.error(f"Erreur Meshy : {e}")

    # Affichage du visualiseur
    if "last_glb_url" in st.session_state:
        glb_url = st.session_state.last_glb_url
        st.write("**Ton modèle 3D interactif**")
        
        model_viewer_html = f"""
        <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
        <model-viewer 
            style="width: 100%; height: 650px; background-color: #111;"
            src="{glb_url}"
            alt="Modèle 3D généré"
            auto-rotate
            camera-controls
            shadow-intensity="1.5"
            exposure="0.8"
            ar>
        </model-viewer>
        """
        components.v1.html(model_viewer_html, height=680)

        st.download_button(
            "⬇️ Télécharger le fichier .glb",
            data=requests.get(glb_url).content,
            file_name="mon_modele_3d.glb",
            mime="model/gltf-binary"
        )

    else:
        st.info("👆 Clique sur le bouton rouge pour que l’IA crée ton modèle 3D.")

# ====================== TAB 3 ======================
with tab3:
    st.info("📞 War Room — à développer")

st.caption("DesAIgn Studio | École de Technologie Supérieure (ÉTS) — Version Avril 2026")
