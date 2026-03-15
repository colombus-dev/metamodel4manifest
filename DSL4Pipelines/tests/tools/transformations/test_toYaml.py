from DSL4Pipelines.src.metamodel.artefacts.artefacts import Artefact, SoftwareFile
from DSL4Pipelines.src.metamodel.artefacts.metrics import Metric
from DSL4Pipelines.src.metamodel.catalogs.MetricCatalog import MetricCatalog
from DSL4Pipelines.src.metamodel.catalogs.vocabulary import FileKind
from DSL4Pipelines.src.metamodel.core.structure import Element, CreationInfo
from DSL4Pipelines.src.metamodel.manifests.manifests import Manifest
from DSL4Pipelines.src.metamodel.pipelines.workflow import (
    Pipeline,
    Step,
    Instruction,
    Task,
)
from DSL4Pipelines.src.tools.transformations.YAMLSerializer import YAMLSerializer
from DSL4Pipelines.tests.examples.NotebookIRISManifest import (
    test_build_pipeline,
    test_build_manifestFromNBonIrisClassification,
)
from DSL4Pipelines.src.metamodel.relations.relations import Relationship
from DSL4Pipelines.src.metamodel.catalogs.vocabulary import RelationshipType
from DSL4Pipelines.src.metamodel.taxonomies.taxonomy import cripDM_Taxonomy, Taxonomy
from DSL4Pipelines.src.metamodel.taxonomies.taxonomy import Category


# --------- TESTS FOR YAMLSerializer.py : from an Objet to Yaml ---------
def test_toYaml_Simple_Element() -> str:
    e = Element(name="TestElement", type="Element")
    yaml_output = YAMLSerializer.to_yaml(e, False)
    print(f"YAML Output:\n{yaml_output} : {type(yaml_output)}")
    assert isinstance(yaml_output, str)
    assert "name: TestElement" in yaml_output
    # assert "description: null" in yaml_output (automatically removed by YAML serializer when value is None)
    assert "type: Element" in yaml_output

    e.description = "A test element"
    yaml_output = YAMLSerializer.to_yaml(e, False)
    print(f"YAML Output with description:\n{yaml_output}")
    assert "description: A test element" in yaml_output

    yaml_output = YAMLSerializer.to_yaml(e, True)
    print(f"YAML Output with type:\n{yaml_output}")
    assert isinstance(yaml_output, str)
    assert "name: TestElement" in yaml_output
    assert "description: null" not in yaml_output
    assert "type: Element" in yaml_output
    return yaml_output


def test_toYaml_Simple_Element_with_properties() -> str:
    e = Element(
        name="TestElement",
        type="TestType",
        description="A test element",
        properties={"key1": "value1", "key2": "value2"},
    )
    yaml_output = YAMLSerializer.to_yaml(e, False)
    print(f"YAML Output:\n{yaml_output} : {type(yaml_output)}")
    assert isinstance(yaml_output, str)
    assert "properties:" in yaml_output
    assert "key1: value1" in yaml_output
    assert "key2: value2" in yaml_output
    yaml_output = YAMLSerializer.to_yaml(e, True)
    print(f"YAML Output:\n{yaml_output} : {type(yaml_output)}")
    assert "properties:" in yaml_output
    return yaml_output


def test_toYaml_Element_with_creationInfo() -> str:
    creationInfo = CreationInfo(
        uid="creationinfo-123", created_by=["mi"], spec_version="1.0"
    )
    e = Element(name="TestElement", type="Element", creation_info=creationInfo)
    yaml_output = YAMLSerializer.to_yaml(e, False)
    print(f"YAML Output:\n{yaml_output} : {type(yaml_output)}")
    assert isinstance(yaml_output, str)
    assert "uid: creationinfo-123" in yaml_output
    assert "spec_version: '1.0'" in yaml_output
    return yaml_output


def test_toYaml_Artefact() -> str:
    a = Artefact(name="TestArtefact", description="A test artefact")
    yaml_output = YAMLSerializer.to_yaml(a, False)
    print(f"YAML Output:\n{yaml_output} : {type(yaml_output)}")
    assert isinstance(yaml_output, str)
    assert "name: TestArtefact" in yaml_output
    assert "description: A test artefact" in yaml_output
    assert "type: Artefact" in yaml_output
    return yaml_output


def test_toYaml_SoftwareFile_with_properties() -> str:
    a = SoftwareFile(
        name="TestSoftwareFile",
        description="A test software file",
        properties={"key1": "value1", "key2": "value2"},
        software_file_kind=FileKind.FILE,
    )
    yaml_output = YAMLSerializer.to_yaml(a, False)
    print(f"YAML Output:\n{yaml_output} : {type(yaml_output)}")
    assert isinstance(yaml_output, str)
    assert "name: TestSoftwareFile" in yaml_output
    assert "description: A test software file" in yaml_output
    assert "type: SoftwareFile" in yaml_output
    assert "properties:" in yaml_output
    assert "key1: value1" in yaml_output
    assert "key2: value2" in yaml_output
    assert "software_file_kind: file" in yaml_output
    return yaml_output


