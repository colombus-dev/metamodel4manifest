# --- Construction de l'Instance ---
from DSL4Pipelines.src.metamodel.artefacts.ml_artefacts import Data, MLModel
from DSL4Pipelines.src.metamodel.artefacts.artefacts import SoftwareFile
from DSL4Pipelines.src.metamodel.catalogs.DatasetCatalog import DatasetCatalog
from DSL4Pipelines.src.metamodel.catalogs.MetricCatalog import MetricCatalog
from DSL4Pipelines.src.metamodel.core.structure import (
    ExternalReference,
    CreationInfo,
    Element,
)
from DSL4Pipelines.src.metamodel.artefacts.metrics import Metric
from DSL4Pipelines.src.metamodel.manifests.manifests import Manifest
from DSL4Pipelines.src.metamodel.pipelines.workflow import (
    Pipeline,
    Task,
    Instruction,
    Step,
)
from DSL4Pipelines.src.metamodel.relations.relations import Relationship
from DSL4Pipelines.src.metamodel.catalogs.vocabulary import RelationshipType, FileKind
from DSL4Pipelines.src.tools.toFile import save_in_file
from DSL4Pipelines.src.tools.transformations.YAMLSerializer import YAMLSerializer
from DSL4Pipelines.src.tools.transformations.toMermaid import MERMAIDSerializer


def test_build_manifestFromNBonIrisClassification() -> Manifest:
    # 1. Racine
    manifest = Manifest("Classification on IRIS")
    manifest.description = " classification ..."
    manifest.name = "Iris Analysis Pipeline Manifest"
    manifest.artefacts = test_build_artefacts()
    manifest.pipeline = test_build_pipeline()
    manifest.relations = build_relations(manifest)
    return manifest


def test_build_pipeline() -> Pipeline:
    pipeline = Pipeline(uid="IRIS Pipeline", name="Iris Analysis Pipeline")
    task_lib = test_task_load_libraries()
    assert task_lib.name == "LibraryLoading"
    pipeline.tasks.append(task_lib)
    pipeline.tasks.append(test_task_data_loading())
    task_prep = test_task_data_preprocessing()
    assert task_prep.name == "DataPreparation"
    pipeline.tasks.append(task_prep)
    task_train = test_task_model_training()
    assert task_train.name == "ModelTraining"
    pipeline.tasks.append(task_train)
    task_eval = test_task_model_evaluation()
    assert task_eval.name == "ModelEvaluation"
    pipeline.tasks.append(task_eval)
    return pipeline


def test_build_artefacts() -> list:
    artefacts = []
    notebook = test_build_artefact_notebook()
    artefacts.append(notebook)
    artefacts.append(test_build_artefact_iris_dataset())
    artefacts.append(test_build_artefact_viz())
    artefacts.append(test_build_artefact_model())
    #    artefacts.append(test_build_artefact_confusion_matrix())
    artefacts.append(test_build_artefact_evaluation_visualization())
    artefacts.append(test_build_artefact_metric_accuracy())
    artefacts.append(test_build_artefact_metric_confusion_matrix())
    artefacts.append(test_build_artefact_visualisation_confusion_matrix())

    return artefacts


def build_relations(manifest) -> list:
    relations = []
    # We will create the relations after creating the pipeline and the artefacts, because we need to link them together.
    relations.append(
        create_relation_manifest_notebook(
            manifest, manifest.find_artefacts(name="notebook")
        )
    )
    relations.append(
        create_relation_stepLoad_irisDataset(
            manifest.pipeline.find_task(name="DataLoading")[0].steps[0],
            manifest.find_artefacts(type="Data", name="Iris Flower Dataset"),
        )
    )
    relations.append(
        create_relation_stepViz_visualisation(
            manifest.pipeline.find_task(name="DataLoading")[0].steps[1],
            manifest.find_artefacts(type="SoftwareFile", name="Data Visualization"),
        )
    )
    relation_task_to_model = Relationship(
        from_=manifest.pipeline.find_task(name="ModelTraining")[0],
        to_=manifest.find_artefacts(type="MLModel", name="Trained Decision Tree Model"),
        relationship_type=RelationshipType.GENERATES,
    )
    relations.append(relation_task_to_model)
    relation_step_to_visualisation = Relationship(
        from_=manifest.pipeline.find_task(name="ModelEvaluation")[0].find_steps(
            name="Visualize"
        )[0],
        to_=manifest.find_artefacts(name="Evaluation Visualization"),
        relationship_type=RelationshipType.GENERATES,
    )
    relations.append(relation_step_to_visualisation)

    step_model_evaluation = manifest.pipeline.find_task(name="ModelEvaluation")[
        0
    ].find_steps(name="Model Evaluation")[0]
    # print(f"METRICS IN MANIFEST: {manifest.find_artefacts(type='Metric')}")
    confusion_matrix_metric = manifest.find_artefacts(
        type="Metric", name="Confusion Matrix"
    )[0]
    accuracy_metric = manifest.find_artefacts(type="Metric", name="Model Accuracy")[0]
    relation_step_to_metrics = Relationship(
        from_=step_model_evaluation,
        to_=[accuracy_metric, confusion_matrix_metric],
        relationship_type=RelationshipType.EVALUATES,
    )
    relations.append(relation_step_to_metrics)

    #  relation_step_to_confusionMatrix = \
    #      Relationship(
    #          from_=step_model_evaluation,
    #          to_=confusion_matrix_metric,
    #          relationshipType=RelationshipType.EVALUATES)
    #  relations.append(relation_step_to_confusionMatrix)
    return relations


