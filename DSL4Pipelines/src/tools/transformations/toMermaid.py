from enum import Enum
from typing import Any, List, Literal

from DSL4Pipelines.src.metamodel.artefacts.artefacts import Person, SoftwareFile
from DSL4Pipelines.src.metamodel.manifests.manifests import Manifest
from DSL4Pipelines.src.metamodel.pipelines.workflow import Pipeline
from DSL4Pipelines.src.metamodel.core.structure import Property
from DSL4Pipelines.src.metamodel.relations.relations import Relationship
from DSL4Pipelines.src.metamodel.catalogs.vocabulary import RelationshipType

# =====================================================================
# ---Mermaid generation functions---
# =====================================================================


class MERMAIDSerializer:
    # ----- CLASS ATTRIBUTES -----
    STYLE_4_PROCESS = "fill:#e1f5fe,stroke:#01579b,stroke-width:2px"
    STYLE_4_ARTEFACT = (
        "fill:#e0fff3,stroke:#e65100,stroke-width:1px,stroke-dasharray: 5 5"
    )
    STYLE_4_TAXONOMY = "fill:##ffe0fc,stroke:#ccc,stroke-width:1px,font-size:10pt"
    DIRECTION = "direction RL"
    ARTEFACTS = ["Artefact", "Data", "MLModel"]
    METRICS = [
        "Metric",
    ]
    # List of class names that should be styled as artefacts in the Mermaid diagram
    PROCESS = [
        "Pipeline",
        "Task",
        "Step",
        "Command",
        "Instruction",
    ]  # List of class names that should be styled as processes in the Mermaid diagram

    TAXONOMY = [
        "Category",
        "Taxonomy"
    ]  # List of class names that should be styled as taxonomy elements in the Mermaid diagram
    # --- MÉTHODE D'INITIALISATION ---
    def __init__(self):
        # --- VARIABLE D'INSTANCE ---
        # Chaque 'serializer' aura sa propre liste vide au départ
        self.stylelist: List[str] = []
        self.max_length = 30  # Longueur maximale pour l'affichage des valeurs dans le diagramme Mermaid, pour éviter de casser la mise en page avec des valeurs trop longues

    # this function will take an object and convert it to a Mermaid class diagram format,
    # following references to other objects and creating associations in the Mermaid diagram
    def object_to_mermaid_full(self, obj, name=None):
        lines = self._object_to_mermaid_full_rec(obj, name, visited=set())
        return (
            "\n classDiagram \n    "
            + MERMAIDSerializer.DIRECTION
            + "\n"
            + lines
            + "\n"
            + "\n".join(self.stylelist)
        )

    def _object_to_mermaid_full_rec(self, obj, name=None, visited=None):
        if visited is None:
            visited = set()

        obj_id = id(obj)
        if obj_id in visited:
            return ""
        visited.add(obj_id)

        # Build the node ID with the name if provided, otherwise with the class name and a unique identifier
        node_id = self.getMermaidId(name, obj, obj_id)
        if isinstance(obj, Relationship):
            return self.displayRelationship(node_id, obj, visited)
        return self.displayClass(node_id, obj, visited)

    def displayRelationship(self, node_id, obj, visited):
        lines = []
        associations = []
        from_id = self.getMermaidId(None, obj.from_, id(obj.from_))
        for to in obj.to_:
            to_id = self.getMermaidId(None, to, id(to))
            associations.append(
                f"{from_id} ..> {to_id}  : {obj.relationship_type.name}"
            )
            # Appel récursif pour générer les nœuds liés
            lines.append(self._object_to_mermaid_full_rec(obj.from_, None, visited))
            lines.append(self._object_to_mermaid_full_rec(to, None, visited))

        # On ajoute les flèches à la fin
        if associations:
            lines.append("\n".join(associations))

        return "\n".join(lines) + "\n"

    def displayClass(self, node_id: str | None | Any, obj, visited) -> str:
        lines = [f"class {node_id}{{"]
        self.generateStyle(node_id, obj)
        # lines = [f'class "{node_id }" {{']
        associations = []

        for key, value in obj.__dict__.items():
            self.attribute_to_mermaid(
                key, value, associations, lines, node_id, associations, visited
            )
        lines.append("}")

        # On ajoute les flèches à la fin
        if associations:
            lines.append("\n".join(associations))

        return "\n".join(lines) + "\n"

    def generateStyle(self, node_id: str | None | Any, obj):
        if obj.__class__.__name__ in MERMAIDSerializer.PROCESS:
            self.stylelist.append(
                f"style {node_id} {MERMAIDSerializer.STYLE_4_PROCESS}"
            )
        else:
            if obj.__class__.__name__ in MERMAIDSerializer.ARTEFACTS:
                self.stylelist.append(
                    f"style {node_id} {MERMAIDSerializer.STYLE_4_ARTEFACT}"
                )
            else:
                if obj.__class__.__name__ in MERMAIDSerializer.METRICS:
                    self.stylelist.append(
                        f"style {node_id} fill:#fff3e0,stroke:#e65100,stroke-width:1px,stroke-dasharray: 5 5"
                    )
                else:
                    if obj.__class__.__name__ in MERMAIDSerializer.TAXONOMY:
                        self.stylelist.append(
                            f"style {node_id} {MERMAIDSerializer.STYLE_4_TAXONOMY}"
                        )
                    else:
                        self.stylelist.append(
                            f"style {node_id} fill:#fafafa,stroke:#ccc,stroke-width:1px,font-size:10pt,font-style:italic"
                        )

    def getMermaidId(self, name, obj, obj_id: int) -> str | None | Any:
        instance_name = name or getattr(obj, "name", None) or f"inst_{obj_id}"
        instance_name = str(instance_name)
        # print(f"Generating Mermaid ID for object: {obj.__class__.__name__} with name: {instance_name}")
        instance_name = instance_name.replace(
            " ", "_"
        )  # On remplace les espaces par des underscores pour l'ID Mermaid
        instance_name = instance_name.replace(
            ".", "xx"
        )  # On remplace les points par des underscores pour l'ID Mermaid
        class_name = obj.__class__.__name__
        node_id = str(instance_name).replace(" ", "_")
        node_id = f"{node_id}__{class_name}"
        return node_id

    def attribute_to_mermaid(
        self, key, value, associations, lines, node_id, associations1, visited
    ):
        # no need to display None values
        if value is None:
            return

        if isinstance(value, Enum):
            # print(f"Value {value} is an Enum, displaying it directly in the class diagram")
            lines.append(f"    {key} : {value.name}")
            return

        if key == "properties":
            return self.dealWithProperties(key, lines, value)

        # Value is a simple attribute, we display it directly in the class diagram
        if not isinstance(value, list):
            if not hasattr(value, "__dict__"):
                value = str(value)
                if len(value) > self.max_length:
                    value = value[: self.max_length] + "..."
                value = sanitize_code_for_mermaid(value)
                lines.append(f"    {key} : {value}")
                return
            else:
                #  print(f"Value {value} is an object, creating an association and generating the target node")
                self.to_mermaid_association(
                    associations=associations,
                    target=value,
                    role=key,
                    origin_id=node_id,
                    lines=lines,
                    visited=visited,
                )
                return

        # If the value is a list of simple values, we display them as a comma-separated list
        if (
            isinstance(value, list)
            and len(value) > 0
            and not hasattr(value[0], "__dict__")
        ):
            lines.append(f"    {key} : {', '.join(str(v) for v in value)}")
            return
        # If the value is a list of objects, we create an association for each object in the list and call the function recursively to generate the target node
        if isinstance(value, list) and len(value) > 0 and hasattr(value[0], "__dict__"):
            for i, item in enumerate(value):
                if isinstance(item, Enum):
                    # print(f"Value {item} is an Enum, displaying it directly in the class diagram")
                    lines.append(f"    {key} : {item.name}")
                    continue
                else:
                    #   print(f"Value {item} is an object, creating an association and generating the target node")
                    self.to_mermaid_association(
                        associations=associations,
                        target=item,
                        role=key,
                        lines=lines,
                        origin_id=node_id,
                        visited=visited,
                    )
        return

    def dealWithProperties(self, key: Literal["properties"], lines, value):
        if isinstance(value, list) or isinstance(value, dict):
            if len(value) <= 0:
                return
            prop_items = []  # On utilise une liste temporaire pour stocker les morceaux
            if isinstance(value, list):
                # Si c'est une liste de propriétés, on les affiche toutes sur la même ligne, séparées"
                for prop in value:
                    if isinstance(prop, Property):
                        label = getattr(prop, "key", getattr(prop, "name", "unknown"))
                        val = getattr(prop, "value", "unknown")
                        if isinstance(val, Enum):
                            val = val.name
                        elif isinstance(val, str):
                            val = sanitize_code_for_mermaid(val)
                            # On tronque si c'est trop long
                            if len(val) > self.max_length:
                                val = val[: self.max_length] + "..."
                        prop_items.append(f"{label}: {val}")
                    elif isinstance(prop, dict):
                        for k, v in prop.items():
                            prop_items.append(f"{k}: {v}")
            elif isinstance(value, dict):
                for k, v in value.items():
                    prop_items.append(f"{k}: {v}")
            # On transforme la liste en une seule chaîne de caractères séparée par des " | "
            final_string = " \n\t\t ".join(prop_items)
            readyString = sanitize_code_for_mermaid(final_string)

        # On ajoute une seule ligne à ton diagramme Mermaid
        lines.append(f"    {key} : {readyString}")
        return

    # generate
    def to_mermaid_association(
        self,
        associations: list[Any],
        target,
        role: str,
        lines: list[str],
        origin_id: str,
        visited: set[Any] | Any,
    ):
        # on vérifie que la cible n'est pas une relation, sinon on risque d'avoir des associations qui pointent vers des nœuds "Relation" sans afficher les liens réels entre les objets
        target_id = self.getMermaidId(None, target, id(target))
        if not isinstance(target, Relationship):
            associations.append(f"{origin_id} --> {target_id}  : {role}")
        # Appel récursif pour générer le nœud cible
        lines.insert(0, self._object_to_mermaid_full_rec(target, None, visited))