def test_toYaml_Metrics() -> str:
    a = Metric(
        name="TestMetric",
        description="A test metric",
        properties={"key1": "value1", "key2": "value2"},
    )
    a.kind = MetricCatalog.FAIRNESS.EQUALIZED_ODDS
    yaml_output = YAMLSerializer.to_yaml(a, False)
    print(f"YAML Output:\n{yaml_output} : {type(yaml_output)}")
    assert isinstance(yaml_output, str)
    assert "name: TestMetric" in yaml_output
    assert "description: A test metric" in yaml_output
    assert "type: Metric" in yaml_output
    assert "properties:" in yaml_output
    assert "key1: value1" in yaml_output
    assert "key2: value2" in yaml_output
    assert "kind: fair:equalized_odds" in yaml_output
    return yaml_output


def test_toYaml_Pipeline() -> str:
    pipeline = test_build_pipeline()
    yaml_output = YAMLSerializer.to_yaml(pipeline, True)
    print(f"YAML Output:\n{yaml_output} : {type(yaml_output)}")
    assert isinstance(yaml_output, str)
    assert "name: Iris Analysis Pipeline" in yaml_output
    assert "type: Pipeline" in yaml_output
    return yaml_output


def test_toYaml_Element_with_relationships() -> str:
    a = Artefact(
        name="Benchmark Dataset", description="A dataset used for benchmarking"
    )
    m = Metric(
        name="TestMetric",
        description="A test metric",
        properties={"key1": "value1", "key2": "value2"},
    )
    m.kind = MetricCatalog.FAIRNESS.EQUALIZED_ODDS

    r = Relationship(from_=a, to_=[m], relationship_type=RelationshipType.PRODUCES)
    manifest = Manifest(
        name="Test Manifest", pipeline=None, artefacts=[a, m], relations=[r]
    )

    yaml_output = YAMLSerializer.to_yaml(manifest, True)
    print(f"YAML Output:\n{yaml_output} : {type(yaml_output)}")
    assert isinstance(yaml_output, str)
    assert "name: Benchmark Dataset" in yaml_output
    assert "type: Artefact" in yaml_output
    assert "relations:" in yaml_output
    assert "relationship_type: produces" in yaml_output
    assert "from_: " + a.uid in yaml_output
    assert "- " + m.uid in yaml_output
    return yaml_output


def test_toYaml_Manifest() -> str:
    manifest = test_build_manifestFromNBonIrisClassification()
    assert manifest is not None
    assert isinstance(manifest, Manifest)
    assert manifest.type == "Manifest"
    yaml_output = YAMLSerializer.to_yaml(manifest, True)
    # print(f"YAML Output:\n{yaml_output} : {type(yaml_output)}")
    assert isinstance(yaml_output, str)
    assert "name: Iris Analysis Pipeline" in yaml_output
    assert "type: Manifest" in yaml_output
    return yaml_output

def test_toYaml_relation_to_taxonomy() -> str:
    task1:Task = Task()
    cat = cripDM_Taxonomy.get_category("step:data-preparation")
    assert cat is not None, "The category 'step:data-preparation' should be present in the taxonomy."
    relation : Relationship = Relationship(
        from_=task1,
        to_=[
            cat,
            cripDM_Taxonomy],
        relationship_type=RelationshipType.ANNOTATED_BY)
    yaml_output = YAMLSerializer.to_yaml(relation, True)
    print(f"\n YAML Output:\n{yaml_output} : {type(yaml_output)}")
    assert isinstance(yaml_output, str)
    assert "relationship_type: annotatedBy" in yaml_output
    assert "uid: " + task1.uid in yaml_output
    assert "- uid: " + cat.uid in yaml_output
    assert "- uid: " + cripDM_Taxonomy.uid in yaml_output
    return yaml_output


# ------------------- test load_yaml -------------------
def test_load_yaml_on_simpleElement():
    res = test_toYaml_Simple_Element()
    # res = test_toYaml_Simple_Element_with_properties()
    print(f"--------------- YAML String to Load:\n{res}\n: {type(res)}")
    loaded_element: dict = YAMLSerializer.load_yaml_to_dict(res)
    print(f"Loaded Element:\n{loaded_element})\n: {type(loaded_element)}")
    assert isinstance(loaded_element, dict)

    elem = YAMLSerializer._from_yaml(Element, loaded_element)
    print(f"Reconstructed Element:\n{elem}\n: {type(elem)}")

    assert isinstance(elem, Element)
    assert elem.name == "TestElement"
    assert elem.type == "Element"