# ----------------------------- Pipeline and Tasks ---------------------------
def test_task_load_libraries() -> Task:
    task_lib = Task(name="LibraryLoading")

    step_libs = Step(name="Import Libraries")
    task_lib.steps.append(step_libs)
    step_libs.commands.append(Instruction(code="import numpy as np"))
    step_libs.commands.append(Instruction(code="import matplotlib.pyplot as plt"))
    step_libs.commands.append(Instruction(code="import seaborn as sns"))
    step_libs.commands.append(
        Instruction(code="from sklearn.model_selection import train_test_split")
    )
    step_libs.commands.append(
        Instruction(code="from sklearn.tree import DecisionTreeClassifier")
    )
    step_libs.commands.append(
        Instruction(
            code="from sklearn.metrics import accuracy_score, classification_report, confusion_matrix"
        )
    )
    step_libs.commands.append(
        Instruction(code=":from sklearn.datasets import load_iris")
    )
    return task_lib


def test_task_data_loading() -> Task:
    task_data = Task(name="DataLoading")
    step_load = Step(name="Load Dataset")
    task_data.steps.append(step_load)

    step_load.commands.append(Instruction(code="iris = load_iris()"))
    step_load.commands.append(
        Instruction(code="df = pd.DataFrame(data=np.c_[iris['data'], iris['target']]")
    )
    step_load.commands.append(Instruction(code="print(df.head())"))
    step_viz = Step("Visualization")
    task_data.steps.append(step_viz)
    step_viz.commands.append(Instruction(code="sns.pairplot(df, hue='species')"))
    step_viz.commands.append(Instruction(code="plt.show()"))
    step_viz.commands.append(Instruction(code="plt.figure(figsize=(8, 6))"))
    step_viz.commands.append(
        Instruction(
            code="sns.histplot(data=df, x='petal_length', hue='species', multiple='stack')"
        )
    )
    step_viz.commands.append(
        Instruction(code="plt.title('Distribution de la longueur des pétales')")
    )
    step_viz.commands.append(Instruction(code="plt.show()"))
    return task_data


# Data Preprocessing
def test_task_data_preprocessing() -> Task:
    task_preparation = Task(name="DataPreparation")
    step_prepare = Step(name="DataPreparation")
    task_preparation.steps.append(step_prepare)
    step_prepare.commands.append(Instruction(code="X = df.drop('species', axis=1)"))
    return task_preparation


# Model Training
def test_task_model_training() -> Task:
    task_train = Task(name="ModelTraining")
    step_model = Step(name="Model Training")
    task_train.steps.append(step_model)
    step_model.commands.append(
        Instruction(code="model = DecisionTreeClassifier(random_state=42)")
    )

    step_train = Step(name="Fit Model")
    task_train.steps.append(step_train)
    step_train.commands.append(Instruction(code="model.fit(X_train, y_train);"))
    return task_train


# Evaluation
def test_task_model_evaluation() -> Task:
    task_eval = Task(name="ModelEvaluation")

    step_eval = Step(name="Model Evaluation")
    task_eval.steps.append(step_eval)
    step_eval.commands.append(Instruction(code="predictions = model.predict(X_test)"))
    step_eval.commands.append(
        Instruction(code="accuracy = accuracy_score(y_test, predictions)")
    )
    step_eval.commands.append(
        Instruction(code="print(f'Accuracy du modèle : {accuracy:.2f}')")
    )
    step_eval.commands.append(
        Instruction(code="print('\nRapport de classification :')")
    )
    step_eval.commands.append(
        Instruction(code="print(classification_report(y_test, predictions))")
    )
    step_eval.commands.append(
        Instruction(code="cm = confusion_matrix(y_test, predictions)")
    )

    step_viz_cm = Step(name="Visualize")
    task_eval.steps.append(step_viz_cm)
    step_viz_cm.commands.append(Instruction(code="plt.figure(figsize=(8, 6))"))
    step_viz_cm.commands.append(Instruction(code="plt.figure(figsize=(8, 6))"))
    step_viz_cm.commands.append(Instruction(code="plt.xlabel('Prédiction')"))
    step_viz_cm.commands.append(Instruction(code="plt.ylabel('Valeur réelle')"))
    step_viz_cm.commands.append(Instruction(code="plt.title('Matrice de Confusion')"))
    step_viz_cm.commands.append(Instruction(code="plt.show()"))
    return task_eval