# =======================================================================================

# This simple function will take an object and convert it to a Mermaid class diagram format
# It only viusalizes the direct attributes of the object, without following references to other objects (no associations)


def object_to_mermaid(obj, name=None):
    node_id = MERMAIDSerializer.getMermaidId(name, obj, id(obj))
    lines = [f"class {node_id} {{"]
    for key, value in obj.__dict__.items():
        # Ignore the end of the UID if it's too long for the schema
        display_value = str(value)[:50] + "..." if len(str(value)) > 50 else value
        display_value = sanitize_code_for_mermaid(display_value)
        lines.append(f"    {key}: {display_value}")
    lines.append("}")
    return "\n".join(lines)


# This function will sanitize the code for Mermaid by replacing special characters with their HTML entities,
# to avoid breaking the Mermaid syntax when displaying code snippets or other text that may contain characters like { }, ( ), " or '.
def sanitize_code_for_mermaid(text):
    if not text:
        return ""
    # converts the input to string if it's not already a string, to avoid errors when calling replace on non-string types
    t = str(text)

    replacements = {
        "{": "&#123;",  # Accolade ouvrante
        "}": "&#125;",  # Accolade fermante
        "(": "&#40;",  # Parenthèse ouvrante
        ")": "&#41;",  # Parenthèse fermante
        '"': "&quot;",  # Guillemet double
        "'": "&#39;",  # Guillemet simple
        "\n": "\\n",  # On remplace les sauts de ligne par des \n pour que ça s'affiche correctement dans Mermaid
    }

    for char, replacement in replacements.items():
        t = t.replace(char, replacement)

    return t


