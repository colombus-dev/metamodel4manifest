"""
This module defines some evaluation rules
for assessing the quality of a manifest in terms of
- its readiness for French language processing.

Each rule is implemented as a function that takes
- a ManifestQuery context and
- yields one or more EvaluationResult objects,
    which contain the results of the evaluation,
    including a label, a success status, a score, and evidence to support the evaluation.
"""

from typing import Iterator, Any

from DSL4Pipelines.src.tools.queries.manifest_query import ManifestQuery
from DSL4Pipelines.src.tools.queries.metarules import eval_rule, EvaluationResult
from DSL4Pipelines.src.metamodel.artefacts.artefacts import Artefact


@eval_rule(name="Dataset and Model Presence", weight=1.0)
def check_dataset_and_model_presence(ctx: ManifestQuery) -> Iterator[EvaluationResult]:
    """Check if the manifest contains at least one dataset and one model"""
    # 1. Check for the presence of a dataset
    datasets = ctx.get_artifacts(type="Data")
    has_dataset = len(datasets) > 0
    # Respond with a structured result that includes the label, success status, score, and evidence
    yield EvaluationResult(
        label="Availability of dataset",
        success=has_dataset,
        score=1.0 if has_dataset else 0.0,
        evidence=f"Number of datasets: {len(datasets)}",
    )

    # 2. Check for the presence of a model
    models = ctx.get_artifacts(type="MLModel")
    has_model = len(models) > 0
    yield EvaluationResult(
        label="Availability of model",
        success=has_model,
        score=1.0 if has_model else 0.0,
        evidence=f"Number of ML models: {len(models)}",
    )


@eval_rule(name="French Readiness", weight=1.0)
def check_french_support(ctx: ManifestQuery) -> Iterator[EvaluationResult]:
    """This rule evaluates the readiness of the project for French language processing.
    It checks if there are datasets that include French as a language
    and if there are performance metrics that indicate good performance on French benchmarks.
    The rule is designed to give a score based on the presence of French in the datasets
    and the performance on French benchmarks, with a penalty for the presence of other languages."""

    target_languages = {"french", "fr"}

    datasets, has_languages, score = evaluate_language_readiness(ctx, target_languages)

    yield EvaluationResult(
        label="Dataset contient du français",
        success=has_languages,
        score=score,
        evidence=f"Langues trouvées: {[d.languages for d in datasets]}",
    )

    # 2. Vérification des performances
    #@todo : bizarre
    bench_fr = ctx.get_metrics(kind="accuracy")  # , slice="fr-test")

    if bench_fr:
        score = float(bench_fr[0].value)
        yield EvaluationResult(
            label="Performance sur benchmark FR",
            success=score > 0.8,
            score=score,
            evidence=f"Accuracy: {score}",
        )
    else:
        yield EvaluationResult(
            label="Performance sur benchmark FR",
            success=False,
            score=0.0,
            evidence="Aucun benchmark de performance en français trouvé",
        )

@eval_rule(name="English Readiness", weight=1.0)
def check_english_support(ctx: ManifestQuery) -> Iterator[EvaluationResult]:
    """This rule evaluates the readiness of the project for French language processing.
    It checks if there are datasets that include French as a language
    and if there are performance metrics that indicate good performance on French benchmarks.
    The rule is designed to give a score based on the presence of French in the datasets
    and the performance on French benchmarks, with a penalty for the presence of other languages."""

    target_languages = {"en", "eng", "english", "eg"}

    datasets, has_languages, score = evaluate_language_readiness(ctx, target_languages)

    yield EvaluationResult(
        label="Dataset contains English",
        success=has_languages,
        score=score,
        evidence=f"Found languages: {[d.languages for d in datasets]}",
    )

def evaluate_language_readiness(ctx: ManifestQuery, target_languages: set[str]) -> tuple[
    set[Any], float, list[Artefact]]:
    # 1. Vérification des données
    datasets = ctx.get_artifacts(type="Data")
    # collect all languages from all datasets and check if "french" is among them
    languages = {lang.strip().lower() for d in datasets for lang in d.languages}
    has_languages = languages.intersection(target_languages)
    # has_fr = "french" in languages or "fr" in languages

    score = 0.0
    if has_languages:
        score = (
                1.0 - (len(languages) - 1) * 0.2
        )  # pénalité de 0.2 pour chaque langue étrangère supplémentaire
    return datasets, has_languages, score


