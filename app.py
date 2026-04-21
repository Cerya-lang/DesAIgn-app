import streamlit as st
import google.generativeai as genai
import re
from huggingface_hub import InferenceClient
import requests
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
    if not GOOGLE_API_KEY:
        return None, "Clé Google API manquante dans les secrets."
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")
        return model, None
    except Exception as e:
        return None, f"Erreur Gemini : {str(e)}"

model, gemini_error = init_gemini()

# --- Client Hugging Face ---
hf_client = InferenceClient(token=HF_TOKEN) if HF_TOKEN else None

# ====================== INTERFACE ======================
st.title("🎨 DesAIgn | Studio de Recherche & Création")
st.caption("Analyse multilingue + Génération 3D gratuite avec Shap-E (FLUX prêt)")

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
    if hf_client:
        st.success("✅ HF connecté")
    else:
        st.warning("⚠️ HF_TOKEN manquant dans les secrets")

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

# ====================== TAB 2 : MOTEUR 3D (Shap-E + FLUX prêt) ======================
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
        st.write("**Prompt 3D généré par l'IA**")
        current_prompt = st.text_area(
            "Prompt actuel (tu peux le modifier)",
            value=st.session_state.current_3d_prompt,
            height=180
        )
        st.session_state.current_3d_prompt = current_prompt

        # Remix avec Gemini
        remix_instruction = st.text_input(
            "Modifier le design avec Gemini :",
            placeholder="Ajoute des bandes rouges racing, style cyberpunk, couleur bleu métallisé..."
        )
        if st.button("✨ Remix avec Gemini"):
            if model and current_prompt.strip():
                with st.spinner("Remix en cours..."):
                    remix_resp = model.generate_content(
                        f"Modifie ce prompt 3D selon : {remix_instruction}\n\nPrompt actuel :\n{current_prompt}\n"
                        "Retourne UNIQUEMENT le nouveau prompt complet et très détaillé en anglais."
                    )
                    st.session_state.current_3d_prompt = remix_resp.text.strip()
                    st.success("✅ Prompt mis à jour par Gemini !")
                    st.rerun()

        use_flux = st.checkbox("Utiliser FLUX pour générer une belle image de référence avant Shap-E", value=False)

        # Bouton de génération
        if st.button("🚀 Générer le modèle 3D avec Shap-E", type="primary"):
            if not hf_client:
                st.error("❌ HF_TOKEN manquant dans les secrets Streamlit.")
            elif not current_prompt.strip():
                st.error("Le prompt est vide.")
            else:
                with st.spinner("Génération en cours... (peut prendre 30 à 90 secondes)"):
                    try:
                        # FLUX (optionnel)
                        if use_flux:
                            with st.spinner("Génération image FLUX..."):
                                flux_image = hf_client.text_to_image(
                                    prompt=current_prompt + ", highly detailed, professional product photo, 8k",
                                    model="black-forest-labs/FLUX.1-schnell",
                                    num_inference_steps=20,
                                    guidance_scale=7.5
                                )
                                st.image(flux_image, caption="Image de référence - FLUX")
                                st.session_state.last_flux_image = flux_image

                        # Shap-E : Text-to-3D
                        result = hf_client.text_to_3d(
                            prompt=current_prompt,
                            model="openai/shap-e",
                            num_inference_steps=64,
                            guidance_scale=15.0
                        )
                        st.session_state.last_3d_result = result
                        st.success("✅ Modèle Shap-E généré !")
                    except Exception as e:
                        st.error(f"Erreur pendant la génération : {str(e)}")

    with col2:
        st.write("**Visualiseur du résultat**")
        if "last_3d_result" in st.session_state:
            result = st.session_state.last_3d_result
            if hasattr(result, 'url') and result.url:
                st.image(result.url, caption="Rendu 3D Shap-E (GIF rotation)", use_column_width=True)
                
                # Téléchargement du GIF
                try:
                    gif_data = requests.get(result.url).content
                    st.download_button(
                        "⬇️ Télécharger le GIF",
                        data=gif_data,
                        file_name="shap-e_generation.gif",
                        mime="image/gif"
                    )
                except:
                    pass
            else:
                st.write("Résultat prêt (debug) :")
                st.json(result)
        else:
            st.info("👈 Clique sur le bouton 'Générer' à gauche pour créer le modèle 3D.")

# ====================== TAB 3 : WAR ROOM ======================
with tab3:
    st.info("📞 War Room — Espace de collaboration avancé (à développer)")

st.caption("DesAIgn Studio | École de Technologie Supérieure (ÉTS) — Version Avril 2026")