# @todo old functions should be re-implemented using the new recursive approach, to have a more consistent and powerful way to generate Mermaid diagrams


def to_simple_mermaid(manifest: Manifest) -> str:
    lines = ["graph TD"]
    lines.append(f"  subgraph Manifest: {manifest.name}")
    lines.append(f"    Pipeline: {manifest.pipeline.name}")
    for art in manifest.artefacts:
        lines.append(f"    Artefact: {art.name} ({art.__class__.__name__})")
    for rel in manifest.relations:
        from_name = getattr(rel.from_, "name", str(rel.from_))
        to_names = [getattr(to, "name", str(to)) for to in rel.to_]
        lines.append(
            f"    {from_name} -->|{rel.relationship_type}| {' ,'.join(to_names)}"
        )
    lines.append("  end")
    return "\n".join(lines)


# Not implemented yet, but the idea is to have a recursive function that can take any metadata structure and format it as a Mermaid-compatible string, handling nested dictionaries and lists appropriately.
# @Todo should : implement this function
def pipelineStructure_to_mermaid_as_graph(pipeline: Pipeline):
    lines = ["graph TD"]
    # Styles
    # Styles
    lines.append("  classDef process fill:#e1f5fe,stroke:#01579b,stroke-width:2px;")
    lines.append(
        "  classDef data fill:#fff3e0,stroke:#e65100,stroke-width:1px,stroke-dasharray: 5 5;"
    )
    lines.append(
        "  classDef meta fill:#fafafa,stroke:#ccc,stroke-width:1px,font-size:10pt,font-style:italic;"
    )
    lines.append(
        "  classDef metaProcess fill:##e8f4fa,stroke:#ccc,stroke-width:1px,font-size:10pt,font-style:italic;"
    )

    drawn_artifacts = set()

    for task in pipeline.tasks:
        # 1. Le Processus
        lines.append(f"  {task.name}[[{task.name}]]:::process")

        # 2. Ses properties (si présentes)
        if task.properties:
            meta_lines = format_meta_mermaid(
                task.metadata.get("metadata", task.metadata)
            )
            meta_text = "<br/>".join(meta_lines)
            meta_id = f"meta_{task.name}"
            lines.append(f'  {meta_id}["{meta_text}"]:::metaProcess')
            lines.append(f"  {task.name} --- {meta_id}")

        # 3. Gestion des artefacts (Inputs et Outputs)
        all_artifacts = task.inputs + task.outputs
        for art in all_artifacts:
            if art.name not in drawn_artifacts:
                # Dessiner l'artefact s'il n'est pas déjà présent
                if any(
                    word in art.type.lower() for word in data_types
                ):  # "data" in art.type.lower():
                    lines.append(f"  {art.name}[({art.name})]:::data")
                else:
                    lines.append(f"  {art.name}[/{art.name}/]:::data")

            if art.metadata:
                # On utilise notre nouvelle fonction récursive
                meta_lines = format_meta_mermaid(art.metadata)
                meta_text = "<br/>".join(meta_lines)

                meta_id = f"meta_{art.name}"
                # On utilise des guillemets pour protéger le HTML interne
                lines.append(f'  {meta_id}["{meta_text}"]:::meta')
                lines.append(f"  {art.name} --- {meta_id}")

                drawn_artifacts.add(art.name)

            # Liens
            if art in task.inputs:
                lines.append(f"  {art.name} -.-> {task.name}")
            else:
                lines.append(f"  {task.name} -.-> {art.name}")

        if task.next_step:
            lines.append(f"  {task.name} ==> {task.next_step}")

        lines.append("\n".join(transform_Step_Artifacts(task)))

    return "\n".join(lines)


