"""Evaluation Engine

This module contains a brief description of the EvaluationEngine:
execution of evaluation rules, on a manifest and generation of reports.
"""

from DSL4Pipelines.src.tools.queries.manifest_query import ManifestQuery
from DSL4Pipelines.src.tools.queries.metarules import RULE_REGISTRY, RuleReport
from DSL4Pipelines.src.metamodel.manifests.manifests import Manifest

"""
L'EvaluationEngine est responsable de l'exécution des règles d'évaluation sur un manifest donné.
Il prend en entrée un manifest et une liste de règles (ou utilise toutes les règles enregistrées) et génère un rapport d'évaluation.
Chaque règle est exécutée, et les résultats sont agrégés pour produire une note nuancée (Green/Orange/Red) basée sur le score moyen des résultats de la règle.
"""


class EvaluationEngine:
    def registered_rules(self) -> list:
        return [r.func for r in RULE_REGISTRY]

    def run_rules(self, manifest: Manifest, rules) -> list[RuleReport]:
        ctx = ManifestQuery(manifest)
        final_report = []

        for rule_func in rules:
            # On exécute la fonction de l'expert
            results = list(rule_func(ctx))

            # On calcule le score moyen
            if not results:
                continue

            avg_score = sum(r.score for r in results) / len(results)

            # On récupère le nom de la fonction proprement
            rule_name = getattr(rule_func, "name", rule_func.__name__)
            rulemetadata = next((r for r in RULE_REGISTRY if r.func == rule_func), None)

            status = (
                "Green" if avg_score > 0.7 else "Orange" if avg_score > 0.4 else "Red"
            )

            ruleReport = RuleReport(
                rule=rulemetadata,
                results=results,
                avg_score=avg_score,
                status=status,
            )

            final_report.append(ruleReport)

        return final_report

    def run_all(self, manifest) -> list[RuleReport]:
        print(f"--- Lancement de l'audit ({len(RULE_REGISTRY)} règles) ---")

        rules = [r.func for r in RULE_REGISTRY]
        return self.run_rules(manifest, rules)
