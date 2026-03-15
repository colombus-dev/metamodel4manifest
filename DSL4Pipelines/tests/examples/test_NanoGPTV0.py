from typing import List

from DSL4Pipelines.src.metamodel.artefacts.ml_artefacts import MLModel, Data
from DSL4Pipelines.src.metamodel.artefacts.artefacts import SoftwareFile, Artefact
from DSL4Pipelines.src.metamodel.catalogs.artefact_catalog import ArtefactCatalog
from DSL4Pipelines.src.metamodel.catalogs.DatasetCatalog import DatasetCatalog
from DSL4Pipelines.src.metamodel.catalogs.vocabulary import RelationshipType
from DSL4Pipelines.src.metamodel.manifests.manifests import Manifest
from DSL4Pipelines.src.metamodel.pipelines.workflow import Pipeline, Task
from DSL4Pipelines.src.metamodel.relations.relations import Relationship
from DSL4Pipelines.src.tools.toFile import save_in_file
from DSL4Pipelines.src.tools.transformations.YAMLSerializer import YAMLSerializer
from DSL4Pipelines.src.metamodel.taxonomies.taxonomy import cripDM_Taxonomy
from tools.transformations.toMermaid import MERMAIDSerializer


def test_nanoGPT_manifest() -> Manifest:
    manifest_nanoGPT = Manifest("nanoGPT manifest")
    manifest_nanoGPT.pipeline = test_nanoGPT_pipeline()
    manifest_nanoGPT.artefacts = test_nanoGPT_artefacts()
    manifest_nanoGPT.relations = create_relations(manifest_nanoGPT)
    assert manifest_nanoGPT.pipeline is not None, "Pipeline is not set in the manifest"
    return manifest_nanoGPT


# ------------------------------------------------------------------------------
# ---------------------------- Tests for artefacts ----------------------------
# ------------------------------------------------------------------------------
def test_nanoGPT_artefacts() -> List:
    artefacts = []
    artefacts.append(test_nanoGPT_MLModel())
    artefacts.append(test_nanoGPT_openWebText())
    artefacts.append(test_nanoGPT_vocabulary())
    artefacts.append(test_nanoGPT_tokenizer_code())
    artefacts.append(test_nanoGPT_model_weights())
    artefacts.append(test_nanoGPT_training_config())

    return artefacts


# Artefact definitions
def test_nanoGPT_MLModel() -> MLModel:
    gpt_model = MLModel(name="nanoGPT Model")
    gpt_model.properties = {
        "model_type": "GPT2",
        "framework": "PyTorch",
        "model_size": "124M",
    }
    errors = []
    isValid = gpt_model.validate(errors)
    assert isValid, f"MLModel validation failed with errors: {errors}"
    return gpt_model


def test_nanoGPT_openWebText() -> Data:
    openWebText = Data(
        name="openWebText",
        description="a reconstructed 'open' version of the GPT2 training corpus \n based on the data published in the GPT2 technical report, \n This corpus was constructed from the code located on code_ref",
        data_types=["text"],
        dataset_kinds=["corpus"],
        data_formats=[".txt"],
        software_download_location="https://huggingface.co/datasets/Skylion007/openwebtext",
        access=ArtefactCatalog.ACCESS.PRIVATE,
        license="none",
        properties={"code_ref": "https://github.com/jcpeterson/openwebtext"},
    )
    errors = []
    isValid = openWebText.validate(errors)
    assert isValid, f"Data validation failed with errors: {errors}"
    return openWebText


def test_nanoGPT_vocabulary() -> Data:
    vocabulary = Data(
        name="vocabulary",
        category=ArtefactCatalog.CATEGORIES.VOCABULARY,
        description="The generated ...",
        dataset_kinds=[DatasetCatalog.DATASET_KINDS.DATASET],
        data_formats=["text", "bpe"],
        content_type="text/plain",
        software_download_location="https://openaipublic.blob.core.windows.net/gpt-2/encodings/main/vocab.bpe",
        access=ArtefactCatalog.ACCESS.PRIVATE,
        license="none",
        properties={
            "code_ref": "https://github.com/jcpeterson/openwebtext",
            "n_vocab": 50257,
        },
    )
    errors = []
    isValid = vocabulary.validate(errors)
    assert isValid, f"Vocabulary validation failed with errors: {errors}"
    return vocabulary


