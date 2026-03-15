####
# Operationalization of Income Prediction justification
####

import json
import re

import keras
import keras.models
import src.helper as helper
import pandas as pd

from tensorflow.python.data.ops.dataset_ops import DatasetV2

from pathlib import Path
from typing import Any

from DSL4Pipelines.examples_original_version.for_fairness_income.helper import SENSITIVE_ATTRIBUTE_KEY

MODEL: keras.Model | None = None
MITIGATED_MODEL: keras.Model | None = None
DATASET_TEST: DatasetV2 | None = None
EVALUATION_RESULTS: dict[str, Any] | None = None
EVALUATION_RESULTS_MITIGATED_MODEL: dict[str, Any] | None = None


# Strategies "verify accuracy" and "verify auc" in "release_model"

def evaluating_model_on_test_dataset() -> dict[str, Any]:
    global EVALUATION_RESULTS

    if EVALUATION_RESULTS is None:
        EVALUATION_RESULTS  = MODEL.evaluate(DATASET_TEST, batch_size=helper.BATCH_SIZE, return_dict=True)

    return EVALUATION_RESULTS

# Strategy "verify accuracy" in "release_model"
def verifying_accuracy_is_acceptable() -> bool:
    evaluation_results  = evaluating_model_on_test_dataset()
    return evaluation_results["accuracy"] > 0.8

# Strategy "verify auc" in "release_model"
def verifying_auc_is_acceptable() -> bool:
    evaluation_results  = evaluating_model_on_test_dataset()
    print (evaluation_results["false_positives"], evaluation_results["false_negatives"])
    return evaluation_results["auc"] > 0.8


# Evidence "model" in "release_model"
def trained_model_is_available() -> bool:
    global MODEL

    if Path("./out/model.keras").exists():
        MODEL = keras.models.load_model("out/model.keras")
        return True
    return False

# --------- Strategy "verify mitigation accuracy tradeoff" in "release_model"

def evaluating_mitigated_model_on_test_dataset():
    global EVALUATION_RESULTS_MITIGATED_MODEL

    if EVALUATION_RESULTS_MITIGATED_MODEL is None:
        EVALUATION_RESULTS_MITIGATED_MODEL  = MITIGATED_MODEL.evaluate(DATASET_TEST, batch_size=helper.BATCH_SIZE, return_dict=True)

    return EVALUATION_RESULTS_MITIGATED_MODEL

def verifying_mitigation_accuracy_tradeoff() -> bool:
    evaluation_results  = evaluating_mitigated_model_on_test_dataset()
    return evaluation_results["accuracy"] > 0.75

# Evidence "model" in "release_model"
def mitigated_model_is_available() -> bool:
    global MITIGATED_MODEL

    if Path("./out/model_remediated.keras").exists():
        MITIGATED_MODEL = keras.models.load_model("out/model_remediated.keras")
        return True
    return False

# Evidence "dataset" in "release_model"
def test_dataset_is_available() -> bool:
    global DATASET_TEST

    if (test_dataset_path := Path("out/test_dataset.csv")).exists():
        acs_test_df = pd.read_csv(test_dataset_path)
        DATASET_TEST = helper.dataframe_to_tf_batches(acs_test_df)
        return True
    return False


PROFILE: dict[str, Any] | None = None
REGEX_COMPATIBLE_PROFILE: str | None = None
MINDIFF_REGEX_PATTERN: str | None = None

# Strategy "verify_profile_remediation" in "release_model"
def verifying_profile_contains_a_remediation_model() -> bool:
    regex = re.compile(MINDIFF_REGEX_PATTERN, re.MULTILINE)
    return regex.search(REGEX_COMPATIBLE_PROFILE)

# Evidence "profile" in "release_model"
def workflow_profile_is_available() -> bool:
    global PROFILE

    if (wf_profile_json_path := Path("./docs/remediation_exploration_profile.json")).exists():
        with open(wf_profile_json_path) as f:
            PROFILE = json.load(f)
        return True
    return False

# Evidence "regex_compatible_profile" in "release_model"
def workflow_regexcompatible_profile_is_available() -> bool:
    global REGEX_COMPATIBLE_PROFILE

    if (regex_compatible_profile_path := Path("./docs/regex_compatible_profile.json")).exists():
        with open(regex_compatible_profile_path) as f:
            REGEX_COMPATIBLE_PROFILE = f.read()
        return True
    return False

