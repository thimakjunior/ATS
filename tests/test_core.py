from ats_simulator.core import ATSSimulator


def test_evaluate_cv_returns_report_with_sections():
    offer = """
    Data Analyst Senior
    Nous cherchons un profil SQL, Python, Power BI avec 5 ans d'expérience.
    Anglais requis. Missions: automatisation KPI, dashboarding, collaboration métier.
    """
    cv = """
    Jane Doe
    Email: jane@doe.com
    Téléphone: +33 6 00 00 00 00
    LinkedIn: linkedin.com/in/janedoe

    Expérience
    - Piloté un projet Python SQL pour automatiser des dashboards KPI.
    - Optimized reporting process and reduced delays by 30%.

    Compétences
    Python, SQL, Tableau

    Formation
    Master Data
    6 ans d'expérience
    Anglais courant
    """

    report = ATSSimulator().evaluate_cv(offer, cv, include_suggestions=True, rewrite_cv=True)

    assert 0 <= report.global_score <= 100
    assert len(report.findings) == 4
    assert report.recommendations
    assert report.rewritten_cv is not None


def test_job_offer_drives_keyword_selection():
    offer_a = "Backend Engineer - Go, Kubernetes, AWS, microservices"
    offer_b = "Marketing Manager - SEO, content strategy, CRM"
    cv = "Go AWS microservices"

    sim = ATSSimulator()
    report_a = sim.evaluate_cv(offer_a, cv)
    report_b = sim.evaluate_cv(offer_b, cv)

    assert report_a.global_score > report_b.global_score