# "> (?:[sdmt]|ll|ve|re)| ?\p{L}++| ?\p{N}++| ?[^\s\p{L}\p{N}]++|\s++$|\s+(?!\S)|\s"
def test_nanoGPT_tokenizer_code() -> SoftwareFile:
    tokenizer_code = SoftwareFile(
        name="GPT2TokenizerCode",
        # category=SoftwareCatalog.CATEGORIES.CODE,
        content_type="text/x-python",
        properties={
            "reference_implementation": "https://github.com/openai/tiktoken/blob/main/tiktoken_ext/openai_public.py",
            "pre_tokenization:": "to encode",
        },
    )
    errors = []
    isValid = tokenizer_code.validate(errors)
    assert isValid, f"Tokenizer code validation failed with errors: {errors}"
    return tokenizer_code


def test_nanoGPT_model_weights() -> SoftwareFile:
    model_weights = SoftwareFile(
        name="GPT2ModelWeights",
        category=ArtefactCatalog.CATEGORIES.MODEL_WEIGHTS,
        properties={
            "location": "https://openaipublic.blob.core.windows.net/gpt-2/models/124M/model.ckpt.data-00000-of-00001",
            "n_parameters": 124439808,
        },
    )
    errors = []
    isValid = model_weights.validate(errors)
    assert isValid, f"Model weights validation failed with errors: {errors}"
    return model_weights


def test_nanoGPT_training_config() -> SoftwareFile:
    training_config = SoftwareFile(
        name="GPT2TrainingConfig",
        category=ArtefactCatalog.CATEGORIES.CONFIG,
        properties={
            "description": "Training the GPT2 model using collected data",
            "optimizer": {
                "type": "adamw",
                "weight_decay": 0.1,
                "beta1": 0.9,
                "beta2": 0.95,
                "notes": "Weight decay is not applied to bias and layer norm layers",
            },
            "model_config": {
                "type": "decoder",
                "n_parameters": 124439808,
                "n_active_parameters": 124439808,
                "n_embedding_dimensions": 768,
                "n_transformers": 12,
                "positional_embedding": {"type": "learned", "n_positions": 1024},
                "transformer_attention": {
                    "type": "multi-head-attention",
                    "n_heads": 12,
                },
                "transformer_ffn": {
                    "hidden_layer_size": 3072,
                    "hidden_layer_size_ratio": 4.0,
                },
            },
        },
    )
    errors = []
    isValid = training_config.validate(errors)
    assert isValid, f"Training config validation failed with errors: {errors}"
    return training_config


# ---------------------------------------------------------------------------------
# ---------------------------- Pipeline building ----------------------------
# ---------------------------------------------------------------------------------


# Construction des étapes du pipeline
def test_nanoGPT_pipeline() -> Pipeline:
    pipeline = Pipeline("nanoGPT Pipeline")
    taskDataCollection = Task(
        name="DataCollection", description="Collecting the training data for GPT2 model"
    )
    pipeline.tasks.append(taskDataCollection)

    taskTokenizer = Task(
        name="Tokenizing",
        description="Tokenizing the training data using byte-level BPE tokenizer",
    )
    taskTokenizer.properties = {"family": "byte-bpe-tokenizer"}
    pipeline.tasks.append(taskTokenizer)

    taskPretraining = Task(
        name="PreTraining",
        description="Pre-training the GPT2 model using the tokenized data",
    )
    pipeline.tasks.append(taskPretraining)
    return pipeline


# --------------------------------------------------------------------------------
# ---------------------------- Relations building ----------------------------
# --------------------------------------------------------------------------------


