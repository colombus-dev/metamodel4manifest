from DSL4Pipelines.src.metamodel.manifests.manifests import Manifest
from DSL4Pipelines.src.tools.queries.evaluation_engine import EvaluationEngine
from DSL4Pipelines.src.tools.queries.metarules import RuleReport
from DSL4Pipelines.src.tools.queries.rules.rules import (
    check_dataset_and_model_presence,
    check_french_support,
)
from DSL4Pipelines.src.tools.toFile import save_in_file
from DSL4Pipelines.src.tools.transformations.YAMLSerializer import YAMLSerializer

from DSL4Pipelines.src.tools.transformations.toMermaid import MERMAIDSerializer

PATH = "/Users/mireillefornarino/GIT/RECHERCHES/metamodele4manifest/DSL4Pipelines/tests/examples/sources/"
OUTPUT = "/Users/mireillefornarino/GIT/RECHERCHES/metamodele4manifest/DSL4Pipelines/tests/examples/outputs/"


def test_demo():
    manifest = step1()
    print(manifest)
    (step2(manifest),)
    step3_4()
    step5()
    step6()


def test_demo_bis():
    manifest = step1Bis()
    print(manifest)
    (step2Bis(manifest),)
    step5Bis()
    step6Bis()


def step1() -> Manifest:
    print("-------------------- Step 1: Read Manifest Yaml file for nanoGPT")
    file = PATH + "nanoGPT_manifest.yaml"
    manifest = YAMLSerializer.from_yaml_file(file, Manifest)
    return manifest


def step1Bis() -> Manifest:
    print(
        "-------------------- Step 1: Read Manifest Yaml file for iris classification"
    )
    file = PATH + "iris_manifest.yaml"
    manifest = YAMLSerializer.from_yaml_file(file, Manifest)
    return manifest


def step2(manifest: Manifest):
    print("-------------------- Step 2: Run rules on the manifest")
    # Here you would run your rules on the manifest and generate a report
    # For example:
    rules = [check_dataset_and_model_presence, check_french_support]
    engine = EvaluationEngine()
    # report
    # report: list[RuleReport] = engine.run_rules(manifest, rules)
    report: list[RuleReport] = engine.run_rules(manifest, rules)
    print("==> Generate report and save it to a file")
    print(report)
    for r in report:
        print(r)
    save_in_file(OUTPUT, "report_step2.txt", str(report))


def step2Bis(manifest: Manifest):
    print("-------------------- Step 2: Run rules on the Iris manifest")
    # Here you would run your rules on the manifest and generate a report
    # For example:
    rules = [check_dataset_and_model_presence, check_french_support]
    engine = EvaluationEngine()
    # report
    # report: list[RuleReport] = engine.run_rules(manifest, rules)
    report: list[RuleReport] = engine.run_rules(manifest, rules)
    print("==> Generate report and save it to a file")
    print(report)
    for r in report:
        print(r)
    save_in_file(OUTPUT, "report_step2Bis.txt", str(report))


def step3_4():
    print("--------------------  Step 3: Read Manifest Yaml file after completion")
    manifest = YAMLSerializer.from_yaml_file(
        PATH + "nanoGPT_manifest2.yaml",
        Manifest,
    )
    print("Step 4: Run one rule on the manifest")
    # Here you would run your rules on the manifest and generate a report
    # For example:
    rules = [check_french_support]
    engine = EvaluationEngine()
    # report
    # report: list[RuleReport] = engine.run_rules(manifest, rules)
    report: list[RuleReport] = engine.run_rules(manifest, rules)
    print("==> Generate report and save it to a file")
    print(report)
    for r in report:
        print(r)


def step5():
    print("-------------------- Step 5: Run all rules on the manifest")
    # Here you would run your rules on the manifest and generate a report
    # For example:
    manifest = YAMLSerializer.from_yaml_file(
        PATH + "nanoGPT_manifest2.yaml",
        Manifest,
    )
    engine = EvaluationEngine()
    report: list[RuleReport] = engine.run_all(manifest)
    print("==> Generate report")
    print(report)
    for r in report:
        print(r)


def step5Bis():
    print("-------------------- Step 5: Run all rules on the manifest")
    # Here you would run your rules on the manifest and generate a report
    # For example:
    manifest = YAMLSerializer.from_yaml_file(
        PATH + "iris_manifest.yaml",
        Manifest,
    )
    engine = EvaluationEngine()
    report: list[RuleReport] = engine.run_all(manifest)
    print("==> Generate report")
    print(report)
    for r in report:
        print(r)


def step6():
    print("-------------------- Step 6: Generate a mermaid file from the manifest")
    manifest = YAMLSerializer.from_yaml_file(PATH + "nanoGPT_manifest2.yaml", Manifest)
    serialiser: MERMAIDSerializer = MERMAIDSerializer()
    mermaid_str = serialiser.object_to_mermaid_full(manifest)
    save_in_file(OUTPUT, "nanoGPT_manifest2.mmd", mermaid_str)


def step6Bis():
    print("-------------------- Step 6: Generate a mermaid file from the manifest")
    manifest = YAMLSerializer.from_yaml_file(PATH + "iris_manifest.yaml", Manifest)
    serialiser: MERMAIDSerializer = MERMAIDSerializer()
    mermaid_str = serialiser.object_to_mermaid_full(manifest)
    save_in_file(OUTPUT, "iris_manifest.mmd", mermaid_str)


def main():
    test_demo()
    test_demo_bis()
