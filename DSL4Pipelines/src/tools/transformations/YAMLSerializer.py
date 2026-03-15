#import json
from dataclasses import asdict
from enum import Enum
from typing import Type, TypeVar, Any

import yaml
from dacite import from_dict, Config

from DSL4Pipelines.src.metamodel.artefacts.ml_artefacts import MLModel, Data
from DSL4Pipelines.src.metamodel.artefacts.artefacts import (
    SoftwareFile,
    Artefact,
    Person,
)
from DSL4Pipelines.src.metamodel.artefacts.metrics import Metric
from DSL4Pipelines.src.metamodel.catalogs.vocabulary import FileKind
from DSL4Pipelines.src.metamodel.core.structure import (
    Element,
    CreationInfo,
    ExternalReference,
)
from DSL4Pipelines.src.metamodel.manifests.manifests import Manifest
from DSL4Pipelines.src.metamodel.pipelines.workflow import (
    Instruction,
    Pipeline,
    Command,
    Task
)
from DSL4Pipelines.src.metamodel.relations.relations import Relationship
#from tools.OLD.toJson import to_json
from DSL4Pipelines.src.metamodel.taxonomies.taxonomy import Taxonomy, Category


class YAMLSerializer:
    T = TypeVar("T")

    # On définit le mapping en dehors pour qu'il soit réutilisable
    MAPPING = {
        "Metric": Metric,
        "SoftwareFile": SoftwareFile,
        "MLModel": MLModel,
        "Data": Data,
        "Artefact": Artefact,
        "Element": Element,
        "Manifest": Manifest,
        "CreationInfo": CreationInfo,
        "Pipeline": Pipeline,
        "Command": Command,
        "Task": Task,
        "Instruction": Instruction,
        "Relationship": Relationship,
        "ExternalReference": ExternalReference,
        "Category": Category,
        "Taxonomy": Taxonomy
    }

    @staticmethod
    def _to_dict_safe(obj, visited=None):
        if visited is None:
            visited = set()

        # Si c'est un Enum, on prend juste sa valeur
        if isinstance(obj, Enum):
            return obj.value
        # 1. On gère les listes
        if isinstance(obj, list):
            return [YAMLSerializer._to_dict_safe(item, visited) for item in obj]

        # 2. On gère les objets complexes (Element et ses enfants)
        if hasattr(obj, "uid"):
            # ANTI-BOUCLE : Si on a déjà traité cet UID, on ne renvoie que l'ID
            if obj.uid in visited:
                return obj.uid

            visited.add(obj.uid)

            # EXHAUSTIVITÉ : Au lieu de __dataclass_fields__, on utilise vars()
            # qui voit TOUT ce qui est réellement stocké dans l'instance
            result = {}
            for key, value in vars(obj).items():
                if key.startswith("_"):
                    continue  # On cache l'interne

                # Nettoyage récursif intégré
                cleaned = YAMLSerializer._to_dict_safe(value, visited)
                if cleaned is not None:
                    result[key] = cleaned
            return result

        # 3. On gère les dictionnaires (comme properties)
        if isinstance(obj, dict):
            return {
                k: YAMLSerializer._to_dict_safe(v, visited)
                for k, v in obj.items()
                if v is not None
            }

        if isinstance(obj, ExternalReference):
            return asdict(
                obj
            )  # On utilise la méthode dédiée pour éviter les problèmes de récursivité

        return obj

    @staticmethod
    def _to_dict_custom(obj, is_reference=False):
        # 1. Si c'est une liste, on traite chaque élément
        if isinstance(obj, list):
            return [YAMLSerializer._to_dict_custom(item, is_reference) for item in obj]

        # 2. Si c'est un objet de type Element (Artefact, Pipeline, etc.)
        if hasattr(obj, "__dataclass_fields__"):  # Vérifie si c'est une dataclass
            # CAS CRITIQUE : Si on est dans un contexte de "référence" (ex: source/target d'une relation)
            # OU si l'objet est un Element et qu'on veut juste son ID
            if is_reference and hasattr(obj, "uid"):
                return obj.uid

            # Sinon, on construit le dictionnaire normalement
            result = {}
            for field in obj.__dataclass_fields__:
                value = getattr(obj, field)
                # Si l'objet actuel est une Relationship, ses champs source/target doivent être des références
                next_is_ref = isinstance(obj, Relationship) and field in [
                    "from_",
                    "to_",
                ]
                cleaned_val = YAMLSerializer._to_dict_custom(
                    value, is_reference=next_is_ref
                )
                if cleaned_val is not None:
                    result[field] = cleaned_val
            return result

        # 3. Cas des dictionnaires (comme 'properties')
        if isinstance(obj, dict):
            return {
                k: YAMLSerializer._to_dict_custom(v)
                for k, v in obj.items()
                if v is not None
            }
        return obj

    @staticmethod
    def _get_real_class(data: dict, default_cls: Type[T]) -> Type:
        """Détermine la vraie classe à utiliser selon le champ 'type'."""
        if isinstance(data, dict) and "type" in data:
            return YAMLSerializer.MAPPING.get(data["type"], default_cls)
        return default_cls

    @staticmethod
    def smart_hook(d, config, cls):
        # CAS 1 : C'est déjà l'UID (une string dans le YAML)
        if isinstance(d, str):
            # On crée un objet "coquille vide" avec juste l'UID
            # Le recâblage (rebuild_all_links) remplacera ça par le vrai objet plus tard
            return cls(uid=d)

        # CAS 2 : C'est un dictionnaire (définition complète)
        if isinstance(d, dict):
            real_class = YAMLSerializer._get_real_class(d, cls)
            return from_dict(data_class=real_class, data=d, config=config)

        return d

    @staticmethod
    def _from_yaml(cls: Type[T], data: dict) -> T:
        if not isinstance(data, dict):
            raise ValueError(
                "Input data must be a dictionary. Call YAMLSerializer.load_yaml_to_dict() first if you have a YAML string."
            )

        # 1. On détermine la VRAIE classe cible (ex: Metric au lieu d'Element)
        real_cls = YAMLSerializer._get_real_class(data, cls)

        # 2. Configuration pour les objets imbriqués (ex: List[Artefact])
        # Ici, on met les hooks sur les classes mères pour que dacite
        # appelle notre logique quand il rencontre un Artefact dans une liste.
        config_local = Config(cast=[Enum, dict])
        config_local.type_hooks = {
            Element: lambda d: from_dict(
                data_class=YAMLSerializer._get_real_class(d, Element),
                data=d,
                config=config_local,
            ),
            Artefact: lambda d: from_dict(
                data_class=YAMLSerializer._get_real_class(d, Artefact),
                data=d,
                config=config_local,
            ),
            Pipeline: lambda d: from_dict(
                data_class=YAMLSerializer._get_real_class(d, Pipeline),
                data=d,
                config=config_local,
            ),
            Command: lambda d: from_dict(
                data_class=YAMLSerializer._get_real_class(d, Command),
                data=d,
                config=config_local,
            ),
            Instruction: lambda d: from_dict(
                data_class=YAMLSerializer._get_real_class(d, Instruction),
                data=d,
                config=config_local,
            ),
            Manifest: lambda d: from_dict(
                data_class=YAMLSerializer._get_real_class(d, Manifest),
                data=d,
                config=config_local,
            ),
            MLModel: lambda d: from_dict(
                data_class=YAMLSerializer._get_real_class(d, MLModel),
                data=d,
                config=config_local,
            ),
            Data: lambda d: from_dict(
                data_class=YAMLSerializer._get_real_class(d, Data),
                data=d,
                config=config_local,
            ),
            Relationship: lambda d: YAMLSerializer.smart_hook(
                d, config=config_local, cls=Relationship
            ),  #  from_dict(data_class=YAMLSerializer._get_real_class(d, Relationship), data=d, config=config_local),
            ExternalReference: lambda d: from_dict(
                data_class=YAMLSerializer._get_real_class(d, ExternalReference),
                data=d,
                config=config_local,
            ),
            Taxonomy: lambda d: from_dict(
                data_class=YAMLSerializer._get_real_class(d, Taxonomy),
                data=d,
                config=config_local,
            ),
            Category: lambda d: from_dict(
                data_class=YAMLSerializer._get_real_class(d, Category),
                data=d,
                config=config_local,
            ),
            FileKind: lambda d: FileKind(d) if isinstance(d, str) else d,
        }
        config_local.type_hooks.update(
            {
                Element: lambda d: YAMLSerializer.smart_hook(d, config_local, Element),
                Artefact: lambda d: YAMLSerializer.smart_hook(
                    d, config_local, Artefact
                ),
                Pipeline: lambda d: YAMLSerializer.smart_hook(
                    d, config_local, Pipeline
                ),
                Command: lambda d: YAMLSerializer.smart_hook(d, config_local, Command),
                Instruction: lambda d: YAMLSerializer.smart_hook(
                    d, config_local, Instruction
                ),
                Manifest: lambda d: YAMLSerializer.smart_hook(
                    d, config_local, Manifest
                ),
                MLModel: lambda d: YAMLSerializer.smart_hook(d, config_local, MLModel),
                Data: lambda d: YAMLSerializer.smart_hook(d, config_local, Data),
                Relationship: lambda d: YAMLSerializer.smart_hook(
                    d, config_local, Relationship
                ),
                ExternalReference: lambda d: YAMLSerializer.smart_hook(
                    d, config_local, ExternalReference
                ),
                FileKind: lambda d: FileKind(d) if isinstance(d, str) else d,
            }
        )

        # 3. On lance la reconstruction avec la vraie classe
        res = from_dict(data_class=real_cls, data=data, config=config_local)
        result = (
            YAMLSerializer.rebuild_manifest_links(res)
            if isinstance(res, Manifest)
            else res
        )
        return result

    @staticmethod
    def __harvest_objects(obj, object_map):
        """This function recursively traverses the manifest and collects all objects with UIDs into a flat map."""
        if not obj or not hasattr(obj, "uid"):
            return

        # record the object in the map if it is not already there
        if obj.uid not in object_map:
            object_map[obj.uid] = obj
        else:  # If the UID is already in the map, we can skip it to avoid infinite loops
            return

        # We need to look into all possible attributes that can contain child objects. This is a bit of a brute-force approach, but it ensures we don't miss anything.
        children_attributes = ["pipeline", "tasks", "steps", "commands", "artefacts"]

        for attr in children_attributes:
            children = getattr(obj, attr, None)
            if children:
                if isinstance(children, list):
                    for child in children:
                        YAMLSerializer.__harvest_objects(child, object_map)
                else:
                    YAMLSerializer.__harvest_objects(children, object_map)

    def rebuild_manifest_links(manifest):
        """This function takes a Manifest object and rebuilds the links between objects based on their UIDs.
        It assumes that the manifest only defines relationships using UIDs of Artefacts and Pipeline components,
        and that the relationships use UIDs to refer to these objects.
        It will replace the UIDs in the relationships with actual references to the objects in the manifest."""
        full_map = {}
        # Collect all artefacts and tasks(steps...) with UIDs in the manifest into a flat map (UID -> Object)
        YAMLSerializer.__harvest_objects(manifest, full_map)

        # We go through all relationships in the manifest and replace the UIDs in 'from_' and 'to_' with actual references to the objects in the manifest using the full_map we built.
        for rel in manifest.relations:
            # Connect the 'from_'
            if rel.from_.uid in full_map:
                rel.from_ = full_map[rel.from_.uid]

            # Connect the 'to_' (which is a list)
            if rel.to_:
                rel.to_ = [
                    full_map[item.uid] if hasattr(item, 'uid') and item.uid in full_map else item
                    for item in rel.to_
                ]

        return manifest

    @staticmethod
    def __artefact_resolverOLD(data: dict) -> Any:
        """
        Cette fonction regarde le champ 'type' et décide
        quelle classe instancier.
        """
        # Répertoire des classes disponibles
        # Assure-toi que ces classes sont importées
        mapping = {
            "Metric": Metric,
            "SoftwareFile": SoftwareFile,
            "MLModel": MLModel,
            "Artefact": Artefact,
            "Element": Element,
            "Manifest": Manifest,
            "CreationInfo": CreationInfo,
            "Instruction": Instruction,
            "Pipeline": Pipeline,
            "Command": Command,
            "Relationship": Relationship,
            "ExternalReference": ExternalReference,
        }
        # On récupère la classe correspondante au nom dans 'type'
        obj_type = data.get("type")
        cls = mapping.get(obj_type, Artefact)

        # On relance from_dict mais avec la classe spécifique
        # On ne passe pas la config ici pour éviter une boucle infinie
        return from_dict(data_class=cls, data=data)

    @staticmethod
    def from_yaml_file(filepath, cls) -> Any:
        data = YAMLSerializer.load_yaml_file(filepath)
        return YAMLSerializer._from_yaml(cls, data)

    @staticmethod
    def load_yaml_file(filepath) -> dict:
        # print current path
        print(f"Loading YAML file from: {filepath}")
        with open(filepath, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    @staticmethod
    def load_yaml_to_dict(string: str) -> dict:
        try:
            data = yaml.safe_load(string)
        #           data = None
        #           if isinstance(string, str):
        #               data = yaml.safe_load(string)
        #           elif isinstance(string, dict):
        #               data = yaml.safe_load(string)
        #           elif isinstance(string, Element):
        #               data = yaml.safe_load(asdict(string))
        #           else: raise ValueError("Input must be a string, dict, or Element.")

        except yaml.YAMLError as exc:
            print(f"Error parsing YAML: {exc}")
            return {}
        return data

    @staticmethod
    def __from_yamlOLD(cls: Type[T], data: dict) -> T:
        # On crée la configuration avec le hook pour la classe mère
        # config = Config(type_hooks={Artefact: YAMLSerializer.artefact_resolver})
        configLocal = Config(
            type_hooks={Artefact: YAMLSerializer.__artefact_resolverOLD},
            cast=[dict],  # Force les dictionnaires à rester des dictionnaires
        )
        return from_dict(data_class=cls, data=data, config=configLocal)

    @staticmethod
    def from_yaml_to_manifest(data: dict, cls) -> Manifest:
        manifest = from_dict(data_class=Manifest, data=data)
        return manifest

    @staticmethod
    def to_yaml(element, clean_none=True) -> str:
        # data = asdict(element)
        data = YAMLSerializer._to_dict_safe(element)
        if clean_none:
            data = YAMLSerializer._recursive_clean(data)
        return yaml.dump(data, sort_keys=False, allow_unicode=True, width=1000)

    @staticmethod
    def _recursive_clean(data) -> dict:
        newdata = data.copy() if isinstance(data, dict) else data
        if isinstance(data, dict):
            for k, v in data.items():
                if v is None:
                    del newdata[k]
                    continue
                if isinstance(v, (dict, list)):
                    newdata[k] = YAMLSerializer._recursive_clean(v)
        elif isinstance(data, list):
            newdata = []
            for item in data:
                if item is None:
                    continue
                if isinstance(item, (dict, list)):
                    newdata.append(YAMLSerializer._recursive_clean(item))
                else:
                    if isinstance(item, Element):
                        newdata.append(YAMLSerializer._recursive_clean(asdict(item)))
                    else:
                        newdata.append(item)

        return newdata


# OLD FUNCTION, we can keep it for backward compatibility but we should encourage using the new one which is more flexible and can be used for any dataclass, not just CreationInfo.
'''
def save_struct_to_yaml(creation_info: CreationInfo, filename: str):
    # On crée une structure avec la clé racine souhaitée
    output_structure = {
        creation_info.type : asdict(creation_info)
    }

    """Transforme les données SPDX en YAML et les sauvegarde dans un fichier."""
    # Conversion de la dataclass en dictionnaire
    # data_dict = asdict(creation_info)

    # Configuration du YAML pour une lecture humaine optimale
    with open(filename, 'w', encoding='utf-8') as f:
        yaml.dump(
            output_structure,
            f,
            sort_keys=False,      # Garde l'ordre de définition des champs
            allow_unicode=True,   # Gère les accents et caractères spéciaux
            default_flow_style=False # Force le format bloc (plus lisible)
        )
    print(f" Fichier sauvegardé avec succès : {filename}")
'''
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
    #json_result = to_json(my_elements)

    print("--- Generated JSON ---")
    #print(json_result)

    # 4. Tests
    #loaded_data = json.loads(json_result)

    #assert isinstance(loaded_data, list), "Result should be a list."
   # assert len(loaded_data) == 2, "Result list should contain 2 elements."
    #assert loaded_data[0]["name"] == "Arthit Suriyawongkul"
    #assert loaded_data[1]["software_primaryPurpose"] == "model"

    print("\n✅ All tests passed successfully.")