# Evidence "mindiff_regex_pattern" in "release_model"
def min_diff_regex_pattern_is_available() -> bool:
    global MINDIFF_REGEX_PATTERN

    if (mindiff_regex_pattern_path := Path("./docs/mindiff_pattern_regex.txt")).exists():
        with open(mindiff_regex_pattern_path) as f:
            MINDIFF_REGEX_PATTERN = f.read()
        return True
    return False


VISUAL_PROFILE: Path | None = None

# Strategy "verify_transparency_artefacts" in "release_model"
def verifying_transparency_artefacts() -> bool:
    # TODO: read profile plantUML content
    return VISUAL_PROFILE.is_file() and VISUAL_PROFILE.suffix == ".puml"

# Evidence "visual_profile" in "release_model"
def visual_workflow_profile_is_available() -> bool:
    global VISUAL_PROFILE

    if (wf_profile_plantuml_path := Path("./docs/remediation_exploration_profile.puml")).exists():
        VISUAL_PROFILE = wf_profile_plantuml_path
        return True
    return False


FAIRNESSLENS_REPORT_PDF: Path | None = None

# Strategy "verify_fairness_artefacts" in "release_model"
def verifying_fairness_artefacts() -> bool:
    # TODO: read fairnessless pdf report content
    return FAIRNESSLENS_REPORT_PDF.is_file() and FAIRNESSLENS_REPORT_PDF.suffix == ".pdf"

# Evidence "fairnesslens_report" in "release_model"
def fairness_lens_pdf_report_is_available() -> bool:
    global FAIRNESSLENS_REPORT_PDF

    if (fairnesslens_report_path := Path("./docs/fairness-income_fairness_report.pdf")).exists():
        FAIRNESSLENS_REPORT_PDF = fairnesslens_report_path
        return True
    return False

RAIL_MODEL_LICENSE: Path | None = None

# Strategy "verify_ethics_artefacts" in "release_model"
def verifying_ethics_artefacts() -> bool:
    expected_license_subcontent = "~~~\n\n### **fairness-income RESEARCH-ONLY RAIL-M**\n\nLicensed Artifact(s):\n\n   - Model\n\n\n**Section I: PREAMBLE**"
    with open(RAIL_MODEL_LICENSE) as f:
        license_content = f.read()
        return expected_license_subcontent in license_content

# Evidence "model_license" in "release_model"
def rail_model_license_is_available() -> bool:
    global RAIL_MODEL_LICENSE

    return (RAIL_MODEL_LICENSE := Path("./docs/fairness-income-ResearchRAIL.md")).exists()


def check_fairness_violation(eval_result, sensitive_feature, threshold=0.1):
    """
    Vérifie si l'écart de FNR entre les groupes dépasse un seuil.
    """
    # 1. Extraire les métriques par slice
    slices = eval_result.slicing_metrics

    fnr_values = {}

    for s in slices:
        # On cherche la slice correspondant à notre attribut sensible (ex: 'gender')
        feature_name = str(s[0])
        if sensitive_feature in feature_name or feature_name == "()": # () est la slice globale
            # Extraction du False Negative Rate à partir de la Confusion Matrix à 0.5
            # Note: TFMA stocke souvent cela dans 'fn' et 'tp' pour calculer le taux
            metrics = s[1]['']['']

            # Calcul du FNR = FN / (FN + TP)
            fn = metrics['false_negatives']['doubleValue']
            tp = metrics['true_positives']['doubleValue']
            fnr = fn / (fn + tp) if (fn + tp) > 0 else 0

            label = feature_name if feature_name != "()" else "Global"
            fnr_values[label] = fnr

    # 2. Calculer l'écart maximum (Gap)
    if len(fnr_values) > 1:
        values = [v for k, v in fnr_values.items() if k != "Global"]
        fnr_gap = max(values) - min(values)

        is_fair = fnr_gap <= threshold
        print(f"--- Fairness Report for {sensitive_feature} ---")
        for group, val in fnr_values.items():
            print(f"Group {group}: FNR = {val:.4f}")
        print(f"Detected FNR Gap: {fnr_gap:.4f}")
        print(f"Status: {'PASS' if is_fair else 'FAIL'} (Threshold: {threshold})")

        return is_fair, fnr_gap

    return False, 0


def check_fairness_violation_on_mitigates_model() -> bool:
    evaluation_results  = evaluating_model_on_test_dataset()

    # Utilisation
    is_fair, gap = check_fairness_violation(evaluation_results, SENSITIVE_ATTRIBUTE_KEY)
    # Utilisation
    return is_fair