def create_relations(manifest: Manifest) -> List[Relationship]:
    relations = []
    # We first retrieve the artefacts and tasks from the manifest to use them in the relations
    vocabulary = manifest.find_artefacts(name="vocabulary")[0]
    assert vocabulary is not None, "Artefact 'vocabulary' not found in the manifest"
    openWebText = manifest.find_artefacts(name="openWebText")[0]
    assert openWebText is not None, "Artefact 'openWebText' not found in the manifest"
    training_config = manifest.find_artefacts(name="GPT2TrainingConfig")[0]
    assert training_config is not None, (
        "Artefact 'GPT2TrainingConfig' not found in the manifest"
    )
    gpt_model = manifest.find_artefacts(name="nanoGPT Model")[0]
    assert gpt_model is not None, "Artefact 'nanoGPT Model' not found in the manifest"
    model_weights = manifest.find_artefacts(name="GPT2ModelWeights")[0]
    assert model_weights is not None, (
        "Artefact 'GPT2ModelWeights' not found in the manifest"
    )
    tokenizer_code = manifest.find_artefacts(name="GPT2TokenizerCode")[0]
    assert tokenizer_code is not None, (
        "Artefact 'GPT2TokenizerCode' not found in the manifest"
    )

    taskDataCollection = manifest.pipeline.find_task(name="DataCollection")[0]
    assert taskDataCollection is not None, (
        "Task 'DataCollection' not found in the pipeline"
    )
    taskTokenizer = manifest.pipeline.find_task(name="Tokenizing")[0]
    assert taskTokenizer is not None, "Task 'Tokenizing' not found in the pipeline"
    taskPretraining = manifest.pipeline.find_task(name="PreTraining")[0]
    assert taskPretraining is not None, "Task 'PreTraining' not found in the pipeline"




    #relations froms taskDataCollection
    relation_Task_to_step1= Relationship(
        from_=taskDataCollection,
        to_=[cripDM_Taxonomy.get_category("step:data-acquisition"),cripDM_Taxonomy],
        relationship_type=RelationshipType.ANNOTATED_BY
    )
    relations.append(relation_Task_to_step1)

    relation_DataCollection_to_Generates = Relationship(
        from_=taskDataCollection,
        to_=[openWebText],
        relationship_type=RelationshipType.PRODUCES,
    )
    relations.append(relation_DataCollection_to_Generates)
    relation_DataCollection_to_NEXT = Relationship(
        from_=taskDataCollection,
        to_=[taskTokenizer],
        relationship_type=RelationshipType.NEXT,
    )
    relations.append(relation_DataCollection_to_NEXT)


    #relations from taskTokenizer
    #relations to steps
    relation_Task_to_step2= Relationship(
        from_=taskTokenizer,
        to_=[cripDM_Taxonomy.get_category("step:other"),cripDM_Taxonomy],
        relationship_type=RelationshipType.ANNOTATED_BY
    )
    relations.append(relation_Task_to_step2)

    relation_Tokenizer_to_Generates = Relationship(
        from_=taskTokenizer,
        to_=[vocabulary],
        relationship_type=RelationshipType.PRODUCES,
    )
    relations.append(relation_Tokenizer_to_Generates)

    relation_Tokenizer_to_USES = Relationship(
        from_=taskTokenizer,
        to_=[tokenizer_code, openWebText],
        relationship_type=RelationshipType.USES,
    )
    relations.append(relation_Tokenizer_to_USES)

    relation_Tokenizer_to_NEXT = Relationship(
        from_=taskTokenizer,
        to_=[taskPretraining],
        relationship_type=RelationshipType.NEXT,
    )
    relations.append(relation_Tokenizer_to_NEXT)

    relation_PreTraining_to_Generates = Relationship(
        from_=taskPretraining,
        to_=[gpt_model, model_weights],
        relationship_type=RelationshipType.PRODUCES,
    )
    relations.append(relation_PreTraining_to_Generates)

    relation_PreTraining_to_USES = Relationship(
        from_=taskPretraining,
        to_=[vocabulary, openWebText, training_config],
        relationship_type=RelationshipType.USES,
    )
    relations.append(relation_PreTraining_to_USES)

    return relations


# --------------------------------------------------------------------------------
# ---------------------------- YAML Serialization and Deserialization ----------------------------
# --------------------------------------------------------------------------------


# ----------------- Tests for artefacts -----------------
def test_artefact_yaml_serialization_deserialisation():
    artefact = test_nanoGPT_MLModel()
    evaluate_artefact_yaml_serialization_deserialisation(artefact)
    evaluate_artefact_yaml_serialization_deserialisation(test_nanoGPT_openWebText())
    evaluate_artefact_yaml_serialization_deserialisation(test_nanoGPT_vocabulary())
    evaluate_artefact_yaml_serialization_deserialisation(test_nanoGPT_tokenizer_code())
    evaluate_artefact_yaml_serialization_deserialisation(test_nanoGPT_model_weights())
    evaluate_artefact_yaml_serialization_deserialisation(test_nanoGPT_training_config())