# ---------------------------- ARTEFACTS ---------------------------


def test_build_artefact_notebook() -> SoftwareFile:
    notebook = SoftwareFile(
        external_reference=ExternalReference(
            external_identifier_type="url", identifier="nbpath"
        )
    )
    notebook.name = "notebook"
    notebook.languages = ["english", "french", "python"]
    notebook.content_type = "text/x-ipynb+json"
    errors = []
    if not notebook.validate(errors):
        print(f"Error validating notebook artefact: {errors}")
    return notebook


# Dataset IRIS
def test_build_artefact_iris_dataset() -> Data:
    iris_dataset = Data(
        name="Iris Flower Dataset",
        description="Dataset classique de Fisher contenant 150 instances de 3 espèces d'iris (Setosa, Versicolor, Virginica).",
        creation_info=CreationInfo(created_by=["R.A. Fisher"], created_on="1936-01-01"),
        software_file_kind=FileKind.FILE,
        software_primary_purpose="Classification and Pattern Recognition",
        content_type="text/csv",
        software_download_location="https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data",
        external_reference=ExternalReference(
            identifier="https://doi.org/10.24432/C56P4B"
        ),
        # --- Attributs spécifiques à Data ---
        languages=["English"],
        data_types=["tabular"],  # Données structurées en colonnes
        dataset_kinds=[
            DatasetCatalog.DATASET_KINDS.DATASET
        ],  # C'est un jeu de données, pas un corpus textuel
        dataset_size=4550,  # Environ 4.5 KB
        dataset_availability="public",
        dataset_has_sensitive_personal_information="no",  # Ce sont des mesures de fleurs !
        dataset_intended_use="Training and evaluation of classification models.",
        dataset_known_bias=["Class balanced 50 samples per class"],
        properties={
            "num_instances": 150,
            "num_features": 4,
            "num_classes": 3,
            "feature_names": [
                "sepal length",
                "sepal width",
                "petal length",
                "petal width",
            ],
            "class_names": ["setosa", "versicolor", "virginica"],
        },
    )
    errors = []
    if not iris_dataset.validate(errors):
        print(f"Error validating iris dataset artefact: {errors}")
    return iris_dataset


def test_build_artefact_viz() -> SoftwareFile:
    viz_file = SoftwareFile(
        name="Data Visualization",
        description="Visualizations generated during data loading, including pairplot and histogram.",
        content_type="image/png",
        properties={
            "Content Preview": "Pairplot and histogram visualizations of the IRIS dataset"
        },
    )
    errors = []
    if not viz_file.validate(errors):
        print(f"Error validating visualization artefact: {errors}")
    return viz_file


def test_build_artefact_model() -> MLModel:
    model = MLModel(
        name="Trained Decision Tree Model",
        description="Un modèle de classification entraîné sur le dataset IRIS.",
        creation_info=CreationInfo(
            created_by="Data Scientist", created_on="2024-06-24T10:00:00Z"
        ),
        software_file_kind=FileKind.FILE,
        software_primary_purpose="Classification",
        content_type="application/octet-stream",
        software_download_location="https://example.com/downloads/iris_decision_tree_model.bin",
        external_reference=ExternalReference(
            identifier="https://doi.org/10.1234/iris-model"
        ),
        properties={"model_type": "Decision Tree"},
    )
    errors = []
    if not model.validate(errors):
        print(f"Error validating model artefact: {errors}")
    return model


def test_build_artefact_visualisation_confusion_matrix() -> SoftwareFile:
    cm_file = SoftwareFile(
        name="Confusion Matrix Visualization",
        description="Visualization of the confusion matrix for the evaluated model.",
        content_type="image/png",
        properties={"Content Preview": "Confusion matrix heatmap"},
    )
    errors = []
    if not cm_file.validate(errors):
        print(f"Error validating confusion matrix artefact: {errors}")
    return cm_file


def test_build_artefact_evaluation_visualization() -> SoftwareFile:
    art_visualization = SoftwareFile(
        name="Evaluation Visualization",
        description="Result from excution , Content Preview: Matrice de Confusion",
    )
    art_visualization.properties.update(
        {"Content Preview": "DecisionTreeClassifier(random_state=42)"}
    )
    errors = []
    if not art_visualization.validate(errors):
        return art_visualization
    print(f"Error validating evaluation visualization artefact: {errors}")
    return art_visualization


