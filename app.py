import streamlit as st
import google.generativeai as genai
import re
from huggingface_hub import InferenceClient
import requests
import streamlit.components.v1 as components
from datetime import datetime

# ====================== CONFIGURATION ======================
st.set_page_config(
    page_title="DesAIgn Studio | ÉTS",
    page_icon="🎨",
    layout="wide"
)

# Secrets
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY")
HF_TOKEN = st.secrets.get("HF_TOKEN", "")

# Initialisation Gemini
def init_gemini():
    if not GOOGLE_API_KEY:
        return None, "Clé Google API manquante"
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        return genai.GenerativeModel("gemini-2.5-flash"), None
    except Exception as e:
        return None, str(e)

model, gemini_error = init_gemini()
hf_client = InferenceClient(token=HF_TOKEN) if HF_TOKEN else None

# Initialisation de la bibliothèque de modèles
if "saved_models" not in st.session_state:
    st.session_state.saved_models = []

# ====================== INTERFACE ======================
st.title("🎨 DesAIgn | Studio de Recherche & Création")
st.caption("Analyse → Génération 3D → Modification externe → Sauvegarde")

with st.sidebar:
    st.title("🎨 DesAIgn Dashboard")
    with st.expander("👤 Mon Compte", expanded=True):
        st.write("**Nom :** Cerya")
        st.write("**Institution :** ÉTS")
        st.write("**Statut :** Développeur Principal")
    st.divider()
    if model:
        st.success("✅ Gemini connecté")
    if hf_client:
        st.success("✅ Hugging Face connecté")
    st.caption("Mode : Gratuit + Édition externe")

tab1, tab2, tab3 = st.tabs(["💬 Analyse Multilingue", "🧊 Moteur 3D", "📚 Bibliothèque"])

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
                with st.spinner("Analyse en cours..."):
                    try:
                        system_prompt = (
                            f"Tu es l'expert DesAIgn. RÉPONDS EXCLUSIVEMENT DANS LA LANGUE DU MESSAGE : '{prompt}'. "
                            f"Analyse en détail les matériaux, construction, ergonomie et design de : {prompt}. "
                            "Termine **obligatoirement** par : 'MASTER PROMPT 3D (EN):' suivi d'une description très détaillée en anglais."
                        )
                        response = model.generate_content(system_prompt)
                        text = response.text
                        st.markdown(text)
                        st.session_state.messages.append({"role": "assistant", "content": text})
                    except Exception as e:
                        st.error(f"Erreur Gemini : {e}")
            else:
                st.error(gemini_error)

# ====================== TAB 2 : MOTEUR 3D ======================
with tab2:
    st.subheader("🧊 Génération 3D + Modification Externe")

    # Extraction du dernier MASTER PROMPT
    last_prompt = ""
    for msg in reversed(st.session_state.get("messages", [])):
        if msg["role"] == "assistant":
            match = re.search(r"MASTER PROMPT 3D \(EN\):\s*(.*)", msg["content"], re.DOTALL | re.IGNORECASE)
            if match:
                last_prompt = match.group(1).strip()
                break

    if "current_3d_prompt" not in st.session_state:
        st.session_state.current_3d_prompt = last_prompt

    current_prompt = st.text_area(
        "Prompt 3D (modifiable)",
        value=st.session_state.current_3d_prompt,
        height=160
    )
    st.session_state.current_3d_prompt = current_prompt

    col_gen, col_view = st.columns([1, 1])

    with col_gen:
        if st.button("🚀 Générer le modèle 3D avec Shap-E", type="primary"):
            if not hf_client:
                st.error("❌ HF_TOKEN manquant dans les secrets.")
            elif not current_prompt.strip():
                st.error("Le prompt est vide.")
            else:
                with st.spinner("Génération Shap-E en cours (30-90 secondes)..."):
                    try:
                        result = hf_client.text_to_3d(
                            prompt=current_prompt,
                            model="openai/shap-e",
                            num_inference_steps=64
                        )
                        st.session_state.last_3d_result = result
                        st.success("✅ Modèle généré avec Shap-E !")
                    except Exception as e:
                        st.error(f"Erreur Shap-E : {str(e)}")

        st.markdown("---")
        st.write("**Modifier le modèle professionnellement**")
        
        if "last_3d_result" in st.session_state and hasattr(st.session_state.last_3d_result, 'url'):
            if st.button("✏️ Ouvrir dans un éditeur 3D externe (Spline)"):
                st.info("Pour l'instant, copie le prompt ci-dessous et va sur : **https://spline.design** ou **https://www.tripo3d.ai/studio**")
                st.text_area("Prompt à utiliser dans l'éditeur externe :", current_prompt, height=100)
        else:
            st.info("Génère d'abord un modèle pour pouvoir l'éditer.")

    with col_view:
        st.write("**Visualiseur 3D**")
        if "last_3d_result" in st.session_state:
            result = st.session_state.last_3d_result
            if hasattr(result, 'url') and result.url:
                st.image(result.url, caption="Rendu Shap-E (GIF rotation)", use_column_width=True)
            else:
                st.json(result)
        else:
            st.info("Le modèle apparaîtra ici après génération.")

    # ====================== SAUVEGARDE DU MODÈLE MODIFIÉ ======================
    st.markdown("---")
    st.subheader("💾 Sauvegarder le modèle modifié")
    
    col_save1, col_save2 = st.columns(2)
    with col_save1:
        saved_name = st.text_input("Nom du modèle :", placeholder="Nissan Skyline R34 - Version Racing")
    with col_save2:
        glb_url = st.text_input("URL du fichier .glb modifié :", placeholder="https://.../model.glb")

    if st.button("Sauvegarder dans la Bibliothèque"):
        if saved_name and glb_url:
            new_model = {
                "name": saved_name,
                "prompt": current_prompt,
                "glb_url": glb_url,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "original_prompt": current_prompt
            }
            st.session_state.saved_models.append(new_model)
            st.success(f"✅ Modèle '{saved_name}' sauvegardé dans la bibliothèque !")
        else:
            st.warning("Veuillez entrer un nom et une URL .glb")

# ====================== TAB 3 : BIBLIOTHÈQUE ======================
with tab3:
    st.subheader("📚 Bibliothèque de Modèles Sauvegardés")
    
    if st.session_state.saved_models:
        for i, model_data in enumerate(st.session_state.saved_models):
            with st.expander(f"🎯 {model_data['name']} — {model_data['date']}"):
                st.write(f"**Prompt original :** {model_data['prompt'][:150]}...")
                if model_data.get("glb_url"):
                    st.write(f"**URL du modèle :** {model_data['glb_url']}")
                    
                    # Visualiseur simple
                    model_viewer_html = f"""
                    <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
                    <model-viewer 
                        style="width: 100%; height: 400px; background-color: #111;"
                        src="{model_data['glb_url']}"
                        alt="Modèle sauvegardé"
                        auto-rotate camera-controls shadow-intensity="1">
                    </model-viewer>
                    """
                    components.v1.html(model_viewer_html, height=420)
    else:
        st.info("Aucun modèle sauvegardé pour l'instant. Génère et modifie des modèles puis sauvegarde-les ici.")

st.caption("DesAIgn Studio | École de Technologie Supérieure (ÉTS) — Workflow Génération → Édition externe → Sauvegarde")
