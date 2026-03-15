"""
This module defines the Relationship class,
which represents a relationship between elements in the DSL4Pipelines
metamodel.
A relationship connects a source element (from)
to one or more target elements (to) with a specific relationship type.
The Relationship class includes validation
to ensure that the 'from' and 'to' fields are properly populated
and that the relationship type is valid according to the defined vocabulary.
"""

from dataclasses import dataclass, field
from typing import List, Any

from DSL4Pipelines.src.metamodel.core.structure import Element
from DSL4Pipelines.src.metamodel.catalogs.vocabulary import RelationshipType


################### Relationships ###################

# https://spdx.github.io/spdx-spec/v3.0.1/model/Core/Vocabularies/RelationshipType/


@dataclass
class Relationship(Element):
    """Relationship represents a relationship between elements in the DSL4Pipelines metamodel."""

    # On donne une valeur par défaut (None ou chaîne vide)
    from_: Element = field(default="", metadata={"json_name": "from"})
    to_: List[Element|str] = field(default_factory=list)
    relationship_type: RelationshipType = RelationshipType.USES
    type: str = "Relationship"

    def __post_init__(self):
        super().__post_init__()  # Appel du post_init de la classe parente pour gérer le type par défaut
        # On peut aussi ajouter une validation spécifique pour les relations, par exemple vérifier que from_ et to_ sont valides.
        if not self.from_:
            raise ValueError("The 'from' field cannot be empty.")
        if not self.to_:
            raise ValueError("The 'to' field cannot be empty.")
        # check to is a list of Element or a list of strings (ids)
        if not all(isinstance(t, (Element, str)) for t in self.to_):
            print("Invalid 'to' field:", self.to_)
            raise ValueError(
                "All items in 'to' must be either Element instances or strings (ids)."
            )
        # check from is an Element or a string (id)
        if not isinstance(self.from_, (Element, str)):
            print("Invalid 'from' field:", self.from_)
            raise ValueError(
                "The 'from' field must be either an Element instance or a string (id)."
            )


"""
        {
            "creationInfo": "_:creationinfo",
            "from": "https://spdx.org/spdxdocs/DatasetPackage1-d1f693d0-b420-4b6a-b9f2-ec2097bac863",
            "relationshipType": "hasDeclaredLicense",
            "spdxId": "https://spdx.org/spdxdocs/Relationship/hasDeclaredLicense1-d1741c4c-4c18-459a-b9f9-e24f018e39f1",
            "to": [
                "https://spdx.org/licenses/CC0-1.0"
            ],
            "type": "Relationship"
        },
"""

# =====================================================================
# ---Test bloc and usage example---
# =====================================================================
