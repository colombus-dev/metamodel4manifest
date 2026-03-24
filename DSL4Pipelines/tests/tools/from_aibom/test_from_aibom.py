from pathlib import Path

from DSL4Pipelines.src.tools.from_aibom.aibom_translator import AIBOMTranslator
from DSL4Pipelines.src.metamodel.manifests.manifests import Manifest
from DSL4Pipelines.src.tools.toFile import save_in_file
from DSL4Pipelines.src.tools.transformations.yamlSerializer import YAMLSerializer


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
OUTPUT = str(BASE_DIR /'DSL4Pipelines/tests/examples/outputs/aibom/')

def test_build_sofwareFile():
    print(f"\nBase directory: {BASE_DIR}")
    nom_fichier = BASE_DIR/'aiboms/0xJustin_Dungeons-and-Diffusion.json'

    translator = AIBOMTranslator(str(nom_fichier))
    file = translator.build_sofware_file_for_aibom()
    print(f"Fichier AIBOM transformé en artefact : {file}")

def test_build_model():
    nom_fichier = BASE_DIR/'aiboms/0xJustin_Dungeons-and-Diffusion.json'
    translator = AIBOMTranslator(str(nom_fichier))
    model = translator.build_model()
    print(f"Model Card  transformed into MLModel artifact : {model}")

def test_transform_aibom_to_manifest():
    nom_fichier = BASE_DIR/'aiboms/0xJustin_Dungeons-and-Diffusion.json'
    translator = AIBOMTranslator(str(nom_fichier))
    nom_fichier = BASE_DIR/'aiboms/1bitLLM_bitnet_b1_58-3B.json'
    check_transform_aibom(str(nom_fichier))
    nom_fichier= BASE_DIR/'aiboms/agentica-org_DeepScaleR-1.5B-Preview.json'
    check_transform_aibom(str(nom_fichier))
    nom_fichier= BASE_DIR/'aiboms/albert_albert-base-v2.json'
    check_transform_aibom(str(nom_fichier))


def check_transform_aibom(nom_fichier: str) -> Manifest:
    translator = AIBOMTranslator(nom_fichier)
    manifest = translator.transform_aibom_to_manifest()
    print(f"Manifest generated from AIBOM : {manifest}")
    yaml_output = YAMLSerializer.to_yaml(manifest, True)
    file_name = nom_fichier.split('/')[-1].replace('.json', '.yaml')
    save_in_file(OUTPUT, file_name, yaml_output)
    print(f"Manifest saved in yaml format in : {OUTPUT + file_name}")
    return manifest


def test_transform_complexe_aibom():
    nom_fichier= BASE_DIR/'aiboms/agentica-org_DeepScaleR-1.5B-Preview.json'
    manifest = check_transform_aibom(str(nom_fichier))
    artefacts = manifest.artefacts
    assert len(artefacts) == 8, f"Expected 8 artefacts, but got {len(artefacts)}"
    datasets = [a for a in artefacts if a.type == "Data"]
    assert len(datasets) ==4, f"Expected 4 datasets, but got {len(datasets)}"
    print("✅ The manifest contains the expected number of datasets.")
    for dataset in datasets:
        assert dataset.languages==["en"], f"Expected content type 'dataset', but got {dataset.content_type}"
    mlmodel = [a for a in artefacts if a.type == "MLModel"]
    assert len(mlmodel) == 2, f"Expected 1 MLModel, but got {len(mlmodel)}"

    softwares = [a for a in artefacts if a.type == "SoftwareFile" ]
    print(f"libraries : {softwares}")
    libraries = [a for a in softwares if a.content_type == "library" ]
    assert len(libraries) == 1, f"Expected 1 libraries, but got {len(libraries)}"
    assert libraries[0].name == "transformers", f"Expected library name 'transformers', but got {libraries[0].name}"
    print("✅ The manifest contains the expected number of libraries.")

    relations = manifest.relations
    assert len(relations) == 5, f"Expected 5 relations, but got {len(relations)}"
    print("✅ The manifest contains the expected number of relations.")

    derived_from = [r for r in relations if r.relationship_type == "derivedFrom"]
    assert len(derived_from) == 1, f"Expected 1 relation of type 'derivedFrom', but got {len(derived_from)}"
    assert derived_from[0].from_.type == "MLModel", f"Expected 'from' element of type 'MLModel', but got {derived_from[0].from_.type}"
    assert derived_from[0].to_[0].type == "MLModel", f"Expected 'to' element of type 'MLModel', but got {derived_from[0].to_[0].type}"
    print("✅ The 'derivedFrom' relation links the expected types of artefacts.")

    uses = [r for r in relations if r.relationship_type == "uses"]
    assert len(uses) == 2, f"Expected 2 relations of type 'uses', but got {len(uses)}"
    print("✅ The manifest contains the expected number of 'uses' relations.")
    assert uses[0].from_.type == "MLModel"
    if (len(uses[0].to_) >1):
        assert uses[0].to_[0].type == "Data"
    else:
        assert uses[0].to_[0].type == "SoftwareFile"
    assert uses[1].from_.type == "MLModel"
    if (len(uses[1].to_) >1): #dataset...
        assert uses[1].to_[0].type == "Data"
    else: #library
        assert uses[1].to_[0].type == "SoftwareFile"
    print("✅ The 'uses' relations link the expected types of artefacts.")

    rel_annotated_by = [r for r in relations if r.relationship_type == "annotatedBy"]
    assert len(rel_annotated_by) == 1, f"Expected 1 relation of type 'annotatedBy', but got {len(rel_annotated_by)}"
    assert rel_annotated_by[0].from_.type == "Manifest", f"Expected 'from' element of type 'Manifest', but got {rel_annotated_by[0].from_.type}"
    assert rel_annotated_by[0].to_[0].type == "SoftwareFile"
    print("✅ The 'annotatedBy' relation links the expected types of elements.")

    rel_produces = [r for r in relations if r.relationship_type == "produces"]
    assert len(rel_produces) == 1, f"Expected 1 relation of type 'produces', but got {len(rel_produces)}"
    assert rel_produces[0].from_.type == "Manifest", f"Expected 'from' element of type 'SoftwareFile', but got {rel_produces[0].from_.type}"
    assert rel_produces[0].to_[0].type == "MLModel", f"Expected 'to' element of type 'MLModel', but got {rel_produces[0].to_[0].type}"
    print("✅ The 'produces' relation links the expected types of elements.")



#@todo : add more tests on the content of the artefacts, and on the properties of the relations
def test_transform_aibom_with_metrics():
    file_path= '../../aiboms/BAAI_bge-multilingual-gemma2.json'







