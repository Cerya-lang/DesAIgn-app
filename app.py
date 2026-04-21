import streamlit as st
import os
import json
import requests
import google.generativeai as genai

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="DesAIgn Studio | ÉTS",
    page_icon="🎨",
    layout="wide"
)

# --- RÉCUPÉRATION SÉCURISÉE DES SECRETS ---
HF_TOKEN = str(st.secrets.get('HF_TOKEN', ""))
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY")

# --- INITIALISATION GEMINI ---
def init_gemini():
    try:
        if not GOOGLE_API_KEY:
            return None, "Clé API Google manquante dans les Secrets Streamlit."
        
        genai.configure(api_key=GOOGLE_API_KEY)
        
        # Modèle recommandé en 2026 (rapide + performant)
        model_name = "gemini-2.5-flash"
        # Autres options possibles :
        # "gemini-2.5-flash-lite"  → plus rapide et économique
        # "gemini-2.5-pro"         → plus puissant mais plus lent/cher
        
        model = genai.GenerativeModel(model_name)
        
        # Test rapide pour vérifier que le modèle fonctionne
        test_response = model.generate_content("Bonjour, réponds par 'OK' uniquement.")
        if "OK" in test_response.text.strip():
            return model, None
        else:
            return None, "Le modèle Gemini a répondu mais de manière inattendue."
            
    except Exception as e:
        return None, f"Erreur d'initialisation Gemini : {str(e)}"


# Initialisation du modèle
model, error_msg = init_gemini()

# --- INTERFACE PRINCIPALE ---
st.title("🎨 DesAIgn | Studio de Recherche & Création")
st.caption("Assistant d'ingénierie design pour l'ÉTS - Analyse multilingue + Moteur 3D")

# Sidebar
with st.sidebar:
    st.title("🎨 DesAIgn Dashboard")
    
    with st.expander("👤 Mon Compte", expanded=True):
        st.write("**Nom :** Cerya")
        st.write("**Institution :** ÉTS")
        st.write("**Statut :** Développeur Principal")
    
    st.divider()
    st.caption("🌐 Langue : Détection automatique active")
    st.caption("🚀 Moteur 3D : Hugging Face Shap-E")
    
    # Option pour changer de modèle Gemini (utile pour tester)
    if model:
        st.success("✅ Gemini connecté")
        model_choice = st.selectbox(
            "Modèle Gemini",
            options=["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.5-pro"],
            index=0
        )
        # Note : pour changer dynamiquement il faudrait réinitialiser le model,
        # mais pour simplifier on garde le choix statique pour l'instant
    else:
        st.error("❌ Gemini non connecté")
        st.info("Vérifie ta clé GOOGLE_API_KEY dans les secrets Streamlit.")

# --- TABS ---
tabs = st.tabs(["💬 Analyse Multilingue", "🧊 Moteur 3D", "📞 War Room"])

# ====================== TAB 1 : ANALYSE MULTILINGUE ======================
with tabs[0]:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    container = st.container(height=550)

    # Affichage de l'historique
    for m in st.session_state.messages:
        with container.chat_message(m["role"]):
            st.markdown(m["content"])

    # Input utilisateur
    if prompt := st.chat_input("Analyse n'importe quel vêtement ou véhicule au monde..."):
        # Ajout du message utilisateur
        st.session_state.messages.append({"role": "user", "content": prompt})
        with container.chat_message("user"):
            st.markdown(prompt)

        # Réponse de l'assistant
        with container.chat_message("assistant"):
            if model:
                with st.spinner("Analyse approfondie en cours..."):
                    system_prompt = (
                        f"Tu es l'expert DesAIgn. RÉPONDS EXCLUSIVEMENT DANS LA LANGUE DU MESSAGE SUIVANT : '{prompt}'. "
                        f"Analyse les matériaux, la construction, l'ergonomie et le design de : {prompt}. "
                        "Termine obligatoirement par : 'MASTER PROMPT 3D (EN):' suivi d'une description technique détaillée en anglais "
                        "optimisée pour la génération 3D (Shap-E ou similaire)."
                    )
                    
                    try:
                        response = model.generate_content(system_prompt)
                        assistant_response = response.text
                        st.markdown(assistant_response)
                        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                    except Exception as e:
                        st.error(f"Erreur lors de la génération : {str(e)}")
            else:
                st.error(f"L'IA n'est pas connectée. {error_msg if error_msg else ''}")
                st.info("Vérifie que ta clé GOOGLE_API_KEY est correctement configurée dans les secrets Streamlit.")

# ====================== TAB 2 & 3 : À COMPLÉTER ======================
with tabs[1]:
    st.info("🧊 Moteur 3D - À implémenter (Shap-E via Hugging Face)")
    st.write("Ici tu pourras utiliser le MASTER PROMPT 3D généré dans l'onglet Analyse.")

with tabs[2]:
    st.info("📞 War Room - À implémenter")
    st.write("Espace de collaboration avancé.")

# Footer
st.caption("DesAIgn Studio | École de Technologie Supérieure (ÉTS) — Version 2026")
