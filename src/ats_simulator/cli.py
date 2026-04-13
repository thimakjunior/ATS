from __future__ import annotations

import argparse
from pathlib import Path

from .core import ATSSimulator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Simulateur ATS pour comparer un CV à une offre.")
    parser.add_argument("--offer", required=True, help="Chemin vers le fichier texte de l'offre")
    parser.add_argument("--cv", required=True, help="Chemin vers le fichier texte du CV")
    parser.add_argument("--no-suggestions", action="store_true", help="Désactive les suggestions")
    parser.add_argument("--rewrite", action="store_true", help="Génère une version adaptée du CV")
    parser.add_argument("--json", action="store_true", help="Sortie JSON")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    offer = Path(args.offer).read_text(encoding="utf-8")
    cv = Path(args.cv).read_text(encoding="utf-8")

    simulator = ATSSimulator()
    report = simulator.evaluate_cv(
        job_offer=offer,
        cv_text=cv,
        include_suggestions=not args.no_suggestions,
        rewrite_cv=args.rewrite,
    )

    if args.json:
        print(report.to_json())
        return

    print(f"Score ATS global: {report.global_score}/100")
    print("\nForces:")
    for finding in report.findings:
        for point in finding.strengths:
            print(f"  + [{finding.area}] {point}")

    print("\nFailles:")
    for finding in report.findings:
        for point in finding.gaps:
            print(f"  - [{finding.area}] {point}")

    if report.recommendations:
        print("\nSuggestions:")
        for rec in report.recommendations:
            print(f"  * {rec}")

    if report.rewritten_cv:
        print("\n=== CV ADAPTÉ ===")
        print(report.rewritten_cv)


if __name__ == "__main__":
    main()
