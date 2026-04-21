import streamlit as st
import google.generativeai as genai
import re
import requests
import streamlit.components.v1 as components

# Optionnel : essayer d'importer HF seulement si nécessaire
try:
    from huggingface_hub import InferenceClient
    hf_available = True
except ImportError:
    hf_available = False
    InferenceClient = None

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
    if not GOOGLE_API_KEY:
        return None, "Clé Google API manquante dans les secrets."
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")
        return model, None
    except Exception as e:
        return None, f"Erreur Gemini : {str(e)}"

model, gemini_error = init_gemini()

# ====================== INTERFACE ======================
st.title("🎨 DesAIgn | Studio de Recherche & Création")
st.caption("Analyse multilingue + Génération 3D gratuite avec Shap-E")

with st.sidebar:
    st.title("🎨 DesAIgn Dashboard")
    with st.expander("👤 Mon Compte", expanded=True):
        st.write("**Nom :** Cerya")
        st.write("**Institution :** ÉTS")
        st.write("**Statut :** Développeur Principal")
    
    st.divider()
    st.success("✅ Mode Gratuit - Hugging Face")
    if model:
        st.success("✅ Gemini connecté")
    if hf_available:
        st.success("✅ huggingface_hub installé")
    else:
        st.error("❌ huggingface_hub non installé → Vérifie requirements.txt")

# ====================== TABS ======================
tab1, tab2, tab3 = st.tabs(["💬 Analyse Multilingue", "🧊 Moteur 3D", "📞 War Room"])

# ====================== TAB 1 : ANALYSE ======================
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
                        f"Analyse en détail les matériaux, construction, ergonomie et design de : {prompt}. "
                        "Termine **obligatoirement** par : 'MASTER PROMPT 3D (EN):' suivi d'une description très détaillée en anglais."
                    )
                    try:
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
    st.subheader("🧊 Moteur 3D Gratuit – Shap-E")

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

    col1, col2 = st.columns([1, 1])

    with col1:
        current_prompt = st.text_area(
            "Prompt 3D actuel (modifiable)",
            value=st.session_state.current_3d_prompt,
            height=180
        )
        st.session_state.current_3d_prompt = current_prompt

        remix_instruction = st.text_input("Modifier avec Gemini :", placeholder="Ajoute des bandes rouges racing...")
        if st.button("✨ Remix avec Gemini"):
            if model and current_prompt.strip():
                with st.spinner("Remix en cours..."):
                    remix_resp = model.generate_content(
                        f"Modifie ce prompt selon : {remix_instruction}\n\nPrompt actuel :\n{current_prompt}\nRetourne UNIQUEMENT le nouveau prompt détaillé en anglais."
                    )
                    st.session_state.current_3d_prompt = remix_resp.text.strip()
                    st.success("✅ Prompt mis à jour !")
                    st.rerun()

        if st.button("🚀 Générer avec Shap-E", type="primary"):
            if not hf_available:
                st.error("❌ huggingface_hub n'est pas installé. Ajoute-le dans requirements.txt")
            elif not HF_TOKEN:
                st.error("❌ HF_TOKEN manquant dans les secrets.")
            elif not current_prompt.strip():
                st.error("Prompt vide.")
            else:
                client = InferenceClient(token=HF_TOKEN)
                with st.spinner("Génération Shap-E en cours (30-90s)..."):
                    try:
                        result = client.text_to_3d(
                            prompt=current_prompt,
                            model="openai/shap-e",
                            num_inference_steps=64
                        )
                        st.session_state.last_3d_result = result
                        st.success("✅ Génération terminée !")
                    except Exception as e:
                        st.error(f"Erreur Shap-E : {e}")

    with col2:
        st.write("**Résultat 3D**")
        if "last_3d_result" in st.session_state:
            result = st.session_state.last_3d_result
            if hasattr(result, 'url') and result.url:
                st.image(result.url, caption="Rendu Shap-E (GIF)", use_column_width=True)
            else:
                st.json(result)
        else:
            st.info("Génère un modèle à gauche →")

# ====================== TAB 3 ======================
with tab3:
    st.info("📞 War Room — À développer")

st.caption("DesAIgn Studio | ÉTS — Version Avril 2026")