@eval_rule(name="Pureté Linguistique Globale", weight=2.0)
def rule_global_french_purity(ctx):
    """This rule evaluates the overall "purity" of the project in terms of French language support.
    It checks all datasets in the manifest and
    calculates a score based on the presence of French and the number of other languages.
    The idea is that a project that has only French datasets gets a score of 1.0,
    while the presence of other languages reduces the score.
    A project with no French datasets gets a score of 0.0.
    """


    target_languages = {"french", "fr"}

    all_scores, final_score = evaluate_purety(ctx, target_languages)

    yield EvaluationResult(
        label="Pipeline Global",
        success=final_score > 0.5,
        score=round(final_score, 2),
        evidence=f"Analyse sur {len(all_scores)} datasets.",
    )

@eval_rule(name="Language purity", weight=2.0)
def rule_global_english_purity(ctx):
    """This rule evaluates the overall "purity" of the project in terms of english language support.
    It checks all datasets in the manifest and
    calculates a score based on the presence of French and the number of other languages.
    The idea is that a project that has only French datasets gets a score of 1.0,
    while the presence of other languages reduces the score.
    A project with no French datasets gets a score of 0.0.
    """
    target_languages = {"en","eg", "english","eng"}

    all_scores, final_score = evaluate_purety(ctx, target_languages)

    yield EvaluationResult(
        label="Pipeline Global",
        success=final_score > 0.5,
        score=round(final_score, 2),
        evidence=f"Analyse on {len(all_scores)} datasets.",
    )

def evaluate_purety(ctx, target_languages: set[str]) -> tuple[float, list[Any]]:
    all_scores = []
    datasets = ctx.get_artifacts(type="Data")
    for d in datasets:
        langs = [l.lower() for l in d.languages]

        if any(lang in target_languages for lang in langs):
            # Score de pureté : 1.0 si seul, baisse si multilingue
            purity = 1.0 / len(langs)
            all_scores.append(purity)
        else:
            # Un dataset sans français du tout fait chuter la moyenne
            all_scores.append(0.0)

    if not all_scores:
        final_score = -1.0  # Indique l'absence totale de datasets
    else:
        final_score = sum(all_scores) / len(all_scores)
    return all_scores, final_score


@eval_rule(name="Ratio de Spécialisation", weight=1.0)
def rule_pollution_ratio(ctx):
    """This rule calculates a "pollution ratio" based on the number of datasets
    that contain French and the number of other languages present in those datasets.
    The idea is that if there are many datasets with French
    but also many other languages, the score will be lower.
    The score is calculated as the number of datasets with French
    divided by the total number of datasets with French
    plus the number of unique "polluting" languages.
    """
    datasets_with_fr = 0
    unique_foreign_langs = set()

    datasets = ctx.get_artifacts(type="Data")
    for d in datasets:
        langs = {l.lower() for l in d.languages}
        if "french" in langs:
            datasets_with_fr += 1
            # On ajoute toutes les langues sauf le français au set des "polluants"
            unique_foreign_langs.update(langs - {"french"})

    # Plus il y a de langues étrangères différentes dans le projet,
    # plus le dénominateur augmente et le score baisse.
    if datasets_with_fr == 0:
        score = 0.0
    else:
        score = datasets_with_fr / (datasets_with_fr + len(unique_foreign_langs))

    yield EvaluationResult(
        label="Cohérence Linguistique",
        success=score > 0.6,
        score=round(score, 2),
        evidence=f"{len(unique_foreign_langs)} langues parasites détectées.",
    )


#@eval_rule(name="Pureté Linguistique Globale", weight=2.0)
def rule_analyze_modelCard_fields(ctx):
    mcs = ctx.get_artifacts(type="ModelCard")
    #get the model name ???
    model_name = mcs.get("name", "Unknown Model")
    print(f"--- Analysis Report for: {model_name} ---")
    # 1. Vérification des "Considerations" (Ethique/Usage)
    considerations = mcs.get("modelCard", {}).get("considerations", {})
    use_cases = considerations.get("useCases", "")

    # On vérifie si c'est vide ou si ça contient juste le template par défaut
    is_documented = bool(use_cases and use_cases.strip() and use_cases.strip() != "Describe the intended use cases for this model here.")


# --- Usage Examples ---
# =====================================================================
# ---Test bloc and usage example---
# =====================================================================
if __name__ == "__main__":
    # On peut tester les règles sur un manifest de test
    from DSL4Pipelines.tests.examples.NotebookIRISManifest import (
        test_build_manifestFromNBonIrisClassification,
    )

    manifest = test_build_manifestFromNBonIrisClassification()

    manifestQuery = ManifestQuery(manifest)
    # On exécute la fonction de l'expert
    res = check_dataset_and_model_presence(manifestQuery)
    print("Results for 'Dataset and Model Presence' rule:")
    for r in res:
        print(
            f"  {r.label}: {'✅' if r.success else '❌'} (Score: {r.score}) - Evidence: {r.evidence}"
        )

#    engine = EvaluationEngine()
#    rules = list
#    report = engine.run_rules(manifest, rules)
#    print(report)

