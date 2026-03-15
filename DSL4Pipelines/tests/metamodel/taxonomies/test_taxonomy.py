from DSL4Pipelines.src.metamodel.taxonomies.taxonomy import cripDM_Taxonomy, Category
from DSL4Pipelines.src.metamodel.pipelines.workflow import Task
from DSL4Pipelines.src.metamodel.relations.relations import Relationship
from DSL4Pipelines.src.metamodel.core.structure import Element


def test_taxonomy():
    categories_keys:list = list(cripDM_Taxonomy.categories.keys())
    print("\nCategories in the taxonomy:", categories_keys)
    assert len(categories_keys) == 8, f"Expected 8 categories in the taxonomy, but got {len(categories_keys)}"


def test_taxonomy_as_target_of_relationships():
    task1:Task = Task()
    cat = cripDM_Taxonomy.get_category("step:data-preparation")
    assert cat is not None, "The category 'step:data-preparation' should be present in the taxonomy."
    assert isinstance(cat, Category), "The retrieved value should be an instance of Category."
    assert isinstance(cat, Element), "The retrieved value should also be an instance of Element, since Category inherits from Element."
    assert isinstance(cripDM_Taxonomy, Element), "The taxonomy itself should be an instance of Element"
    relation : Relationship = Relationship(
        from_=task1,
        to_=[
            cat,
            cripDM_Taxonomy]
    )