def test_load_yaml_on_Element_with_properties():
    res = test_toYaml_Simple_Element_with_properties()
    print(f"-------------------- YAML String to Load:\n{res}\n: {type(res)}")

    loaded_element: dict = YAMLSerializer.load_yaml_to_dict(res)
    print(
        f"-------------------- Loaded Element:\n{loaded_element})\n: {type(loaded_element)}"
    )
    assert isinstance(loaded_element, dict)

    elem = YAMLSerializer._from_yaml(Element, loaded_element)
    print(f"Reconstructed Element:\n{elem}\n: {type(elem)}")
    assert isinstance(elem, Element)
    assert elem.properties is not None
    assert elem.properties.get("key1") == "value1"
    assert elem.properties.get("key2") == "value2"


def test_load_yaml_on_Element_with_properties_Creation():
    res = test_toYaml_Element_with_creationInfo()
    print(f"-------------------- YAML String to Load:\n{res}\n: {type(res)}")

    loaded_element: dict = YAMLSerializer.load_yaml_to_dict(res)
    print(
        f"-------------------- Loaded Element:\n{loaded_element})\n: {type(loaded_element)}"
    )
    assert isinstance(loaded_element, dict)

    elem = YAMLSerializer._from_yaml(Element, loaded_element)
    print(f"Reconstructed Element:\n{elem}\n: {type(elem)}")
    assert isinstance(elem, Element)
    assert elem.properties is not None
    assert elem.creation_info is not None
    assert elem.creation_info.uid == "creationinfo-123"
    assert elem.creation_info.created_by == ["mi"]
    assert elem.creation_info.spec_version == "1.0"
    creationInfo = CreationInfo(
        uid="creationinfo-123", created_by=["mi"], spec_version="1.0"
    )
    e = Element(name="TestElement", creation_info=creationInfo)
    e.uid = elem.uid

    assert elem == e


def test_load_yaml_on_Metric():
    res = test_toYaml_Metrics()
    print(f"-------------------- YAML String to Load:\n{res}\n: {type(res)}")

    loaded_element: dict = YAMLSerializer.load_yaml_to_dict(res)
    print(
        f"-------------------- Loaded Element:\n{loaded_element})\n: {type(loaded_element)}"
    )
    assert isinstance(loaded_element, dict)

    elem = YAMLSerializer._from_yaml(Element, loaded_element)
    print(f"Reconstructed Element:\n{elem}\n: {type(elem)}")
    assert isinstance(elem, Metric)


def test_load_yaml_on_Pipeline():
    res = test_toYaml_Pipeline()
    print(f"-------------------- YAML String to Load:\n{res}\n: {type(res)}")

    loaded_element: dict = YAMLSerializer.load_yaml_to_dict(res)
    print(
        f"-------------------- Loaded Element:\n{loaded_element})\n: {type(loaded_element)}"
    )
    assert isinstance(loaded_element, dict)

    elem = YAMLSerializer._from_yaml(Element, loaded_element)
    print(f"Reconstructed Element:\n{elem}\n: {type(elem)}")
    assert isinstance(elem, Pipeline)
    eval_pipeline_structure(elem)
    yamlPipeline = YAMLSerializer.to_yaml(elem)
    print(f"Reconstructed Pipeline to YAML:\n{yamlPipeline}\n: {type(yamlPipeline)}")
    assert isinstance(yamlPipeline, str)
    assert "name: Iris Analysis Pipeline" in yamlPipeline
    assert "type: Pipeline" in yamlPipeline


def test_load_yaml_on_Element_with_relationships():
    res = test_toYaml_Element_with_relationships()
    print(f"-------------------- YAML String to Load:\n{res}\n: {type(res)}")

    loaded_element: dict = YAMLSerializer.load_yaml_to_dict(res)
    print(
        f"-------------------- Loaded Element:\n{loaded_element})\n: {type(loaded_element)}"
    )
    assert isinstance(loaded_element, dict)

    manifest = YAMLSerializer._from_yaml(Manifest, loaded_element)
    # manifest = YAMLSerializer._from_yaml(Element, loaded_element)
    print(f"Reconstructed Element:\n{manifest}\n: {type(manifest)}")
    assert isinstance(manifest, Manifest)
    assert manifest.relations is not None
    assert len(manifest.relations) == 1
    r = manifest.relations[0]
    assert r.relationship_type == "produces"
    assert manifest.artefacts is not None
    assert len(manifest.artefacts) == 2
    # look for the artefac with name "TestMetric"
    metric_artefact = next(
        (a for a in manifest.artefacts if a.name == "TestMetric"), None
    )
    assert metric_artefact is not None
    assert isinstance(metric_artefact, Metric)
    artefact = next(
        (a for a in manifest.artefacts if a.name == "Benchmark Dataset"), None
    )
    assert artefact is not None
    assert isinstance(artefact, Artefact)

    assert r.from_ is not None
    assert r.to_ is not None
    assert len(r.to_) == 1
    assert r.from_ == artefact
    assert r.to_[0] == metric_artefact

