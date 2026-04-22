"""This module defines specific artefacts related to machine learning,
such as MLModel and Data, which are specialized types of SoftwareFile.
These classes include additional attributes relevant to their specific roles
in the machine learning pipeline,
as well as validation logic to ensure that the attributes conform to expected values."""

from dataclasses import dataclass, field
from typing import Optional, List

from DSL4Pipelines.src.metamodel.artefacts.artefacts import SoftwareFile
from DSL4Pipelines.src.metamodel.catalogs.artefact_catalog import ArtefactCatalog
from DSL4Pipelines.src.metamodel.catalogs.MLModelCatalog import MLModelCatalog
from DSL4Pipelines.src.metamodel.artefacts.Consideration import Consideration


#equivalent to a model card?
@dataclass
class MLModel(SoftwareFile):
    """MLModel is a specific type of SoftwareFile that represents a machine learning model."""
    type: str = (
        "MLModel"  # Override the type to specify that this is an MLModel artifact
    )
    ml_model_type: Optional[str] = (
        None  # e.g., "Transformer", "CNN", "RNN", MLModelCatalog.ML_MODEL_TYPE.TRANSFORMER
    )
    #cycloneDX uses task instead of purpose, but I find that purpose is more intuitive and less technical, so I prefer to use purpose.
    purpose: Optional[str] = (
        None  # e.g., "text-to-image, text classification", "image recognition", "object detection", ...
    )
    architectureFamily: Optional[str] = (
        None  # e.g., ???"
    )
    modelArchitecture: Optional[str] = (
        None  # e.g., "BERT", "ResNet", "LSTM", ...
    )
    modelSize: Optional[str] = (
        None  # e.g., "110M parameters", "1.5B parameters", ...
    )
    consideration: Optional[Consideration] = (
        None  # A field to include any ethical, social, or environmental considerations related to the model (e.g., known biases, potential misuse, etc.)
    )

    def validate(self, errors: list = None) -> bool:
        """Validate the MLModel artifact, ensuring that it conforms to expected properties and values."""
        # 1. first we call the superclass validation to check for common SoftwareFile properties
        base_valid = super().validate(errors)
        # 2. Then we can add specific validation for MLModel, for example checking if the ml_modelType is one of the known types.
        ml_model_type_ok = True  # Default to True if ml_modelType is None
        if self.ml_model_type is not None:
            ml_model_type_ok = (
                self.ml_model_type in MLModelCatalog.ML_MODEL_TYPE.ALL
            )  # Allow None f
        if not ml_model_type_ok:
            errors.append(
                f"ml_modelType '{self.ml_model_type}' is not recognized. Valid types are: {list(MLModelCatalog.ML_MODEL_TYPE.ALL)}"
            )
            print(
                f"Validation error: ml_modelType '{self.ml_model_type}' is not recognized. Valid types are: {list(MLModelCatalog.ML_MODEL_TYPE.ALL)}"
            )
        return base_valid and ml_model_type_ok


## MI: added a new class for data,
# which is a specific type of software file
# with an additional attribute 'data_type'
# to specify the kind of data (e.g., dataset, corpus)
# and (e.g. images, tabular, etc.).
@dataclass
class Data(SoftwareFile):
    """Data is a specific type of SoftwareFile that represents a dataset or corpus
    used for training or evaluating machine learning models."""

    # Using lists to allow for multiple types/kinds/formats, but they can also be single strings if needed
    data_types: List[str] = field(default_factory=list)  # ['images', 'tabular']
    dataset_kinds: List[str] = field(default_factory=list)  # ['corpus', 'dataset']
    data_formats: List[str] = field(default_factory=list)  # ['.jpg', '.csv', '.json']
    type: str = "Data"  # Override the type to specify that this is a Data artifact

    dataset_size: Optional[int] = None  # e.g., size in bytes
    dataset_availability: Optional[str] = (
        None  # e.g., "public", "restricted", "directDownload"
    )
    dataset_has_sensitive_personal_information: Optional[str] = (
        "yes"  # e.g., "yes", "no"
    )
    dataset_intended_use: Optional[str] = (
        None  # e.g., "For training and evaluation of sentiment analysis models."
    )
    dataset_known_bias: List[str] = field(default_factory=list)  # e.g.,

    def __post_init__(self):
        """Petit test interne pour s'assurer que c'est bien une liste"""
        if isinstance(self.data_types, str):
            self.data_types = [self.data_types]

    def validate(self, errors: list = None) -> bool:
        # 1. first we call the superclass validation to check for common SoftwareFile properties
        base_valid = super().validate(errors)
        # 2. Then we can add specific validation for Data, for example checking if the datasetAvailability is one of the known options.
        availability_ok = True  # Default to True if datasetAvailability is None
        if self.dataset_availability is not None:
            availability_ok = self.dataset_availability in ArtefactCatalog.ACCESS.ALL
            if not availability_ok:
                errors.append(
                    f"datasetAvailability '{self.dataset_availability}' is not recognized. "
                )
                print(
                    f"Validation error: datasetAvailability '{self.dataset_availability}' is not recognized. Valid options are: {ArtefactCatalog.ACCESS}"
                )
        return base_valid and availability_ok
