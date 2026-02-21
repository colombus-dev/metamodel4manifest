"""Definition of the Metric class, which represents a performance, energy,
or environmental metric associated with a component in the pipeline.
This class includes fields for the type of metric, its value, unit, and an optional slice to specify the context
(e.g., idle vs peak-load).
It also includes a method to validate the metric against a predefined catalog of metrics (MetricCatalog)
and to automatically fill in the category based on the kind of metric if it matches a known metric in the catalog."""

from dataclasses import dataclass
from typing import Optional, List

from DSL4Pipelines.src.metamodel.artefacts.artefacts import Artefact
from DSL4Pipelines.src.metamodel.catalogs.MetricCatalog import MetricCatalog
from DSL4Pipelines.src.metamodel.pipelines.workflow import Task
from DSL4Pipelines.src.metamodel.relations.relations import Relationship
from DSL4Pipelines.src.metamodel.catalogs.vocabulary import RelationshipType
from DSL4Pipelines.src.metamodel.artefacts.ml_artefacts import Data
from DSL4Pipelines.src.metamodel.artefacts.artefacts import SoftwareFile


# Defines metric related to performance, energy usage, or environmental impact of a component in the pipeline.
# @check it true, CycloneDX inspires this definition, but we keep it simple for now. We can later enrich it with more specific fields (e.g., for performance metrics: latency, throughput; for energy metrics: energy consumption, carbon footprint; etc.)
@dataclass
class Metric(Artefact):
    """Represents a performance, energy, or environmental metric associated with a component in the pipeline."""

    type: str = "Metric"  # To distinguish from other types of artefacts
    kind: Optional[str] = None  # ex:MetricCatalog.Performance.ACCURACY
    value: Optional[str] = None  # ex: "0.45", "150", "2.3"
    unit: Optional[str] = None  # ex: "MB", "kWh", "kgCO2e"
    slice: Optional[str] = None  # ex:  "idle", "peak-load"
    category: Optional[str] = (
        None  # ex: "PERFORMANCE" (manually or automatically filled based on the kind if it matches a known metric in the catalog)
    )

    def validate_with_catalog(self) -> bool:
        """
        Check if the 'kind' exists in the MetricCatalog.
        if yes, it also fills the 'category' if it's empty.
        """
        if not self.kind:
            return False

        # We try to find the category for the given kind in the catalog. If we find it, we fill the category field and return True. Otherwise, we return False.
        found_cat = MetricCatalog.find_category_for_metric(self.kind)

        if found_cat != "UNKNOWN":
            self.category = found_cat
            # Optionnel : on nettoie le kind pour enlever le préfixe si présent
            #       if ":" in self.kind:
            #           self.kind = self.kind.split(":")[-1]
            return True

        return False


# todo: @remove d'ici c'est pas du tout à sa place....
def find_origin(metric: Metric, rels: List[Relationship]) -> str:
    """This function takes a metric and a list of relationships, and checks if the metric is the 'from' element of any relationship of type 'EVALUATES'.
    If it finds such a relationship, it returns a string indicating which task is being evaluated by the metric.
    Otherwise, it returns 'Origine inconnue'."""
    for r in rels:
        test = metric == r.from_
        print(
            f"Checking relationship: from {r.from_.uid} of type {r.relationship_type} : {test}"
        )
        if r.from_ == metric and r.relationship_type == RelationshipType.EVALUATES:
            string = f"-- The metric {metric.uid} evaluates the following task {r.to_[0].uid} --"
            return f" {string} : {test} "
    return "Origine inconnue"


# Dans JSON CycloneDX, cela sera stocké sous :
# performanceMetric
# qui est plus riche que cette version simplifiée
# A La SPDX, on va utiliser les metrics pour faire le lien entre les éléments du pipeline
# et les éléments de la SBOM, en indiquant par exemple que tel composant du pipeline a telle empreinte carbone ou tel coût énergétique.


# --- Exemple de construction du graphe ---
# =====================================================================
# ---Test bloc and usage example---
# =====================================================================


def test_other():
    print("------------ 1. Defining Elements and Relationships")
    script = SoftwareFile(
        "spdx:script-01", "eval_energy.py", "print('measuring...')", "python"
    )
    my_code = SoftwareFile(
        uid="spdx:eval-script", name="accuracy_check.py", creation_info="now"
    )
    dataset = Data(
        uid="spdx:val-set",
        name="ImageNet-Subset",
        data_types=["images"],
        creation_info="now",
    )
    print("------------ 2. Creating a Task that uses both the code and the dataset")
    benchmark_task = Task(uid="task-01", description="Benchmark de Précision Q1")
    res_metric = Metric("spdx:metric-01", "Power Usage", "0.45", "kWh")
    relationships = [
        Relationship(
            uid="rel1",
            from_=benchmark_task,
            to_=[my_code, script],
            relationship_type=RelationshipType.DEPENDS_ON,
        ),
        Relationship(
            "rel2",
            from_=benchmark_task,
            to_=[dataset],
            relationship_type=RelationshipType.TESTED_ON,
        ),
        Relationship(
            "rel3",
            from_=res_metric,
            to_=[benchmark_task],
            relationship_type=RelationshipType.EVALUATES,
        ),
    ]
    res = find_origin(res_metric, relationships)
    print(f"ORIGIN = {res}")
    assert (
        res
        == " -- The metric spdx:metric-01 evaluates the following task task-01 -- : True "
    ), "Test failed: Origin not found correctly"


if __name__ == "__main__":
    # 1. Création brute (on ne connaît pas encore la catégorie)
    m = Metric(kind="perf:accuracy", value="0.98")

    # 2. Validation et enrichissement
    if m.validate_with_catalog():
        print(f"Métrique valide ! Catégorie détectée : {m.category}")
    else:
        print("Attention : cette métrique n'est pas répertoriée dans le catalogue.")

    # Maintenant m.kind vaut "accuracy" et m.category vaut "PERFORMANCE"
    test_other()
