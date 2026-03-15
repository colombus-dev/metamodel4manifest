from dataclasses import dataclass, field
from typing import Optional

from DSL4Pipelines.src.metamodel.core.structure import Element

@dataclass
class Category(Element):
    """Category represents a general concept or idea that can be used to classify
    or categorize elements in the DSL4Pipelines metamodel."""


@dataclass
class Taxonomy(Element):
    """Taxonomy represents a classification system for categorizing elements in the DSL4Pipelines metamodel.
    It can be used to define categories, tags, or labels that can be applied to elements such as artefacts, tasks, or relationships.
    The taxonomy can help organize and structure the elements in the model, making it easier to understand and navigate."""
    categories: dict[str, Category] = field(default_factory=dict)
    def add_category(self, category: Category):
        """Ajoute une catégorie au dictionnaire en utilisant son UID comme clé."""
        if not category.uid:
            raise ValueError(f"La catégorie {category.name} doit avoir un UID.")
        self.categories[category.uid] = category

    def get_category(self, uid: str) -> Category | None:
        """Récupère une catégorie par son UID (retourne None si absente)."""
        return self.categories.get(uid)


crispDM_categories: dict[str, Category] = {
    "step:data-acquisition": Category(
        uid="step:data-acquisition",
        name="Data Acquisition",
        description="Collect of data from various sources (databases, APIs, web scraping)."
    ),
    "step:data-preparation": Category(
        uid="step:data-preparation",
        name="Data Preparation",
        description="Cleaning, normalization, and splitting of data into training and test sets."
    ),
    "step:feature-engineering": Category(
        uid="step:feature-engineering",
        name="Feature Engineering",
        description="Transformation of raw data into features that better represent the underlying problem to the predictive models, resulting in improved model performance."
    ),
    "step:model-training": Category(
        uid="step:model-training",
        name="Model Training",
        description="Training of the machine learning model using the training dataset."
    ),
    "step:model-evaluation": Category(
        uid="step:model-evaluation",
        name="Model Evaluation",
        description="Evaluation of the model's performance using the test dataset and relevant metrics."
    ),
    "step:model-deployment": Category(
        uid="step:model-deployment",
        name="Model Deployment",
        description="Deployment of the trained model into a production environment for inference."
    ),
    "step:monitoring": Category(
        uid="step:monitoring",
        name="Monitoring & Observability",
        description="Monitoring of the model's performance and behavior in production, including detection of data drift, performance degradation, and other issues that may arise over time."
    ),
    "step:other": Category(
        uid="step:other",
        name="Other",
        description="Other steps that may be part of the machine learning lifecycle but are not covered by the main categories."
    )
}
cripDM_Taxonomy= Taxonomy(
    uid="taxo:ml-lifecycle",
    name="Machine Learning Lifecycle Steps",
    description="Classification standard for the main steps of the machine learning lifecycle, based on the CRISP-DM methodology.",
    categories= crispDM_categories
)

# --- Intégration dans ton moteur de recherche ---

# Supposons que full_map soit ton dictionnaire central
# On y ajoute la taxonomie elle-même ET chaque concept individuellement
