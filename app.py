import streamlit as st
import google.generativeai as genai
import re
from huggingface_hub import InferenceClient
import requests
import streamlit.components.v1 as components

# ====================== CONFIG ======================
st.set_page_config(page_title="DesAIgn Studio | ÉTS", page_icon="🎨", layout="wide")

GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY")
HF_TOKEN = st.secrets.get("HF_TOKEN", "")

def init_gemini():
    if not GOOGLE_API_KEY:
        return None, "Clé Gemini manquante"
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        return genai.GenerativeModel("gemini-2.5-flash"), None
    except Exception as e:
        return None, str(e)

model, gemini_error = init_gemini()
hf_client = InferenceClient(token=HF_TOKEN) if HF_TOKEN else None

st.title("🎨 DesAIgn | Studio de Recherche & Création")
st.caption("Analyse + Génération 3D gratuite via Hugging Face")

with st.sidebar:
    st.title("🎨 DesAIgn Dashboard")
    with st.expander("👤 Mon Compte", expanded=True):
        st.write("**Nom :** Cerya")
        st.write("**Institution :** ÉTS")
        st.write("**Statut :** Développeur Principal")
    st.divider()
    st.success("✅ Mode Gratuit Hugging Face activé")
    if model:
        st.success("✅ Gemini connecté")

tab1, tab2, tab3 = st.tabs(["💬 Analyse Multilingue", "🧊 Moteur 3D", "📞 War Room"])

# ====================== TAB 1 (inchangé) ======================
with tab1:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    container = st.container(height=520)
    for msg in st.session_state.messages:
        with container.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Analyse n'importe quel vêtement ou véhicule..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with container.chat_message("user"):
            st.markdown(prompt)

        with container.chat_message("assistant"):
            if model:
                with st.spinner("Analyse en cours..."):
                    sp = f"Tu es l'expert DesAIgn. Réponds dans la langue du message. Analyse en détail : {prompt}. Termine obligatoirement par 'MASTER PROMPT 3D (EN):' suivi d'une description très détaillée en anglais."
                    try:
                        resp = model.generate_content(sp)
                        text = resp.text
                        st.markdown(text)
                        st.session_state.messages.append({"role": "assistant", "content": text})
                    except Exception as e:
                        st.error(e)
            else:
                st.error(gemini_error)

# ====================== TAB 2 : MOTEUR 3D (Version HF Gratuite) ======================
with tab2:
    st.subheader("🧊 Moteur 3D Gratuit (Hugging Face)")

    # Extraction MASTER PROMPT
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
        st.write("**Prompt 3D (créé par Gemini)**")
        current_prompt = st.text_area("Prompt actuel", value=st.session_state.current_3d_prompt, height=180)
        st.session_state.current_3d_prompt = current_prompt

        remix = st.text_input("Modifier avec Gemini :", placeholder="Ajoute des bandes rouges, style cyberpunk...")
        if st.button("✨ Remix avec Gemini"):
            if model and current_prompt:
                with st.spinner("Remix en cours..."):
                    new_p = model.generate_content(f"Modifie ce prompt 3D selon : {remix}\n\nPrompt actuel :\n{current_prompt}\nRetourne UNIQUEMENT le nouveau prompt détaillé en anglais.")
                    st.session_state.current_3d_prompt = new_p.text.strip()
                    st.success("Remix terminé !")
                    st.rerun()

        # Génération 3D
        if st.button("🚀 Générer le modèle 3D (HF - gratuit)", type="primary"):
            if not hf_client:
                st.error("HF_TOKEN manquant dans les secrets")
            elif not current_prompt.strip():
                st.error("Prompt vide")
            else:
                with st.spinner("Génération en cours... (peut prendre 30-90 secondes)"):
                    try:
                        # On utilise Shap-E pour commencer (plus stable)
                        result = hf_client.text_to_3d(
                            prompt=current_prompt,
                            model="openai/shap-e",
                            num_inference_steps=64
                        )
                        st.session_state.last_3d_result = result
                        st.success("Génération terminée !")
                    except Exception as e:
                        st.error(f"Erreur HF : {e}")

    with col2:
        st.write("**Visualiseur 3D**")
        if "last_3d_result" in st.session_state:
            result = st.session_state.last_3d_result
            if hasattr(result, 'url'):
                st.image(result.url, caption="Rendu 3D (GIF rotation)")
            else:
                st.write("Résultat prêt (vérifie dans le debug ci-dessous)")
                st.json(result)
        else:
            st.info("Clique sur le bouton ci-contre pour générer")

st.caption("DesAIgn Studio | ÉTS — Mode Gratuit Hugging Face (2026)")
