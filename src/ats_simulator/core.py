from __future__ import annotations

from dataclasses import dataclass, field
import json
import math
import re
from collections import Counter
from typing import Iterable

STOPWORDS = {
    "le", "la", "les", "de", "des", "du", "et", "a", "au", "aux", "un", "une",
    "pour", "par", "dans", "sur", "avec", "en", "ou", "the", "and", "of", "to", "for",
    "in", "on", "by", "as", "at", "is", "are", "be", "this", "that"
}

ACTION_VERBS = {
    "piloté", "conçu", "déployé", "optimisé", "augmenté", "réduit", "automatisé", "coordonné",
    "managed", "designed", "implemented", "delivered", "improved", "led", "built", "optimized",
    "created", "launched", "migrated"
}

SECTION_HINTS = {
    "experience": ["expérience", "experience", "work history", "professional experience"],
    "education": ["formation", "education", "diplôme", "degree"],
    "skills": ["compétences", "skills", "technologies", "stack"],
    "contact": ["email", "téléphone", "phone", "linkedin"],
}


@dataclass
class JobProfile:
    title: str
    raw_text: str
    must_have: list[str] = field(default_factory=list)
    nice_to_have: list[str] = field(default_factory=list)
    years_required: int | None = None
    language_requirements: list[str] = field(default_factory=list)


@dataclass
class ATSFinding:
    area: str
    score: int
    max_score: int
    strengths: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)


@dataclass
class ATSReport:
    global_score: int
    findings: list[ATSFinding]
    matched_keywords: list[str]
    missing_keywords: list[str]
    recommendations: list[str]
    rewritten_cv: str | None = None

    def to_json(self) -> str:
        return json.dumps(
            {
                "global_score": self.global_score,
                "matched_keywords": self.matched_keywords,
                "missing_keywords": self.missing_keywords,
                "recommendations": self.recommendations,
                "rewritten_cv": self.rewritten_cv,
                "findings": [
                    {
                        "area": f.area,
                        "score": f.score,
                        "max_score": f.max_score,
                        "strengths": f.strengths,
                        "gaps": f.gaps,
                    }
                    for f in self.findings
                ],
            },
            ensure_ascii=False,
            indent=2,
        )


