from typing import Iterator


from DSL4Pipelines.src.tools.queries.evaluation_engine import EvaluationEngine
from DSL4Pipelines.src.tools.queries.rules.rules import (
    check_dataset_and_model_presence,
    check_french_support,
)
from DSL4Pipelines.tests.examples.NotebookIRISManifest import (
    test_build_manifestFromNBonIrisClassification,
)
from DSL4Pipelines.src.tools.queries.manifest_query import ManifestQuery
from DSL4Pipelines.src.tools.queries.metarules import EvaluationResult, RULE_REGISTRY


def test_rules():
    manifest = test_build_manifestFromNBonIrisClassification()

    rules = [check_dataset_and_model_presence, check_french_support]
    engine = EvaluationEngine()
    report = engine.run_rules(manifest, rules)
    print(report)

def test_rule_evaluate():
    manifest = test_build_manifestFromNBonIrisClassification()

    mq = ManifestQuery(manifest)
    rule = check_dataset_and_model_presence
    result = rule(mq)
    assert isinstance(result, Iterator), "Expected an iterator of EvaluationResult"
    for r in result:
        assert isinstance(r, EvaluationResult), "Expected an EvaluationResult instance"
        print(
            f"  {r.label}: {'✅' if r.success else '❌'} (Score: {r.score}) - Evidence: {r.evidence}"
        )


def test_rules_on_iris_nb():
    manifest = test_build_manifestFromNBonIrisClassification()
    manifestQuery = ManifestQuery(manifest)
    # On exécute la fonction de l'expert
    res: Iterator[EvaluationResult] = check_dataset_and_model_presence(manifestQuery)
    print("\n Results for 'Dataset and Model Presence' rule:")
    results_list = list(res)
    assert len(results_list) == 2
    for r in results_list:
        print(
            f"  {r.label}: {'✅' if r.success else '❌'} (Score: {r.score}) - Evidence: {r.evidence}"
        )
    assert results_list[0].success
    assert results_list[0].score == 1.0
    assert results_list[0].label == "Availability of dataset"
    assert results_list[0].evidence == "Number of datasets: 1"
    assert results_list[1].success
    assert results_list[1].score == 1.0
    assert results_list[1].label == "Availability of model"
    assert results_list[1].evidence == "Number of ML models: 1"
