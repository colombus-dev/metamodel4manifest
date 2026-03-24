from DSL4Pipelines.src.tools.from_aibom.aibom_translator import AIBOMTranslator
from DSL4Pipelines.src.tools.queries.manifest_query import ManifestQuery
from DSL4Pipelines.src.tools.queries.rules.rules import check_dataset_and_model_presence
from tools.from_aibom.aibom_manager import AIBOMManager
from tools.toFile import check_file_or_dict_exists, print_cwd, save_in_file
from tools.transformations.yamlSerializer import YAMLSerializer

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


PATH_AIBOMS = '../../aiboms'

def test_build_AIBOMManager():
    print_cwd()
    path = PATH_AIBOMS
    manager = AIBOMManager(path)
    assert len(manager.aibom_files) == 312, f"Expected 4 AIBOM files, but got {len(manager.aibom_files)}"
    assert len(manager.manifests) == 312, f"Expected 4 manifests, but got {len(manager.manifests)}"
    print("✅ AIBOM Manager built successfully with the expected number of AIBOM files and manifests.")

def test_save_AIBOMManager():
    print_cwd()
    path = PATH_AIBOMS
    manager = AIBOMManager(path)
    output_path = 'aibom_manifests_yaml/'
    manager.save_manifests_in_yaml(output_path)
    # we check that the files are saved in the output path
    for manifest_name in manager.manifests:
        file_name = manifest_name.replace('.json', '.yaml')
        file_path = output_path + file_name
        assert check_file_or_dict_exists(file_path), f"Expected file {file_path} to be saved, but it does not exist."
    logger.info("✅ All manifests saved successfully in yaml format in the output path.")
def test_save_stranger():
    path = PATH_AIBOMS+'/strangerzonehf_Flux-Super-Realism-LoRA.json'
    manifest = AIBOMTranslator(path).transform_aibom_to_manifest()
    output = YAMLSerializer.to_yaml(manifest, True)
    output_path = 'aibom_manifests_yaml/'
    file_name = path.split('/')[-1].replace('.json', '.yaml')
    save_in_file(output_path, file_name, output)
    file_path = output_path + file_name
    assert check_file_or_dict_exists(file_path), f"Expected file {file_path} to be saved, but it does not exist."

def test_filter_manifests_by_rule_llama():
    path = PATH_AIBOMS
    manager = AIBOMManager(path)
    #we define a rule that says that the model must be based on a transformer architecture, we will check if the manifest contains an MLModel artefact with a property "ml_model_type" with value "Transformer", and we will keep only the manifests that contain such an artefact.
    def rule(mq: ManifestQuery) -> bool:
        ml_models = mq.get_artifacts("MLModel")
        for ml_model in ml_models:
            if ml_model.properties and ml_model.properties.get("architectureFamily") == "llama" and ml_model.purpose == "text-generation" and ml_model.properties.get("modelArchitecture")== "LlamaForCausalLM":
                return True
        return False
    results = manager.filter_manifests_by_rule(rule)
    assert len(results) == 48, f"Expected 55 manifests that validate the rule, but got {len(results)}"
    logger.debug(f"Manifests that validate the rule : {len(results)}")
    #print(f"First result: {results[0]}")
    for manifest in results:
        ml_models = [a for a in manifest.artefacts if a.type == "MLModel"]
        assert len(ml_models) > 0, f"Expected at least one MLModel artefact in the manifest, but got {len(ml_models)}"
        check_property = False
        for ml_model in ml_models:
            if ml_model.properties and ml_model.properties.get("architectureFamily") == "llama" and ml_model.purpose == "text-generation" and ml_model.properties.get("modelArchitecture")== "LlamaForCausalLM":
                check_property = True
                break
        assert check_property, f"Expected at least one MLModel artefact with the expected properties in the manifest, but got none."

    logger.info("✅ All manifests that validate the rule have the expected properties in their MLModel artefact.")
    for manifest in results:
        name = manager.get_file_name_from_manifest(manifest)
        print(f"MLModel artefact in the manifest {name}")


def test_filter_manifests_by_rule_gpt():
    path = PATH_AIBOMS

    manager = AIBOMManager(path)
    #we define a rule that says that the model must be based on a transformer architecture, we will check if the manifest contains an MLModel artefact with a property "ml_model_type" with value "Transformer", and we will keep only the manifests that contain such an artefact.
    def rule(mq: ManifestQuery) -> bool:
        ml_models = mq.get_artifacts("MLModel")
        for ml_model in ml_models:
            if (ml_model.properties
                    and ml_model.properties.get("architectureFamily")
                    and "gpt" in ml_model.properties.get("architectureFamily")
                    and ml_model.purpose == "text-generation"):
                return True
        return False
    results = manager.filter_manifests_by_rule(rule)
    #assert len(results) == 8, f"Expected 8 manifests that validate the rule, but got {len(results)}"
    logger.debug(f"Manifests that validate the rule : {len(results)}")
    #print(f"First result: {results[0]}")
    for manifest in results:
        ml_models = [a for a in manifest.artefacts if a.type == "MLModel"]
        assert len(ml_models) > 0, f"Expected at least one MLModel artefact in the manifest, but got {len(ml_models)}"
        check_property = False
        for ml_model in ml_models:
            if (ml_model.properties
                    and ml_model.properties.get("architectureFamily")
                    and "gpt" in ml_model.properties.get("architectureFamily")
                    and ml_model.purpose == "text-generation"):
                check_property = True
                break
        assert check_property, f"Expected at least one MLModel artefact with the expected properties in the manifest, but got none."

    logger.info("✅ All manifests that validate the rule have the expected properties in their MLModel artefact.")
    for manifest in results:
        name = manager.get_file_name_from_manifest(manifest)
        print(f"MLModel artefact in the manifest {name}")

def test_filter_manifests_by_rule_purpose():
    path = PATH_AIBOMS

    manager = AIBOMManager(path)
    #we define a rule that says that the model must be based on a transformer architecture, we will check if the manifest contains an MLModel artefact with a property "ml_model_type" with value "Transformer", and we will keep only the manifests that contain such an artefact.
    def rule(mq: ManifestQuery) -> bool:
        ml_models = mq.get_artifacts("MLModel")
        for ml_model in ml_models:
            if (ml_model.purpose == "text-generation"):
                return True
        return False
    results = manager.filter_manifests_by_rule(rule)
    #assert len(results) == 8, f"Expected 8 manifests that validate the rule, but got {len(results)}"
    print(f"Manifests that have for purpose text-generation : {len(results)}")

    def rule(mq: ManifestQuery) -> bool:
        ml_models = mq.get_artifacts("MLModel")
        for ml_model in ml_models:
            if (ml_model.purpose != "text-generation"):
                return True
        return False
    results = manager.filter_manifests_by_rule(rule)
    #assert len(results) == 8, f"Expected 8 manifests that validate the rule, but got {len(results)}"
    print(f"Manifests that do'nt have for purpose text-generation : {len(results)}")


def test_filter_manifests_by_rule_r():
    path = PATH_AIBOMS
    manager = AIBOMManager(path)
    #we define a rule that says that the model must be based on a transformer architecture, we will check if the manifest contains an MLModel artefact with a property "ml_model_type" with value "Transformer", and we will keep only the manifests that contain such an artefact.
    manifests = manager.filter_manifests_by_rule(check_dataset_and_model_presence)
    assert len(manifests) == 312, f"Expected 312 manifests that validate the rule check_dataset_and_model_presence, but got {len(manifests)}"
    logger.debug(f"Manifests that validate the rule check_dataset_and_model_presence : {len(manifests)}")