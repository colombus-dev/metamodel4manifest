from enum import Enum
# https://github.com/spdx/tools-python/blob/main/src/spdx_tools/spdx/model/relationship.py
# 1. On définit les types autorisés par le standard

""""
Type de Relation,Usage dans votre SBOM
contains,Un package contient un fichier ou un répertoire.
generates,Un script (ex: train.py) génère un artefact (ex: model.bin).
trainedOn,Un modèle a été entraîné en utilisant un dataset spécifique.
testedOn,Un modèle a été évalué sur un dataset de test.
hasDocumentation,Lie un package à son fichier README.md ou ses techdocs.
dependsOn,Un script a besoin d'une bibliothèque ou d'un autre fichier.
hasDataFile,"Un script de prédiction utilise un fichier de poids (.bin, .pt)."
"""


# Some relationship types are not included in the SPDX standard but can be useful for our use case, so we can add them as needed.
class RelationshipType(str, Enum):
    PRODUCES = "produces"  # to link a script to the artefact it produces (e.g., train.py produces model.bin, ...)
   # EVALUATES = "evaluates" # to link a script to the artefacts and the metrics it evaluates e.g., from_ : a code  to_: a dataset, a model and a metric
    ANNOTATED_BY = "annotatedBy" #to link a task or step to a category and taxonomy
    USES = "uses" # to link a script to the artefacts it uses (e.g., predict.py uses model.bin, ...)
    COMPOSED_OF = "composedOf" # to link an Element to its components (e.g., a pipeline composedOf steps, a step composedOf scripts and artefacts, ...)

 #   CONTAINS = "contains"
 #   TRAINED_ON = "trainedOn" #
 #   TESTED_ON = "testedOn"
 #   HAS_DECLARED_LICENSE = "hasDeclaredLicense"
#    HAS_DATA_FILE = "hasDataFile"
#    HAS_DOCUMENTATION = "hasDocumentation"
   # DEPENDS_ON = "dependsOn"
    # Pour l'évaluation de performance pure
#    PERFORMANCE_EVALUATION = "evaluates_performance"
    # Pour l'évaluation éthique/biais
#    BIAS_ASSESSMENT = "assesses_bias"

    # Pour la validation de pipeline
#    INTEGRITY_CHECK = "checks_integrity"
    #EVALUATED_BY = "evaluated_by" #
    #GENERATED_FROM = "generatedFrom"
#    GENERATED_BY = "generatedBy"
#    GENERATES = "generates"
#    USED_BY = "usedBy" # to link an artefact to the script that uses it (e.g., model.bin usedBy predict.py)

    # Mi
    #SOURCE = "hasForSource" # to link
    NEXT = "next"  # MI added for pipeline steps
    #    HAS_PREREQUISITE = auto()
    #    METAFILE_OF = auto()
    #    OPTIONAL_COMPONENT_OF = auto()
    #    OPTIONAL_DEPENDENCY_OF = auto()
    OTHER = "other"




#    PACKAGE_OF = auto()
#    PATCH_APPLIED = auto()
#    PATCH_FOR = auto()
#   PREREQUISITE_FOR = auto()
#    PROVIDED_DEPENDENCY_OF = auto()
#    REQUIREMENT_DESCRIPTION_FOR = auto()
#    RUNTIME_DEPENDENCY_OF = auto()
#    SPECIFICATION_FOR = auto()
#    STATIC_LINK = auto()
#    TEST_CASE_OF = auto()
#   TEST_DEPENDENCY_OF = auto()
#   TEST_OF = auto()
#   TEST_TOOL_OF = auto()
#   VARIANT_OF = auto()


class FileKind(str, Enum):
    FILE = "file"
    DIRECTORY = "directory"