class ATSSimulator:
    """Simulateur ATS inspiré des pratiques courantes de screening recruteur."""

    def parse_job_offer(self, offer_text: str) -> JobProfile:
        title = self._extract_title(offer_text)
        kws = self._extract_keywords(offer_text)
        must_have = kws[:15]
        nice_to_have = kws[15:30]
        years = self._extract_years(offer_text)
        languages = [lang for lang in ["français", "english", "anglais"] if lang in offer_text.lower()]
        return JobProfile(
            title=title,
            raw_text=offer_text,
            must_have=must_have,
            nice_to_have=nice_to_have,
            years_required=years,
            language_requirements=languages,
        )

    def evaluate_cv(
        self,
        job_offer: str,
        cv_text: str,
        include_suggestions: bool = True,
        rewrite_cv: bool = False,
    ) -> ATSReport:
        profile = self.parse_job_offer(job_offer)
        findings: list[ATSFinding] = []

        parsing = self._assess_parsing_quality(cv_text)
        keyword = self._assess_keyword_alignment(profile, cv_text)
        content = self._assess_content_quality(profile, cv_text)
        impact = self._assess_impact_signals(cv_text)

        findings.extend([parsing, keyword, content, impact])

        total = sum(f.score for f in findings)
        max_total = sum(f.max_score for f in findings) or 1
        global_score = round(total / max_total * 100)

        matched, missing = self._keyword_presence(profile.must_have, cv_text)
        recs = self._build_recommendations(findings, missing) if include_suggestions else []

        rewritten = self._rewrite_cv(profile, cv_text, missing) if rewrite_cv else None
        return ATSReport(
            global_score=global_score,
            findings=findings,
            matched_keywords=matched,
            missing_keywords=missing,
            recommendations=recs,
            rewritten_cv=rewritten,
        )

    def _assess_parsing_quality(self, cv_text: str) -> ATSFinding:
        score, max_score = 0, 25
        strengths, gaps = [], []
        lower = cv_text.lower()

        section_hits = 0
        for _, hints in SECTION_HINTS.items():
            if any(h in lower for h in hints):
                section_hits += 1
        score += min(section_hits * 4, 16)
        if section_hits >= 3:
            strengths.append("Sections ATS-friendly détectées (expérience, compétences, formation, contact).")
        else:
            gaps.append("Structure incomplète: ajoutez des sections standard lisibles ATS.")

        has_email = bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", cv_text))
        has_phone = bool(re.search(r"\+?\d[\d\s().-]{7,}", cv_text))
        if has_email and has_phone:
            score += 5
            strengths.append("Coordonnées détectées correctement.")
        else:
            gaps.append("Coordonnées incomplètes ou format non standard (email/téléphone).")

        if len(cv_text.splitlines()) >= 12:
            score += 4
            strengths.append("Longueur de CV raisonnable pour un parsing ATS stable.")
        else:
            gaps.append("CV trop court: risque de manque d'informations clés pour l'ATS.")

        return ATSFinding("Parsing & structure", min(score, max_score), max_score, strengths, gaps)

    def _assess_keyword_alignment(self, profile: JobProfile, cv_text: str) -> ATSFinding:
        score, max_score = 0, 35
        strengths, gaps = [], []
        matched, missing = self._keyword_presence(profile.must_have, cv_text)

        ratio = len(matched) / max(len(profile.must_have), 1)
        score += round(25 * ratio)
        if ratio >= 0.6:
            strengths.append(f"Bonne couverture des mots-clés critiques ({len(matched)}/{len(profile.must_have)}).")
        else:
            gaps.append(f"Couverture faible des mots-clés critiques ({len(matched)}/{len(profile.must_have)}).")

        nice_matched, _ = self._keyword_presence(profile.nice_to_have, cv_text)
        score += min(len(nice_matched), 10)
        if nice_matched:
            strengths.append("Présence de compétences différenciantes de l'offre.")

        if missing:
            gaps.append("Mots-clés absents: " + ", ".join(missing[:8]))

        return ATSFinding("Matching offre/CV", min(score, max_score), max_score, strengths, gaps)

    def _assess_content_quality(self, profile: JobProfile, cv_text: str) -> ATSFinding:
        score, max_score = 0, 20
        strengths, gaps = [], []
        lower = cv_text.lower()

        if profile.years_required is not None:
            years_in_cv = [int(x) for x in re.findall(r"(\d+)\+?\s*ans", lower)]
            cv_years = max(years_in_cv) if years_in_cv else 0
            if cv_years >= profile.years_required:
                score += 8
                strengths.append(f"Niveau d'expérience compatible ({cv_years} ans vs requis {profile.years_required}).")
            else:
                gaps.append(f"Expérience affichée ({cv_years} ans) < attendu ({profile.years_required} ans).")

        lang_hits = [lang for lang in profile.language_requirements if lang in lower]
        if lang_hits:
            score += 6
            strengths.append("Langues demandées retrouvées dans le CV.")
        elif profile.language_requirements:
            gaps.append("Langues de l'offre non explicitées dans le CV.")

        if "linkedin" in lower or "github" in lower or "portfolio" in lower:
            score += 6
            strengths.append("Preuves externes (LinkedIn/GitHub/Portfolio) présentes.")
        else:
            gaps.append("Ajoutez un lien LinkedIn/GitHub/portfolio pour crédibiliser le profil.")

        return ATSFinding("Qualité du contenu", min(score, max_score), max_score, strengths, gaps)

    def _assess_impact_signals(self, cv_text: str) -> ATSFinding:
        score, max_score = 0, 20
        strengths, gaps = [], []
        tokens = self._tokenize(cv_text)
        token_set = set(tokens)

        verb_hits = len(token_set.intersection(ACTION_VERBS))
        score += min(verb_hits * 2, 10)
        if verb_hits >= 3:
            strengths.append("Utilisation de verbes d'action valorisés en ATS/recrutement.")
        else:
            gaps.append("Renforcez le CV avec des verbes d'action (piloté, déployé, optimized...).")

        number_hits = len(re.findall(r"\b\d+(?:[.,]\d+)?\s*(%|kpi|€|\$|users|clients|jours|heures)?", cv_text.lower()))
        score += min(number_hits, 10)
        if number_hits >= 4:
            strengths.append("Réalisations quantifiées détectées (KPIs/chiffres).")
        else:
            gaps.append("Ajoutez des résultats mesurables (%, économies, volume, délais).")

        return ATSFinding("Impact & réalisations", min(score, max_score), max_score, strengths, gaps)

    def _build_recommendations(self, findings: list[ATSFinding], missing_keywords: list[str]) -> list[str]:
        recs = []
        for finding in findings:
            if finding.score < math.ceil(0.6 * finding.max_score):
                recs.extend(finding.gaps[:2])
        if missing_keywords:
            recs.append(
                "Intégrez naturellement ces termes issus de l'offre dans vos expériences: "
                + ", ".join(missing_keywords[:12])
            )
        if not recs:
            recs.append("CV déjà solide pour l'offre ciblée. Faites un ajustement mineur du titre et du résumé.")
        return recs

    def _rewrite_cv(self, profile: JobProfile, cv_text: str, missing_keywords: list[str]) -> str:
        lines = [line.rstrip() for line in cv_text.splitlines() if line.strip()]
        if not lines:
            return cv_text

        header = lines[0]
        summary = (
            f"Résumé ciblé — {profile.title}: profil orienté résultats avec focus sur "
            + ", ".join((profile.must_have[:5] or ["priorités du poste"]))
            + "."
        )

        injected_keywords = ", ".join(missing_keywords[:6]) if missing_keywords else "alignement déjà satisfaisant"
        adaptation_block = [
            "",
            "Expériences adaptées à l'offre:",
            f"- Piloté des initiatives alignées avec les exigences du poste ({injected_keywords}).",
            "- Optimisé les processus avec des résultats mesurables (qualité, délais, coût).",
            "- Collaboré avec les parties prenantes et assuré un delivery fiable.",
        ]

        rewritten = [header, summary] + lines[1:] + adaptation_block
        return "\n".join(rewritten)

    def _extract_title(self, text: str) -> str:
        first_line = next((line.strip() for line in text.splitlines() if line.strip()), "Poste")
        return first_line[:120]

    def _extract_years(self, text: str) -> int | None:
        matches = [int(m) for m in re.findall(r"(\d+)\+?\s*(?:ans|years)", text.lower())]
        return max(matches) if matches else None

    def _extract_keywords(self, text: str) -> list[str]:
        tokens = [t for t in self._tokenize(text) if len(t) > 2 and t not in STOPWORDS]
        counts = Counter(tokens)
        ordered = [word for word, _ in counts.most_common(40)]
        return ordered

    def _keyword_presence(self, keywords: Iterable[str], cv_text: str) -> tuple[list[str], list[str]]:
        lower = cv_text.lower()
        matched, missing = [], []
        for kw in keywords:
            if kw and kw.lower() in lower:
                matched.append(kw)
            else:
                missing.append(kw)
        return matched, missing

    def _tokenize(self, text: str) -> list[str]:
        return re.findall(r"[a-zA-Zàâçéèêëîïôûùüÿñæœ0-9+#.-]+", text.lower())
