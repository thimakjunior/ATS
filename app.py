import streamlit as st

from ats_simulator.core import ATSSimulator
from ats_simulator.parsers import SUPPORTED_EXTENSIONS, UnsupportedFormatError, extract_text_from_bytes

st.set_page_config(page_title="ATS Simulator", page_icon="📄", layout="wide")

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.8rem; padding-bottom: 2rem;}
    .hero {background: linear-gradient(120deg, #0f172a, #1d4ed8); padding: 1rem 1.2rem; border-radius: 14px; color: white; margin-bottom: 1rem;}
    .card {background: #0b1220; border: 1px solid #1f2937; border-radius: 12px; padding: 0.8rem 1rem; margin-bottom: 0.8rem;}
    .subtle {opacity: 0.85; font-size: 0.92rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <h2 style="margin:0;">📄 ATS Simulator Pro</h2>
      <p style="margin:0.25rem 0 0 0;">Analyse CV ↔ offre avec scoring ATS, forces/failles, suggestions et réécriture ciblée.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander("Formats acceptés", expanded=False):
    st.write(
        "CV/offre: "
        + ", ".join(sorted(SUPPORTED_EXTENSIONS))
        + " (DOC/ODT: demande conversion vers DOCX/PDF)."
    )

col1, col2 = st.columns(2)
with col1:
    st.markdown("### Offre")
    offer_file = st.file_uploader(
        "Importer l'offre",
        type=["txt", "md", "rtf", "csv", "json", "pdf", "docx", "html", "htm", "xml", "doc", "odt"],
        key="offer_upload",
    )
    offer_text = st.text_area("Ou collez le texte de l'offre", height=240)

with col2:
    st.markdown("### CV")
    cv_file = st.file_uploader(
        "Importer le CV",
        type=["txt", "md", "rtf", "csv", "json", "pdf", "docx", "html", "htm", "xml", "doc", "odt"],
        key="cv_upload",
    )
    cv_text = st.text_area("Ou collez le texte du CV", height=240)

options = st.columns([1, 1, 2])
with options[0]:
    include_suggestions = st.toggle("Suggestions", value=True)
with options[1]:
    rewrite = st.toggle("Réécriture CV", value=False)
with options[2]:
    st.markdown('<p class="subtle">Astuce: privilégiez PDF/DOCX pour une extraction fiable.</p>', unsafe_allow_html=True)


def resolve_input(label: str, uploaded_file, pasted_text: str) -> str:
    if uploaded_file is not None:
        try:
            return extract_text_from_bytes(uploaded_file.name, uploaded_file.getvalue())
        except UnsupportedFormatError as exc:
            st.error(f"{label}: {exc}")
            return ""
    return pasted_text.strip()


if st.button("Analyser", type="primary", use_container_width=True):
    offer_payload = resolve_input("Offre", offer_file, offer_text)
    cv_payload = resolve_input("CV", cv_file, cv_text)

    if not offer_payload or not cv_payload:
        st.warning("Merci de fournir une offre et un CV (fichier ou texte collé).")
    else:
        report = ATSSimulator().evaluate_cv(
            job_offer=offer_payload,
            cv_text=cv_payload,
            include_suggestions=include_suggestions,
            rewrite_cv=rewrite,
        )

        m1, m2, m3 = st.columns(3)
        m1.metric("Score ATS", f"{report.global_score}/100")
        m2.metric("Mots-clés trouvés", str(len(report.matched_keywords)))
        m3.metric("Mots-clés manquants", str(len(report.missing_keywords)))

        st.markdown("### Forces")
        for finding in report.findings:
            for item in finding.strengths:
                st.success(f"[{finding.area}] {item}")

        st.markdown("### Failles")
        for finding in report.findings:
            for item in finding.gaps:
                st.error(f"[{finding.area}] {item}")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### Mots-clés trouvés")
            st.write(", ".join(report.matched_keywords) or "Aucun")
        with c2:
            st.markdown("### Mots-clés manquants")
            st.write(", ".join(report.missing_keywords) or "Aucun")

        if report.recommendations:
            st.markdown("### Suggestions")
            for rec in report.recommendations:
                st.info(rec)

        if report.rewritten_cv:
            st.markdown("### CV adapté")
            st.code(report.rewritten_cv)