# @Todo implement this function to improve the visualization of relationships between objects, by following the references to other objects and creating associations in the Mermaid diagram
# @Take-care it fails.
def styleHeader() -> str:
    # Définition des styles (CSS-like)
    # Dans un classDiagram, on sépare les styles par des espaces, pas des virgules
    styles = [
        "    classDef relationship fill:#f9f stroke:#333 stroke-width:2px color:#000",
        "    classDef data fill:#bbf stroke:#333 stroke-width:2px color:#000",
        "    classDef instruction fill:#dfd stroke:#333 stroke-dasharray:5 5",
    ]
    return "\n".join(styles)


# -----------------------------


"""def association_to_mermaid(value, key, header, lines, visited):
    for i, item in enumerate(value):
        target_name = getattr(item, 'name', f"{key}_{i}")
    target_id = str(target_name).replace(" ", "_")
    associations.append(f'"{header}" --> "{target_id} : {item.__class__.__name__}" : {key}')
    # Appel récursif pour générer le nœud cible
    lines.insert(0, _object_to_mermaid_full_rec(item, target_name, visited))
"""

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
    # print(object_to_mermaid(pers, "archit"))

    fichier = SoftwareFile(
        uid="https://spdx.org/spdxdocs/File10-model",
        creation_info=creInfo,
        name="model.bin",
        software_file_kind="file",
        software_primary_purpose="model",
    )
   # print(object_to_mermaid(fichier))

    relation = Relationship(
        from_=pers, to_=[fichier], relationship_type=RelationshipType.USES
    )
    #print(object_to_mermaid_full(relation, "relation_pers_fichier"))
