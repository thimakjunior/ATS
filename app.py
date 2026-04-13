import streamlit as st

from ats_simulator.core import ATSSimulator

st.set_page_config(page_title="ATS Simulator", page_icon="📄", layout="wide")

st.title("📄 ATS Simulator (CV vs Offre)")
st.caption("Collez une offre et un CV pour obtenir un score ATS, les forces/failles, des suggestions et une version adaptée.")

col1, col2 = st.columns(2)
with col1:
    offer_text = st.text_area("Offre d'emploi", height=320, placeholder="Collez ici l'offre...")
with col2:
    cv_text = st.text_area("CV (texte)", height=320, placeholder="Collez ici le CV...")

include_suggestions = st.checkbox("Afficher des suggestions", value=True)
rewrite = st.checkbox("Générer une version adaptée du CV", value=False)

if st.button("Analyser", type="primary"):
    if not offer_text.strip() or not cv_text.strip():
        st.warning("Merci de renseigner à la fois l'offre et le CV.")
    else:
        simulator = ATSSimulator()
        report = simulator.evaluate_cv(
            job_offer=offer_text,
            cv_text=cv_text,
            include_suggestions=include_suggestions,
            rewrite_cv=rewrite,
        )

        st.subheader(f"Score ATS global: {report.global_score}/100")

        st.markdown("### Forces")
        for finding in report.findings:
            for item in finding.strengths:
                st.success(f"[{finding.area}] {item}")

        st.markdown("### Failles")
        for finding in report.findings:
            for item in finding.gaps:
                st.error(f"[{finding.area}] {item}")

        st.markdown("### Mots-clés")
        st.write("**Trouvés :**", ", ".join(report.matched_keywords) or "Aucun")
        st.write("**Manquants :**", ", ".join(report.missing_keywords) or "Aucun")

        if report.recommendations:
            st.markdown("### Suggestions")
            for rec in report.recommendations:
                st.info(rec)

        if report.rewritten_cv:
            st.markdown("### CV adapté")
            st.code(report.rewritten_cv)