def test_load_yaml_on_Element_with_relationships_to_taxonomy():
    res = test_toYaml_relation_to_taxonomy()
    print(f"-------------------- YAML String to Load:\n{res}\n: {type(res)}")

    loaded_element: dict = YAMLSerializer.load_yaml_to_dict(res)
    print(
        f"-------------------- Loaded Element:\n{loaded_element})\n: {type(loaded_element)}"
    )
    assert isinstance(loaded_element, dict)

    relation = YAMLSerializer._from_yaml(Relationship, loaded_element)
    print(f"Reconstructed Element:\n{relation}\n: {type(relation)}")
    assert isinstance(relation, Relationship)
    assert relation.relationship_type == "annotatedBy"
    assert relation.from_ is not None
    assert relation.to_ is not None
    assert len(relation.to_) == 2
    to_cat = relation.to_
    print (f"\n ---------- Targets of the relationship:\n{to_cat}\n: {type(to_cat)}")
    cat = next((t for t in relation.to_ if isinstance(t, Category) ), None)
    assert cat is not None, "The category 'Data Preparation' should be present in the relationship's targets."
    assert cat.uid == "step:data-preparation", f"The category's UID should be 'step:data-preparation', but got '{cat.uid}'"
    taxonomy = next((t for t in relation.to_ if isinstance(t, Taxonomy)), None)
    assert taxonomy is not None, "The taxonomy 'CRISP-DM Taxonomy' should be present in the relationship's targets."
    assert taxonomy.uid == "taxo:ml-lifecycle", f"The taxonomy's UID should be 'taxonomy:crispdm', but got '{taxonomy.uid}'"



def test_load_yaml_on_Manifest():
    res = test_toYaml_Manifest()
    print(f"-------------------- YAML String to Load:\n{res}\n: {type(res)}")

    loaded_element: dict = YAMLSerializer.load_yaml_to_dict(res)
    print(
        f"-------------------- Loaded Element:\n{loaded_element})\n: {type(loaded_element)}"
    )
    assert isinstance(loaded_element, dict)

    elem = YAMLSerializer._from_yaml(Element, loaded_element)
    print(f"Reconstructed Element:\n{elem}\n: {type(elem)}")
    assert isinstance(elem, Manifest)



# -------------------- test from_yaml_file --------------------
def test_from_yaml_file_on_Manifest():
    manifest = YAMLSerializer.from_yaml_file(
        "/Users/mireillefornarino/GIT/RECHERCHES/DescribeLLM/untitled/DSL4Pipelines/tests/examples/sources/nanoGPT_manifest.yaml",
        Manifest,
    )
    assert manifest is not None
    assert isinstance(manifest, Manifest)

    assert manifest.name == "NanoGPT Manifest"
    assert manifest.type == "Manifest"
    assert manifest.pipeline is not None
    assert isinstance(manifest.pipeline, Pipeline)
    assert manifest.pipeline.name == "NanoGPT Pipeline"
    assert manifest.pipeline.type == "Pipeline"
    eval_pipeline_structure(manifest.pipeline)
    eval_artefact_structure(manifest.artefacts)
    eval_relationships_structure(manifest.relations)


## -------------------- Helper functions for structure evaluation --------------------
def eval_pipeline_structure(elem: Pipeline):
    tasks = elem.tasks
    for t in tasks:
        print(f"Task: {t.name}, type: {t.type}")
        assert isinstance(t, Element)
        for s in t.steps:
            print(f"Step: {s.name}, type: {s.type}")
            assert s.type == "Step"
            assert isinstance(s, Step)
            for i in s.commands:
                print(f"Command: {i.name}, type: {i.type}")
                assert isinstance(i, Instruction)


def eval_artefact_structure(artefacts: list[Artefact]):
    for a in artefacts:
        print(f"Artefact: {a.name}, type: {a.type}")
        assert isinstance(a, Artefact)
        if isinstance(a, SoftwareFile):
            assert a.software_file_kind is not None


def eval_relationships_structure(relationships: list[Relationship]):
    for r in relationships:
        print(f"{r.__class__} : Relationship: {r} ")
        print(f"{r.__class__ == Relationship} : is instance of Relationship ?")
        print(f"true ? {r == Relationship} : is r == Relationship ?")
        assert isinstance(r, Relationship)