def evaluate_artefact_yaml_serialization_deserialisation(artefact: Artefact):
    output = YAMLSerializer.to_yaml(artefact)
    fileName = artefact.name.replace(" ", "_") + ".yaml"
    save_in_file("./targets/artefacts", fileName, output)

    loaded_element: dict = YAMLSerializer.load_yaml_to_dict(output)
    assert loaded_element is not None, "YAML loading to dict returned None"
    assert isinstance(loaded_element, dict), (
        f"Expected loaded element to be a dict, got {type(loaded_element)}"
    )

    object = YAMLSerializer._from_yaml(Task, loaded_element)
    assert object is not None, "Deserialization returned None"
    type = artefact.__class__
    assert isinstance(object, type), (
        f"Deserialized object is not of {type} but of type {object.__class__}"
    )
    assert object.name == artefact.name, (
        f"Expected name '{artefact.name}', got '{object.name}'"
    )
    assert object.properties == artefact.properties, (
        f"Expected properties '{artefact.properties}', got '{object.properties}'"
    )
    print(
        f"YAML serialization and deserialization test for {fileName} passed successfully!"
    )


def test_pipeline_yaml_serialization_deserialisation():
    pipeline = test_nanoGPT_pipeline()
    output = YAMLSerializer.to_yaml(pipeline)
    save_in_file("./targets/pipelines", "nanoGPT_pipeline.yaml", output)

    loaded_element: dict = YAMLSerializer.load_yaml_to_dict(output)
    assert loaded_element is not None, "YAML loading to dict returned None"
    assert isinstance(loaded_element, dict), (
        f"Expected loaded element to be a dict, got {type(loaded_element)}"
    )

    pipelineBis = YAMLSerializer._from_yaml(Task, loaded_element)

    assert pipelineBis is not None, "Deserialization returned None"
    assert pipelineBis.tasks is not None, "Deserialized pipeline has no tasks"
    assert len(pipelineBis.tasks) == 3, (
        f"Expected 3 tasks in the pipeline, found {len(pipelineBis.tasks)}"
    )
    print(
        "YAML serialization and deserialization test for pipeline passed successfully!"
    )


def test_to_yaml_and_reverse_nanoGPT():
    manifest = test_nanoGPT_manifest()
    output = YAMLSerializer.to_yaml(manifest)
    save_in_file("./targets/manifests", "nanoGPT_manifest.yaml", output)

    loaded_element: dict = YAMLSerializer.load_yaml_to_dict(output)
    assert loaded_element is not None, "YAML loading to dict returned None"
    assert isinstance(loaded_element, dict), (
        f"Expected loaded element to be a dict, got {type(loaded_element)}"
    )

    manifestBis = YAMLSerializer._from_yaml(Task, loaded_element)
    assert manifestBis is not None, "Deserialization returned None"
    assert manifestBis.pipeline is not None, "Deserialized manifest has no pipeline"
    assert len(manifestBis.pipeline.tasks) == 3, (
        f"Expected 3 tasks in the pipeline, found {len(manifestBis.pipeline.tasks)}"
    )
    assert len(manifestBis.artefacts) == 6, (
        f"Expected 6 artefacts, found {len(manifestBis.artefacts)}"
    )
    assert len(manifestBis.relations) == 9, (
        f"Expected 9 relations, found {len(manifestBis.relations)}"
    )

    annotated_relations = [
        relation
        for relation in manifestBis.relations
        if relation.relationship_type == RelationshipType.ANNOTATED_BY
    ]
    assert len(annotated_relations) == 2, (
        f"Expected 2 annotated_by relations, found {len(annotated_relations)}"
    )
    assert annotated_relations[0].to_[0].uid == "step:data-acquisition", (
        f"Expected first annotated_by relation to target 'step:data-acquisition', found '{annotated_relations[0].to_[0].uid}'"
    )
    print("YAML serialization and deserialization test passed successfully!")


def test_to_mermaid_nanoGPT():
    manifest = test_nanoGPT_manifest()
    serializer = MERMAIDSerializer()
    mermaid_output = serializer.object_to_mermaid_full(manifest)
    save_in_file("./targets/diagrams", "nanoGPT_manifest.mmd", mermaid_output)
    print("Mermaid diagram generation test passed successfully!")


# @todo : tout revoir
# print(save_yaml(builder))

# Export en Mermaid
# print("--- Génération du diagramme Mermaid ---")
# mermaid_output = to_mermaid(builder)
# print("--- Génération du diagramme Mermaid ---")
# save_in_file("../targets/diagrams", "gpt2.mmd", mermaid_output)
