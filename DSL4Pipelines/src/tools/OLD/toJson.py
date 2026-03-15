# @TODO : OLD VERSION, TO UPDATE
# ECHOUE car structure trop récursive, à revoir pour éviter les références circulaires (ex: creationInfo dans Person) et/ou ajouter des méthodes de sérialisation personnalisées dans les dataclasses

import json
from dataclasses import asdict
from typing import List, Any

from DSL4Pipelines.src.metamodel.artefacts.artefacts import Person, SoftwareFile


def to_json(elements_list: List[Any]) -> str:
    """Convertit une liste de dataclasses en une chaîne JSON formatée."""
    # On transforme chaque élément de la liste en dictionnaire
    list_of_dicts = [asdict(e) for e in elements_list]
    return json.dumps(list_of_dicts, indent=4, ensure_ascii=False)


# =====================================================================
# ---Test bloc and usage example---
# =====================================================================

if __name__ == "__main__":
    # 1. Preparing test objects
    creInfo = "_:creationinfo"

    pers = Person(
        uid="https://spdx.org/spdxdocs/Person/AS-123",
        creation_info=creInfo,
        name="Arthit Suriyawongkul",
    )

    # Exemple
    # print(object_to_mermaid(pers, "archit"))
    fichier = SoftwareFile(
        uid="https://spdx.org/spdxdocs/File10-model",
        creation_info=creInfo,
        name="model.bin",
        software_file_kind="file",
        software_primary_purpose="model",
    )

    # 2. regrouping elements
    my_elements = [pers, fichier]

    # 3. Conversion
    json_result = to_json(my_elements)

    print("--- Generated JSON ---")
    print(json_result)

    # 4. Tests
    loaded_data = json.loads(json_result)

    assert isinstance(loaded_data, list), "Result should be a list."
    assert len(loaded_data) == 2, "Result list should contain 2 elements."
    assert loaded_data[0]["name"] == "Arthit Suriyawongkul"
    assert loaded_data[1]["software_primaryPurpose"] == "model"

    print("\n✅ Simple Tests passed successfully.")

    #manifest = test_build_manifestFromNBonIrisClassification()
    json_result = to_json([manifest])
    print(json_result)

    print("\n✅ Transformation To Json passed")

    #manifest =test_build_manifestFromNBonIrisClassification()
    json_result = to_json([manifest])
    print("--- Manifest JSON ---")
    print(json_result)

    print("\n✅ All tests passed successfully.")
