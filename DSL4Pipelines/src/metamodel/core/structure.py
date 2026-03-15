"""
This module defines the core data structures
for representing elements in a graph-based model,
inspired by the SPDX specification.

The main classes include:
- `CreationInfo`: Represents metadata about the creation of an element (SPDX)
- `Element`: A base class for all elements in the graph, with common attributes like
        `uid`, `type`, `name`, `description`, and a reference to `CreationInfo`.
        It also includes a flexible `properties` field that can store additional key-value pairs,
        and a method `get_value` to retrieve values from either the actual attributes or the properties.
- `Property`: Represents a simple key-value pair that can be associated with an element.
- `ExternalReference`: Represents a reference to an external resource, including its type and identifier.
"""

import json
import uuid
from typing import Optional, List, Union, Dict, Any
from dataclasses import dataclass, field, asdict

import yaml

YamlValue = Union[str, int, float, bool, List[Any], Dict[str, Any], None]


# From SPDX
@dataclass
class CreationInfo:
    """Represents metadata about the creation of an element,
    including who created it and when."""

    #    created: str
    created_by: List[str]
    type: str = "CreationInfo"
    uid: Optional[str] = None
    created_on: Optional[str] = None
    spec_version: Optional[str] = None


# From SPDX mais simplifié ...


@dataclass
class Element:
    """Base class for all elements in the graph.
    It includes common attributes and a flexible properties field.
    type is a required field, but it can be set to the name of the class by default if not provided.
        it is used to identify the type of the element in the graph,
        and can be used for transformation, validation and processing logic.
    """

    uid: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    creation_info: Optional[CreationInfo] = (
        None  # Optionel for now, we will link it later with the actual CreationInfo object
    )
    # On accepte soit une liste de Property, soit un dictionnaire
    #YamlValue est un type qui peut être une valeur simple (str, int, float, bool), une liste ou un dictionnaire, ou None.
    properties: Dict[str, YamlValue] = field(default_factory=dict)

    # @todo : forbid properties to have keys that are the same as actual attributes (uid, type, name, description, creation_info) to avoid confusion and conflicts in get_value method.
    def __post_init__(self):
        """Post-initialization to set the type to the class name if it's not explicitly provided."""
        # When the object is created, if the type is not explicitly set, we can set it to the name of the class by default.
        if self.type is None:
            # We can use the class name as the default type, but it can be overridden if needed.
            self.type = self.__class__.__name__

    def validate(self, errors: Optional[list] = None) -> bool:
        """Validate the element and its properties.
        This method can be overridden in subclasses to implement specific validation logic."""
        # Initialize the errors list if it's not provided
        if errors is None:
            errors = []
        return True  # Placeholder for validation logic, to be implemented as needed

    def get_value(self, name: str, default=None) :
        """Get the value of an attribute or property by name.
        This method first checks if the name corresponds to an actual attribute of the object (or a Python property),
        and if not found, it looks in the 'properties' field, which can be either a dictionary or a list of Property objects.
        """
        # 1. Attempt to get the value from the actual attribute (or Python property)
        value = getattr(self, name, None)
        if value is not None:
            return value

        # 2. If not found, look in the 'properties' field
        props = getattr(self, "properties", None)
        if not props:
            return default

        # Cas A : properties is a dictionary
        if isinstance(props, dict):
            return props.get(name, default)

        # Cas B : properties is a list of Property objects
        if isinstance(props, list):
            for p in props:
                if getattr(p, "name", None) == name:
                    return getattr(p, "value", default)

        return default


# The Property class represents a key-value pair that can be associated with
# A améliorer pour savoir si on est sur des éléments externes ou non..
# il faudrait avoir des dtypes de valeurs différents str ou Element au moins.


@dataclass
class Property:
    name: str
    value: str


# @toREMOVE? The ExternalIdentifier est-ce utile?? ca peut éviter des recherches inutiles
@dataclass
class ExternalReference:
    """From SPDX Represents a reference to an external resource,
    including its type and identifier."""

    external_identifier_type: Optional[str] = None
    identifier: Optional[str] = None
    type: str = "ExternalReference"


#    issuingAuthority: Optional[str] = None
#    identifierLocator: List[str] = field(default_factory=list)


# =====================================================================
# ---Test bloc and usage example---
# =====================================================================
if __name__ == "__main__":
    print("------------ 1. Creating CreationInfo metadata")
    creation_info = CreationInfo(
        spec_version="3.0.1",
        created_by=["https://spdx.org/spdxdocs/Person/AS-123"],
        uid="_:creationinfo",
    )

    print("------------ 2. Creating a Document that references CreationInfo")
    doc = Element(
        creation_info=creation_info,  # Utilise l'ID de l'objet ci-dessus
        uid="https://spdx.org/spdxdocs/MyDoc-001",
        type="Document",
        name="My SPDX Document",
        description="Un exemple de document SPDX avec CreationInfo",
    )

    print("------------ 3. Test de validation simple")
    print("Vérification des liens internes...")
    assert doc.creation_info == creation_info
    print("✅ Le lien entre le Document et CreationInfo est correct.")

    print("------------  4. Aperçu du JSON généré (pour simuler le @graph)")
    graph = [asdict(creation_info), asdict(doc)]
    print("\nStructure du graphe SPDX (extrait) :")
    print(json.dumps(graph, indent=4))

    print("------------  5. Exécution de la fonction")
    test_filename = "../../../sandbox/sbomInspired/test_spdx_creation.yaml"
    # save_struct_to_yaml(creation_info, test_filename)

    print("------------ 6. Test de vérification (on recharge le fichier pour comparer)")
    print("Vérification du contenu du fichier...")
    with open(test_filename, "r") as f:
        loaded_data = yaml.safe_load(f)
    try:
        # Assertions pour s'assurer que la data n'a pas été corrompue
        assert "creationInfo" in loaded_data, "La clé racine est manquante !"
        assert loaded_data["creationInfo"]["specVersion"] == "3.0.1"
        assert loaded_data["creationInfo"]["spdxId"] == "_:creationinfo"
        assert "AS-123" in loaded_data["creationInfo"]["createdBy"][0]

        print("✅ Test réussi : Le YAML est valide et fidèle à l'objet Python !")

    except AssertionError:
        val = loaded_data["creationInfo"]["spdxId"]
        print(
            f"❌ Erreur d'assertion ! La valeur est '{val}' au lieu de '_:creationinfo'"
        )
        # Optionnel : lever l'erreur après le message
        raise
    # Optionnel : On nettoie le fichier de test après
    # os.remove(test_filename)
