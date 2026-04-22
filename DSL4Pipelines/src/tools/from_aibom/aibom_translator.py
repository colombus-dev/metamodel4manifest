import json
from pathlib import Path
from typing import Optional, Any


from DSL4Pipelines.src.metamodel.core.structure import ExternalReference, Element

from DSL4Pipelines.src.metamodel.artefacts.artefacts import SoftwareFile
from DSL4Pipelines.src.metamodel.manifests.manifests import Manifest
from DSL4Pipelines.src.metamodel.relations.relations import Relationship

from DSL4Pipelines.src.metamodel.catalogs.vocabulary import RelationshipType
from DSL4Pipelines.src.tools.toFile import print_cwd
from DSL4Pipelines.src.metamodel.artefacts.ml_artefacts import MLModel, Data
from DSL4Pipelines.src.metamodel.artefacts.Consideration import Consideration
from DSL4Pipelines.src.metamodel.catalogs.vocabulary import FileKind


# Dans aibom_translator.py
import logging



logging.basicConfig(
    level=logging.INFO, # Niveau par défaut pour TOUT le monde
    format='%(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class AIBOMTranslator:

    def __init__(self, file_path):
        self.file_path = file_path
        self.manifest : Manifest = Manifest()
        self.ml_model : MLModel = MLModel()
        print_cwd()
        # Read the AIBOM file and store its content in self.data
        # If the file is not found, this will raise a FileNotFoundError
        with open(file_path, 'r') as f:
           self.data = json.load(f)
        self.metadata = self.data.get("metadata", {})

    def transform_aibom_to_manifest(self):
        with open(self.file_path, 'r') as f:
            data = json.load(f)

        self.build_sofware_file_for_aibom()
        self.build_model()
        self.build_components()

        return self.manifest

    def build_sofware_file_for_aibom(self) -> SoftwareFile:
        logger.debug("----------Building software file for AIBOM...")
        reference = ExternalReference()
        reference.external_identifier_type = "urlScheme"
        # transform the file path to a URI (e.g. "file:///path/to/file") and set it as the identifier of the reference
        uri = Path(self.file_path).resolve().as_uri()
        logger.debug(uri)
        reference.identifier = uri

        software_file = SoftwareFile()
        software_file.name = self.file_path.split('/')[-1]  # On utilise le nom du fichier comme nom de l'artefact
        software_file.uid = uri  # On utilise l'URI du fichier
        software_file.external_reference = reference
        software_file.content_type = "AIBOM"
        software_file.properties = {
        "bomFormat": self.data.get("bomFormat"),
        "specVersion": self.data.get("specVersion"),
        "serialNumber": self.data.get("serialNumber"),
        "version": self.data.get("version")
        }
        relation = Relationship(from_=self.manifest,
                                to_=[software_file],
                                relationship_type=RelationshipType.ANNOTATED_BY)
        self.manifest.artefacts.append(software_file)
        self.manifest.relations.append(relation)
        return software_file


    # This method will extract information about the model from the metadata of the AIBOM
    # and from the model card section of the AIBOM metadata,
    # and set it as properties of the MLModel artefact,
    # then add this model as an artefact of the manifest and
    # create a relation of type "annotatedBy" between the manifest and the model.
    # It will also build a dependency relation between the model and the library it uses (e.g. diffusers, transformers, etc.) based on the properties of the model card, if they exist and if they contain a property with name "library_name" and value "diffusers".

    def build_model(self) -> MLModel:
        logger.debug("----------Building model...")
        treated_properties = set()  # Set to keep track of properties that have been treated
        #extract information about the model from the metadata of the AIBOM
        mlmodel_properties = {
            "timestamp": self.metadata.get("timestamp","")
        }
        treated_properties.add("timestamp")
            #deal with the component section of the AIBOM, which contains information about the model, and set it as properties of the MLModel artefact, then add this model as an artefact of the manifest and create a relation of type "annotatedBy" between the manifest and the model.
            #we will also extract information about the model from the model card section of the AIBOM metadata and set it as properties of the MLModel artefact, then add this model as an artefact of the manifest and create a relation of type "annotatedBy" between the manifest and the model.
            #we will also build a dependency relation between the model and the library it uses (e.g. diffusers, transformers, etc.) based on the properties of the model card, if they exist and if they contain a property with name "library_name" and value "diffusers".

        component = self.metadata.get("component", {})
        mlmodel_properties = self.deal_with_MLModelComponent(component, treated_properties, mlmodel_properties)
        self.ml_model.properties = mlmodel_properties
        self.manifest.artefacts.append(self.ml_model)
        relation = Relationship(from_=self.manifest,
                                to_=[self.ml_model],
                                relationship_type=RelationshipType.PRODUCES)
        self.manifest.relations.append(relation)
        return self.ml_model


    def build_components(self) -> MLModel:
        logger.debug("----------Building components...")
        components = self.data.get("components", [])
        for component in components:
            logger.debug(f"xxxx Processing component : {component}")
            if component.get("type") == "data":
                self.addLocalDefinedComponents(component)

    def deal_with_MLModelComponent(self,
                                   component,
                                   component_treated_properties: set[Any],
                                   mlmodel_properties: dict[str, Any]) -> dict[str, Any]:
        fields_to_copy = ["bom-ref", "name", "authors"]
        for field in fields_to_copy:
            value = component.get(field)
            if value is not None:
                mlmodel_properties[field] = value
        component_treated_properties.update(fields_to_copy)

        #deal with the licenses field, which is a list of licenses, we will take the first license of the list and set it as the license of the model, and we will add the "licenses" property to the treated properties
        licenses = component.get("licenses", [])
        if licenses:
            self.ml_model.license = component.get("licenses", "")[0].get("license", "")
        component_treated_properties.add("licenses")

        #deal with the external reference of the model, we will take the first external reference of the list and set it as the external reference of the model, and we will add the "externalReferences" property to the treated properties
        external_reference = ExternalReference()
        external_reference.external_identifier_type = "urlScheme"
        reference = component.get("externalReferences", [{}])[0]
        if reference:
            external_reference.kind = reference.get("type", "")
            external_reference.identifier = reference.get("url", "")
        self.ml_model.external_reference = external_reference
        component_treated_properties.add("externalReferences")

        # extract information about the model from the model card section of the AIBOM metadata and set it as properties of the MLModel artefact, then add this model as an artefact of the manifest and create a relation of type "annotatedBy" between the manifest and the model.
        modelcard = component.get("modelCard", {})
        component_treated_properties.add("modelCard")
        self.deal_with_modelCard_in_component(modelcard,mlmodel_properties)
        manage_remaining_properties(component, component_treated_properties, mlmodel_properties)
        return mlmodel_properties

# ----------------
# This method will extract information about the model
# from the model card section of the AIBOM metadata and
#set it as properties of the MLModel artefact,
# then add this model as an artefact of the manifest and
#create a relation of type "annotatedBy" between the manifest and the model.
# ------------------

    def deal_with_modelCard_in_component(self, modelcard, mlmodel_properties) -> Any:
        "This method will extract information about the model from the model card section of the AIBOM metadata and set it as properties of the MLModel artefact"
        modelcard_treated_properties = set()  # Set to keep track of properties that have been treated in the model card section

        #deal with the model parameters section of the model card, which contains information about the model,
        # and set it as properties of the MLModel artefact,
        modelcard_treated_properties.add("modelParameters")
        self.deal_with_modelParameters_of_modelcard(mlmodel_properties, modelcard)

        #deal with the library used by the model, which is a property of the model card,
        # we will create a new artefact for the library and create a relation of type "uses" between the model and the library,
        # and we will add the "library_name" property to the treated properties of the model card
        modelcard_treated_properties.add("properties")
        self.deal_with_properties_of_modelcard(mlmodel_properties, modelcard)

        modelcard_treated_properties.add("consideration")
        self.deal_with_consideration_of_modelcard(mlmodel_properties, modelcard)
        manage_remaining_properties(modelcard, modelcard_treated_properties, mlmodel_properties)

        return mlmodel_properties

    def deal_with_consideration_of_modelcard(self, mlmodel_properties, modelcard):
        consideration = modelcard.get("consideration", {})
        if consideration:
            self.ml_model.consideration = Consideration(
                use_cases = consideration.get("useCases",[]),
                limitations = consideration.get("limitation", []),  # Ce que le modèle ne sait pas faire
                ethical_risks = consideration.get("ethical_risks",[]),
                intended_users = [] # The model card does not contain information about the intended users of the model, so we set it to "unknown"
            )


    def deal_with_properties_of_modelcard(self, mlmodel_properties, modelcard):
        modelCard_properties = modelcard.get("properties", {})
        prop_treated_properties = set()
        prop_treated_properties.add("library_name")
        # PROBLEM
        # @todo we have to create a new artefact for the model card and link it to the model with a relation of type "annotatedBy", because the model card contains information about the model but is not the model itself, and we want to keep this information in the manifest as well.
        # self.manifest.artefacts.append(modelcard)
        # build dependency relation between the model and the library it uses (e.g. diffusers, transformers, etc.) based on the properties of the model card, if they exist and if they contain a property with name "library_name" and value "diffusers"
        logger.debug(f"Model card : {modelcard}")
        logger.debug(f"Model card properties : {modelCard_properties}")

        # Deal with the model card properties and set them as properties of the model card
        # @todo then add the model card as an artefact of the manifest and create a relation of type "annotatedBy" between the model and the model card.

        library = self.extract_library(modelCard_properties)
        if library:
            # we create a relation of type "uses" between the model and the library
            relation = Relationship(from_=self.ml_model,
                                    to_=[library],
                                    relationship_type=RelationshipType.USES)
            self.manifest.relations.append(relation)

        prop_treated_properties.add("base_model")
# Deal with a base_model property of the model card, which indicates that the model is based on another model, we will create a relation of type "derivedFrom" between the model and the base model
        baseModel = self.extract_base_model(modelCard_properties)
        if baseModel:
            relation = Relationship(from_=self.ml_model,
                                    to_=[baseModel],
                                    relationship_type=RelationshipType.DERIVED_FROM)
            self.manifest.relations.append(relation)
        #manage_remaining_properties(modelCard_properties, prop_treated_properties, mlmodel_properties)

    def deal_with_modelParameters_of_modelcard(self, mlmodel_properties, modelcard):
        # deal with the model parameters section of the model card,
        # which contains information about the model, and set it as properties of the MLModel artefact,
        modelparameters = modelcard.get("modelParameters", {})

        # deal with the pupose
        purpose = modelparameters.get("task", "")
        modelParameters_treated_properties = set()
        modelParameters_treated_properties.add("task")
        self.ml_model.purpose = purpose

        datasets = modelparameters.get("datasets", "")
        modelParameters_treated_properties.add("datasets")
        if datasets:
            logger.debug(f"Datasets used by the model : {datasets}")
            datasetsObjects = []

            for dataset in datasets:
                logger.debug(f"--- Processing dataset : {dataset}")
                dataset_reference = ExternalReference()
                dataset_reference.identifier = dataset.get("ref", "")
                if dataset_reference.identifier:
                    if dataset_reference.identifier.startswith("http://") or dataset_reference.identifier.startswith(
                            "https://"):
                        dataset_reference.external_identifier_type = "urlScheme"
                    else:
                        dataset_reference.external_identifier_type = "other"
                dataset = Data(external_reference=dataset_reference)
                self.manifest.artefacts.append(dataset)
                datasetsObjects.append(dataset)

            relation = Relationship(from_=self.ml_model,
                                    to_=datasetsObjects,
                                    relationship_type=RelationshipType.USES)
            self.manifest.relations.append(relation)

        manage_remaining_properties(modelparameters, modelParameters_treated_properties, mlmodel_properties)

    def extract_library(self, properties) -> Optional[SoftwareFile]:
        for prop in properties:
            if prop.get("name") == "library_name":
                lib_name = prop.get("value")
                logger.debug(f"Library used by the model: {lib_name}")

                # Création de l'artefact
                library = SoftwareFile()
                library.content_type = FileKind.LIBRARY
                library.name = lib_name
                self.manifest.artefacts.append(library)
                return library
        return None



    def extract_base_model(self, properties):
        for prop in properties:
            if prop.get("name") == "base_model":
                ref = prop.get("value")
                logger.debug(f"Base model: {ref}")
                # Création de l'artefact
                model = MLModel()
                model.external_reference = ExternalReference(
                    external_identifier_type="urlScheme",
                    identifier=ref
                )
                self.manifest.artefacts.append(model)
                return model
        return None


    def addLocalDefinedComponents(self,dataComponent):
        #we look for a Data Artefact in the manifest with the same external reference as the data component,
        data_artifacts = [a for a in self.manifest.artefacts if isinstance(a, Data)]
        logger.debug(f"Looking for a data artefact with the same external reference as the data component {dataComponent} among the data artefacts of the manifest : {data_artifacts}")
        for data_artifact in data_artifacts:
            if data_artifact.external_reference and data_artifact.external_reference.identifier == dataComponent.get("bom-ref"):
                completeDataArtifact(data_artifact,dataComponent)
        #if we find it, we update its properties with the properties of the data component, and we add the properties of the data component to the treated properties of the component section, so that they will not be added again as remaining properties of the component section.


def manage_remaining_properties(source, treated_properties:set, properties: dict[str, Any]):
    """This method takes a source dictionary,
    a set of treated properties
    and an element
    and adds to the properties of the element all the properties of the source that have not been treated yet"
    """
    treated_properties.add("type")
    logger.debug(f"Source properties : {source} and treated properties : {treated_properties}")
    for key, value in source.items():
        if key not in treated_properties:
            if value:
                if (isinstance(value, list) and len(value) == 0):
                    continue  # Skip empty lists
                properties[key] = value

    logger.debug(f"Element properties after managing remaining properties : {properties}")




def completeDataArtifact(data_artifact, dataComponent):

    logger.debug(f"----------Completing data artifact {data_artifact} \n\t with data component {dataComponent}")
    properties = data_artifact.properties if data_artifact.properties else {}
    treated_properties = set()
    fields_to_copy = ["bom-ref", "name", "authors"]
    for field in fields_to_copy:
        value = dataComponent.get(field)
        if value is not None:
            properties[field] = value
        treated_properties.add(field)
    data_artifact.properties = properties


    data_list = dataComponent.get("data", [])
    for data in data_list:
        #we don't read again type etc
        contents = data.get("contents", [])
        if contents:
            deal_with_dataComponent_contents(data_artifact, contents)
    treated_properties.add("data")
    manage_remaining_properties(dataComponent, treated_properties, data_artifact.properties)


def deal_with_dataComponent_contents(data_artifact, contents):
    data_artifact.properties = data_artifact.properties if data_artifact.properties else {}
    logger.debug(f"Processing content of data component : {contents}")
    # URL
    url = contents.get("url","")
    if url:
        reference = data_artifact.external_reference
        if reference is None:
            reference = ExternalReference(identifier=url, external_identifier_type="urlScheme")
            data_artifact.external_reference = reference
        else:
            data_artifact.properties["content_url"] = url
        #print(f"====> url - Data artefact after copying fields : {data_artifact}")
    #deal with properties of the content
    content_properties = contents.get("properties", [])
    for prop in content_properties:
        key = prop.get("name")
        value = prop.get("value")
        # On l'ajoute au dictionnaire de l'artefact
        if key:
            if key=="language":
                if data_artifact.languages:
                    data_artifact.languages.append(value)
                else:
                    data_artifact.languages = [value]
            else:
                data_artifact.properties[key] = value
    manage_remaining_properties(contents, set(["url", "properties"]), data_artifact.properties)