def test_build_artefact_metric_accuracy() -> Metric:
    metric_accuracy = Metric(
        name="Model Accuracy",
        description="Accuracy du modèle de classification sur le dataset IRIS.",
        kind=MetricCatalog.PERFORMANCE.ACCURACY,
        # value=0.95,
        # unit="%",
        properties={"calculation_method": "accuracy_score from scikit-learn"},
    )
    metric_accuracy.validate_with_catalog()
    errors = []
    if not metric_accuracy.validate(errors):
        print(f"Error validating accuracy metric artefact: {errors}")
    return metric_accuracy


def test_build_artefact_metric_confusion_matrix() -> Metric:
    confusion_matrix_metric = Metric(
        name="Confusion Matrix",
        description="Matrice de confusion du modèle de classification sur le dataset IRIS.",
        kind=MetricCatalog.PERFORMANCE.CONFUSION_MATRIX,
        properties={"calculation_method": "confusion_matrix from scikit-learn"},
    )
    confusion_matrix_metric.validate_with_catalog()
    errors = []
    if not confusion_matrix_metric.validate(errors):
        print(f"Error validating confusion matrix metric artefact: {errors}")
    print(f"Confusion Matrix Metric: {confusion_matrix_metric}")
    return confusion_matrix_metric


# ---------------------------- Relations ---------------------------


def create_relation_manifest_notebook(manifest, listArtefacts) -> Relationship:
    if len(listArtefacts) == 0:
        print("No notebook found in manifest artefacts")
        return None
    rel1 = Relationship(
        from_=manifest, to_=listArtefacts, relationship_type=RelationshipType.SOURCE
    )
    return rel1


def create_relation_stepLoad_irisDataset(
    step_load: Step, iris_datasets
) -> Relationship:
    if len(iris_datasets) == 0:
        print("No dataset IRIS found in manifest artefacts")
        return None
    if not isinstance(step_load, Step):
        print("step_load is not a Step instance")
        return None
    relation = Relationship(
        from_=step_load,
        to_=iris_datasets,
        relationship_type=RelationshipType.DEPENDS_ON,
    )
    return relation


def create_relation_stepViz_visualisation(step_viz: Step, viz_file) -> Relationship:
    if viz_file is None:
        print("No visualization artefact found in manifest artefacts")
        return None
    return Relationship(
        from_=step_viz, to_=viz_file, relationship_type=RelationshipType.GENERATES
    )


# ------ PRINCIPAL TEST : FROM BUILDING THE MANIFEST TO EXPORTING IT IN MERMAID SYNTAX FOR VISUALIZATION ------
def test_From_building_to_mermaid():
    manifest = test_build_manifestFromNBonIrisClassification()
    to_mermaid(manifest)


def to_mermaid(manifest):
    # This function is a simplified version of the object_to_mermaid_full function, that only generates the pipeline and tasks, without the artefacts and relations.
    serializer = MERMAIDSerializer()
    mermaid_output = serializer.object_to_mermaid_full(manifest)
    # save_in_file(
    #    "./diagrams",
    #    "notebook_pipeline_example_simple.mmd",
    #    to_simple_mermaid(manifest))
    save_in_file("./diagrams", "notebook_pipeline_example_full.mmd", mermaid_output)


# -----
def test_to_yaml_and_reverse_NBIris():
    manifest = test_build_manifestFromNBonIrisClassification()
    output = YAMLSerializer.to_yaml(manifest)
    file_name = manifest.name.replace(" ", "_").lower() + ".yaml"
    save_in_file("./targets/manifests", file_name, output)

    loaded_element: dict = YAMLSerializer.load_yaml_to_dict(output)
    assert loaded_element is not None, "YAML loading to dict returned None"
    assert isinstance(loaded_element, dict), (
        f"Expected loaded element to be a dict, got {type(loaded_element)}"
    )

    manifestBis = YAMLSerializer._from_yaml(Task, loaded_element)
    assert manifestBis is not None, "Deserialization returned None"
    assert manifestBis.pipeline is not None, "Deserialized manifest has no pipeline"
    assert len(manifestBis.pipeline.tasks) == 5, (
        f"Expected 5 tasks in the pipeline, found {len(manifestBis.pipeline.tasks)}"
    )
    assert len(manifestBis.artefacts) == 8, (
        f"Expected 8 artefacts, found {len(manifestBis.artefacts)}"
    )
    assert len(manifestBis.relations) == 6, (
        f"Expected 6 relations, found {len(manifestBis.relations)}"
    )
    print("YAML serialization and deserialization test passed successfully!")
