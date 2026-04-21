import streamlit as st
import re
from datetime import datetime
import uuid

st.set_page_config(
    page_title="DesAIgn Studio | ÉTS",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== SESSION STATE ======================
if "user" not in st.session_state:
    st.session_state.user = None

if "subscription" not in st.session_state:
    st.session_state.subscription = "Free"

if "current_ai" not in st.session_state:
    st.session_state.current_ai = "Gemini 2.5 Flash"

if "history" not in st.session_state:
    st.session_state.history = []

if "saved_models" not in st.session_state:
    st.session_state.saved_models = []

if "messages" not in st.session_state:
    st.session_state.messages = []

if "rooms" not in st.session_state:
    st.session_state.rooms = {}

# ====================== SIDEBAR (Style propre comme ChatGPT/Grok) ======================
with st.sidebar:
    st.title("🎨 DesAIgn Studio")

    # Connexion (exactement comme Gemini/ChatGPT)
    if st.session_state.user is None:
        st.markdown("### 👤 Connexion")
        if st.button("🔑 Se connecter avec Google", use_container_width=True, type="secondary"):
            st.session_state.user = {
                "name": "Cerya",
                "email": "cerya@etsmtl.ca",
                "avatar": "🎨"
            }
            st.success("✅ Connecté avec Google")
            st.rerun()
        
        st.divider()
        email = st.text_input("Email", placeholder="ton@email.com")
        if st.button("Se connecter avec email", use_container_width=True):
            if email:
                st.session_state.user = {"name": email.split("@")[0].title(), "email": email, "avatar": "👤"}
                st.success("✅ Connecté")
                st.rerun()
    else:
        st.success(f"✅ {st.session_state.user['avatar']} {st.session_state.user['name']}")
        st.caption(st.session_state.user["email"])
        if st.button("🚪 Déconnexion", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    st.divider()

    # Choix du modèle IA
    st.caption("🤖 Modèle IA")
    st.session_state.current_ai = st.selectbox(
        "Modèle actif",
        ["Gemini 2.5 Flash", "Grok 4", "ChatGPT-4o", "Claude 3.5 Sonnet"],
        index=0
    )

    st.divider()

    # Navigation
    page = st.radio(
        "Navigation",
        ["🏠 Accueil", "💬 Analyse", "🧊 3D Model", "📞 Call", "📚 Bibliothèque"],
        label_visibility="collapsed"
    )

# ====================== ACCUEIL ======================
if page == "🏠 Accueil":
    st.title("🎨 DesAIgn Studio")
    st.subheader("Assistant d'ingénierie design pour l'ÉTS")

    if st.session_state.user:
        st.success(f"Bienvenue, {st.session_state.user['name']} !")
    else:
        st.warning("🔒 Connecte-toi pour débloquer toutes les fonctionnalités")

    # Abonnements
    st.markdown("### 💎 Abonnements")
    cols = st.columns(3)
    with cols[0]:
        st.metric("Free", "0 $")
        st.button("Utiliser gratuitement", use_container_width=True)
    with cols[1]:
        st.metric("Pro", "19 $/mois", "Recommandé")
        if st.button("Passer à Pro", type="primary", use_container_width=True):
            st.session_state.subscription = "Pro"
            st.toast("✅ Abonnement Pro activé")
    with cols[2]:
        st.metric("Team / ÉTS", "49 $/mois")
        st.button("Choisir Team", use_container_width=True)

# ====================== ANALYSE (avec conseils intelligents) ======================
elif page == "💬 Analyse":
    st.subheader("💬 Analyse & Conseils")

    container = st.container(height=520)
    for m in st.session_state.messages:
        with container.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("Analyse n'importe quel vêtement ou véhicule..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.history.append({"type": "Analyse", "title": prompt[:40], "date": datetime.now().strftime("%H:%M")})
        
        with container.chat_message("user"):
            st.markdown(prompt)

        with container.chat_message("assistant"):
            # Réponse d'analyse + question sur les matériaux
            st.markdown(f"""
**Analyse de :** {prompt}

J'ai analysé le design, les matériaux et la construction.  
**Voulez-vous utiliser les mêmes matériaux que dans l'analyse originale ?**  
Répondez simplement par **oui** ou **non**.
""")
            st.session_state.messages.append({
                "role": "assistant", 
                "content": f"Analyse de : {prompt}\n\nVoulez-vous utiliser les mêmes matériaux ? (oui/non)"
            })

    # Gestion intelligente des réponses "oui"
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        last_user_msg = st.session_state.messages[-1]["content"].lower()
        if "oui" in last_user_msg or "yes" in last_user_msg:
            with container.chat_message("assistant"):
                st.markdown("""
**Conseils pratiques :**

**Coût approximatif :**  
• Vêtement : 45 – 120 $ selon la quantité  
• Voiture (pièces custom) : 800 – 4500 $ selon la complexité

**Meilleurs fournisseurs (qualité/prix/rapidité) :**
- **Pour vêtements** : Printful / Printify (très bon rapport qualité/prix)
- **Pour pièces auto** : Local Motors / Xometry / Protolabs (qualité pro)
- **Fabrication rapide Québec** : 48h – 5 jours selon le fournisseur

**Recommandation :**  
Je peux te proposer 3 options précises (budget bas / moyen / premium) si tu me donnes ton budget maximum.

**Veux-tu que je te prépare un devis détaillé ?**
""")
                st.session_state.messages.append({"role": "assistant", "content": "Conseils fournis + proposition de devis"})

# ====================== 3D MODEL ======================
elif page == "🧊 3D Model":
    st.subheader("🧊 3D Model")
    st.info("Génération 3D via Shap-E (gratuit) – En cours de test")
    current_prompt = st.text_area("Prompt pour le modèle 3D", height=160, placeholder="Décris ton véhicule ou vêtement en détail...")
    
    if st.button("🚀 Générer le modèle 3D", type="primary"):
        st.success("✅ Modèle en cours de génération (simulation)")
        st.session_state.history.append({"type": "3D Model", "title": "Nouveau modèle", "date": datetime.now().strftime("%H:%M")})

# ====================== CALL (ex-War Room) ======================
elif page == "📞 Call":
    st.subheader("📞 Call – Collaboration en direct")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Créer un nouvel appel", type="primary", use_container_width=True):
            code = str(uuid.uuid4())[:8].upper()
            st.session_state.rooms[code] = {"name": f"Call {code}", "messages": []}
            st.success(f"Appel créé ! Code : **{code}**")
    with col2:
        code = st.text_input("Rejoindre un appel (code)")
        if st.button("Rejoindre", use_container_width=True) and code:
            st.session_state.current_room = code.upper()
            st.success(f"Connecté à l'appel {code.upper()}")

# ====================== BIBLIOTHÈQUE ======================
elif page == "📚 Bibliothèque":
    st.subheader("📚 Bibliothèque de modèles")
    if st.session_state.saved_models:
        for m in st.session_state.saved_models:
            with st.expander(m["name"]):
                st.write(m["prompt"])
    else:
        st.info("Aucun modèle sauvegardé pour l’instant.")

st.caption("DesAIgn Studio | École de Technologie Supérieure (ÉTS) — Version mise à jour Avril 2026")
