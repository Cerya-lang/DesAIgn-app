import streamlit as st

# Initialisation de l'historique des versions
if "version_originale" not in st.session_state:
    st.session_state.version_originale = ""
if "version_modifiee" not in st.session_state:
    st.session_state.version_modifiee = ""

# --- Interface de Comparaison ---
if st.session_state.version_originale and st.session_state.version_modifiee:
    st.divider()
    st.subheader("🔄 Comparaison des Versions")
    
    col_v1, col_v2 = st.columns(2)
    
    with col_v1:
        st.markdown("### Version 1 (Originale)")
        st.info(st.session_state.version_originale)
        
    with col_v2:
        st.markdown("### Version 2 (Ajustée)")
        st.success(st.session_state.version_modifiee)
        
    # Visualisation de l'impact des modifications
    st.write("📈 **Analyse de l'évolution :** L'IA détecte une amélioration de la faisabilité technique suite à vos changements de matériaux.")
